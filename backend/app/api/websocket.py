"""
WebSocket Handler for Real-Time Simulation Streaming
Streams progress, intermediate QBER metrics, and alerts to connected dashboards/mobile apps.
"""

import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..services.simulation_service import simulation_service
from ..models.schemas import SimulationConfig

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/simulation/run")
async def websocket_simulation_run(websocket: WebSocket):
    """
    Allows a client to submit a JSON config message, and the server creates and streams the simulation.
    Must be defined before /ws/simulation/{simulation_id} to avoid path shadowing.
    """
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        config_dict = json.loads(data)
        config = SimulationConfig(**config_dict)
        sim = simulation_service.create_simulation(config)
        
        await websocket.send_json({
            "type": "started",
            "simulation_id": sim.simulation_id,
            "config": config.model_dump()
        })

        async for update in simulation_service.run_simulation_stream(sim.simulation_id):
            await websocket.send_json(update)

    except WebSocketDisconnect:
        logger.info("Client disconnected from /ws/simulation/run")
    except Exception as exc:
        logger.error(f"WebSocket run error: {exc}")
        try:
            await websocket.send_json({"type": "error", "message": str(exc)})
            await websocket.close()
        except Exception:
            pass


@router.websocket("/ws/simulation/{simulation_id}")
async def websocket_simulation_stream(websocket: WebSocket, simulation_id: str):
    """
    WebSocket endpoint that streams simulation progress and metrics in real-time.
    Client can connect, and the server runs the simulation streaming batches.
    """
    await websocket.accept()
    logger.info(f"WebSocket client connected for simulation: {simulation_id}")

    try:
        # Check if simulation exists; if not, create default
        sim = simulation_service.get_simulation(simulation_id)
        if not sim:
            sim = simulation_service.create_simulation(SimulationConfig())
            simulation_id = sim.simulation_id

        async for update in simulation_service.run_simulation_stream(simulation_id):
            await websocket.send_json(update)

    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected for simulation: {simulation_id}")
        simulation_service.stop_simulation(simulation_id)
    except Exception as exc:
        logger.error(f"WebSocket error for simulation {simulation_id}: {exc}")
        try:
            await websocket.send_json({"type": "error", "message": str(exc)})
            await websocket.close()
        except Exception:
            pass
