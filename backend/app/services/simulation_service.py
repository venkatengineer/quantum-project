"""
Simulation Service
Manages simulation lifecycles, execution, history, and exports.
"""

import io
import csv
import json
import uuid
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, AsyncGenerator

from ..models.schemas import (
    SimulationConfig,
    SimulationResponse,
    SimulationStatus,
    SimulationMetrics,
    KeyDisplay,
    QubitTransmissionRecord,
    TimelineEvent,
    SecurityState,
)
from ..core.bb84 import BB84SimulationEngine
from ..core.security_monitor import SecurityMonitor
from ..core.qber import calculate_qber


class SimulationInstance:
    """Holds active and completed simulation data."""
    def __init__(self, simulation_id: str, config: SimulationConfig):
        self.simulation_id = simulation_id
        self.config = config
        self.status = SimulationStatus.PENDING
        self.metrics: Optional[SimulationMetrics] = None
        self.keys: Optional[KeyDisplay] = None
        self.records: List[QubitTransmissionRecord] = []
        self.monitor = SecurityMonitor(threshold=config.qber_threshold)
        self.error_message: Optional[str] = None
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.completed_at: Optional[str] = None
        self.stop_requested = False

    def to_response(self, sample_limit: int = 50) -> SimulationResponse:
        return SimulationResponse(
            simulation_id=self.simulation_id,
            status=self.status,
            config=self.config,
            metrics=self.metrics,
            keys=self.keys,
            records_sample=self.records[:sample_limit] if self.records else None,
            error_message=self.error_message,
            created_at=self.created_at,
            completed_at=self.completed_at
        )


