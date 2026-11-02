"""
FastAPI REST API Routes for QuantumShield BB84 Simulator
"""

import time
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import Response

from ..models.schemas import (
    SimulationConfig,
    SimulationResponse,
    HealthResponse,
    TimelineEvent,
)
from ..services.simulation_service import simulation_service
from ..core.backend_loader import get_backend_info

router = APIRouter()
START_TIME = time.time()


@router.get("/health", response_model=HealthResponse)
def get_health():
    """Returns backend and quantum simulator availability status."""
    info = get_backend_info()
    sim_count = len(simulation_service.list_simulations())
    uptime = time.time() - START_TIME
    return HealthResponse(
        status="healthy",
        backend="FastAPI + Qiskit",
        simulator=info["simulator_name"],
        qiskit_version=info["qiskit_version"],
        qiskit_aer_version=info.get("qiskit_aer_version"),
        active_simulations=sim_count,
        uptime_seconds=round(uptime, 2)
    )


@router.post("/simulation/start", response_model=SimulationResponse)
def start_simulation(config: SimulationConfig):
    """Start a BB84 QKD simulation with validated configuration parameters."""
    try:
        response = simulation_service.run_simulation_sync(config)
        return response
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(exc)}")


@router.get("/simulation/{simulation_id}", response_model=SimulationResponse)
def get_simulation(simulation_id: str):
    """Return the latest metrics and results for a simulation."""
    sim = simulation_service.get_simulation(simulation_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return sim.to_response()


@router.post("/simulation/{simulation_id}/stop")
def stop_simulation(simulation_id: str):
    """Stop an active simulation safely."""
    success = simulation_service.stop_simulation(simulation_id)
    if not success:
        raise HTTPException(status_code=400, detail="Simulation not running or not found")
    return {"status": "stopped", "simulation_id": simulation_id}


@router.post("/simulation/{simulation_id}/reset")
def reset_simulation(simulation_id: str):
    """Reset the simulation state."""
    success = simulation_service.reset_simulation(simulation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return {"status": "reset", "simulation_id": simulation_id}


@router.get("/simulation/{simulation_id}/history", response_model=List[TimelineEvent])
def get_simulation_history(simulation_id: str):
    """Return the recorded metrics and alert timeline for a simulation."""
    sim = simulation_service.get_simulation(simulation_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return simulation_service.get_history(simulation_id)


@router.get("/simulation/{simulation_id}/export")
def export_simulation(simulation_id: str, format: str = Query(default="json", pattern="^(json|csv)$")):
    """Export simulation results in CSV or JSON format."""
    try:
        content, media_type, filename = simulation_service.export_data(simulation_id, format)
        return Response(
            content=content,
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(exc)}")


@router.get("/simulations", response_model=List[SimulationResponse])
def list_simulations():
    """List all executed simulations."""
    return simulation_service.list_simulations()