class SimulationService:
    def __init__(self):
        self._simulations: Dict[str, SimulationInstance] = {}
        self._lock = asyncio.Lock()

    def create_simulation(self, config: SimulationConfig) -> SimulationInstance:
        sim_id = str(uuid.uuid4())
        sim = SimulationInstance(simulation_id=sim_id, config=config)
        self._simulations[sim_id] = sim
        return sim

    def get_simulation(self, simulation_id: str) -> Optional[SimulationInstance]:
        return self._simulations.get(simulation_id)

    def list_simulations(self) -> List[SimulationResponse]:
        return [sim.to_response() for sim in self._simulations.values()]

    def stop_simulation(self, simulation_id: str) -> bool:
        sim = self._simulations.get(simulation_id)
        if sim and sim.status in (SimulationStatus.RUNNING, SimulationStatus.PENDING):
            sim.stop_requested = True
            sim.status = SimulationStatus.STOPPED
            sim.completed_at = datetime.now(timezone.utc).isoformat()
            return True
        return False

    def reset_simulation(self, simulation_id: str) -> bool:
        sim = self._simulations.get(simulation_id)
        if sim:
            sim.status = SimulationStatus.PENDING
            sim.metrics = None
            sim.keys = None
            sim.records.clear()
            sim.monitor.reset()
            sim.error_message = None
            sim.stop_requested = False
            sim.completed_at = None
            return True
        return False

    def get_history(self, simulation_id: str) -> List[TimelineEvent]:
        sim = self._simulations.get(simulation_id)
        if not sim:
            return []
        return sim.monitor.get_timeline()

    def run_simulation_sync(self, config: SimulationConfig) -> SimulationResponse:
        """Runs the simulation synchronously to completion."""
        sim = self.create_simulation(config)
        sim.status = SimulationStatus.RUNNING
        try:
            engine = BB84SimulationEngine(config)
            metrics, keys, records = engine.run_full_simulation()
            sim.metrics = metrics
            sim.keys = keys
            sim.records = records
            sim.status = SimulationStatus.COMPLETED
            sim.completed_at = datetime.now(timezone.utc).isoformat()

            # Record final summary event
            sim.monitor.record_batch(
                simulation_id=sim.simulation_id,
                batch_index=1,
                qubits_processed=config.num_qubits,
                total_qubits=config.num_qubits,
                current_qber=metrics.measured_qber,
                sample_size=metrics.parameter_sample_length
            )
        except Exception as e:
            sim.status = SimulationStatus.FAILED
            sim.error_message = str(e)
            sim.completed_at = datetime.now(timezone.utc).isoformat()
            raise

        return sim.to_response()

    async def run_simulation_stream(
        self,
        simulation_id: str
    ) -> AsyncGenerator[Dict, None]:
        """
        Executes BB84 in batches, yielding real-time progress, metrics, and alerts
        for WebSocket consumers.
        """
        sim = self._simulations.get(simulation_id)
        if not sim:
            yield {"type": "error", "message": "Simulation not found"}
            return

        sim.status = SimulationStatus.RUNNING
        config = sim.config
        engine = BB84SimulationEngine(config)
        num_qubits = config.num_qubits
        batch_size = min(config.batch_size, num_qubits)
        
        processed = 0
        batch_index = 0
        all_raw_records = []

        try:
            while processed < num_qubits and not sim.stop_requested:
                batch_index += 1
                current_batch = min(batch_size, num_qubits - processed)
                batch_records = engine.run_batch(current_batch, start_index=processed)
                all_raw_records.extend(batch_records)
                processed += current_batch

                # Intermediate sifted calculation for live monitoring
                intermediate_sifted = [r for r in all_raw_records if r["basis_matched"]]
                inter_sifted_count = len(intermediate_sifted)
                inter_errors = sum(1 for r in intermediate_sifted if r["alice_bit"] != r["bob_measured"])
                inter_qber = calculate_qber(inter_errors, inter_sifted_count)

                # Record event in timeline
                event = sim.monitor.record_batch(
                    simulation_id=sim.simulation_id,
                    batch_index=batch_index,
                    qubits_processed=processed,
                    total_qubits=num_qubits,
                    current_qber=inter_qber,
                    sample_size=inter_sifted_count
                )

                yield {
                    "type": "progress",
                    "simulation_id": sim.simulation_id,
                    "batch_index": batch_index,
                    "qubits_processed": processed,
                    "total_qubits": num_qubits,
                    "progress_percentage": round((processed / num_qubits) * 100, 1),
                    "current_qber": round(inter_qber, 2),
                    "sifted_count": inter_sifted_count,
                    "sifted_errors": inter_errors,
                    "security_state": event.security_state.value,
                    "alert": event.alert,
                    "message": event.message
                }

                await asyncio.sleep(0.01)

            if sim.stop_requested:
                sim.status = SimulationStatus.STOPPED
                yield {"type": "stopped", "simulation_id": sim.simulation_id}
                return

            # Perform full reconciliation and parameter estimation
            metrics, keys, records = engine.run_full_simulation()
            sim.metrics = metrics
            sim.keys = keys
            sim.records = records
            sim.status = SimulationStatus.COMPLETED
            sim.completed_at = datetime.now(timezone.utc).isoformat()

            yield {
                "type": "completed",
                "simulation_id": sim.simulation_id,
                "metrics": metrics.model_dump(),
                "keys": keys.model_dump(),
                "records_sample": [r.model_dump() for r in records[:50]]
            }

        except Exception as exc:
            sim.status = SimulationStatus.FAILED
            sim.error_message = str(exc)
            yield {"type": "failed", "simulation_id": sim.simulation_id, "error": str(exc)}

    def export_data(self, simulation_id: str, format_type: str = "json") -> Tuple[str, str, str]:
        """
        Export simulation results as JSON or CSV.
        Returns (content, mime_type, filename).
        """
        sim = self._simulations.get(simulation_id)
        if not sim:
            raise ValueError(f"Simulation {simulation_id} not found")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if format_type.lower() == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow([
                "index", "alice_bit", "alice_basis", "alice_state",
                "eve_intercepted", "eve_basis", "eve_measured", "eve_resent_state",
                "bob_basis", "bob_measured", "basis_matched", "sifted_match",
                "in_parameter_estimation", "in_candidate_key"
            ])
            for r in sim.records:
                writer.writerow([
                    r.index, r.alice_bit, r.alice_basis, r.alice_state,
                    r.eve_intercepted, r.eve_basis or "", r.eve_measured if r.eve_measured is not None else "",
                    r.eve_resent_state or "", r.bob_basis, r.bob_measured,
                    r.basis_matched, r.sifted_match if r.sifted_match is not None else "",
                    r.in_parameter_estimation, r.in_candidate_key
                ])
            content = output.getvalue()
            return content, "text/csv", f"qkd_simulation_{simulation_id}_{timestamp}.csv"
        else:
            export_dict = {
                "simulation_id": sim.simulation_id,
                "status": sim.status.value,
                "config": sim.config.model_dump(),
                "metrics": sim.metrics.model_dump() if sim.metrics else None,
                "keys": sim.keys.model_dump() if sim.keys else None,
                "records_count": len(sim.records),
                "records": [r.model_dump() for r in sim.records]
            }
            content = json.dumps(export_dict, indent=2)
            return content, "application/json", f"qkd_simulation_{simulation_id}_{timestamp}.json"


# Global singleton service
simulation_service = SimulationService()
