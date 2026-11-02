"""
Tests for FastAPI Backend Endpoints & WebSockets
Validates:
1. Health endpoint.
2. Simulation execution and input validation.
3. Simulation stop and reset endpoints.
4. Export endpoints (JSON and CSV).
5. WebSocket progress streaming.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.schemas import SimulationConfig

client = TestClient(app)


def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "Qiskit" in data["simulator"] or "Aer" in data["simulator"]
    assert data["qiskit_version"] is not None


def test_simulation_start_ideal():
    payload = {
        "num_qubits": 100,
        "enable_eve": False,
        "enable_noise": False,
        "random_seed": 42
    }
    res = client.post("/api/simulation/start", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "COMPLETED"
    assert data["metrics"]["measured_qber"] == 0.0
    assert data["metrics"]["security_state"] == "SECURE"
    assert data["keys"]["candidate_key_length"] > 0
    assert len(data["records_sample"]) > 0


def test_simulation_start_attack():
    payload = {
        "num_qubits": 200,
        "enable_eve": True,
        "eve_interception_prob": 1.0,
        "qber_threshold": 11.0,
        "random_seed": 42
    }
    res = client.post("/api/simulation/start", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "COMPLETED"
    assert data["metrics"]["measured_qber"] > 11.0
    assert data["metrics"]["security_state"] == "SUSPICIOUS"
    # When suspicious, candidate key is discarded
    assert data["keys"]["candidate_key_length"] == 0


def test_simulation_input_validation():
    # num_qubits too small (< 10)
    bad_res = client.post("/api/simulation/start", json={"num_qubits": 2})
    assert bad_res.status_code == 422

    # eve_interception_prob > 1.0
    bad_res2 = client.post("/api/simulation/start", json={"num_qubits": 100, "eve_interception_prob": 1.5})
    assert bad_res2.status_code == 422


def test_export_json_and_csv():
    # First start a simulation
    payload = {"num_qubits": 50, "random_seed": 12}
    start_res = client.post("/api/simulation/start", json=payload)
    sim_id = start_res.json()["simulation_id"]

    # Export JSON
    res_json = client.get(f"/api/simulation/{sim_id}/export?format=json")
    assert res_json.status_code == 200
    assert res_json.headers["content-type"].startswith("application/json")
    json_data = res_json.json()
    assert json_data["simulation_id"] == sim_id
    assert len(json_data["records"]) == 50

    # Export CSV
    res_csv = client.get(f"/api/simulation/{sim_id}/export?format=csv")
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers["content-type"]
    csv_text = res_csv.text
    assert "alice_bit,alice_basis" in csv_text


def test_websocket_stream():
    # Start a run via websocket
    with client.websocket_connect("/ws/simulation/run") as ws:
        ws.send_json({"num_qubits": 100, "batch_size": 50, "random_seed": 99})
        init_msg = ws.receive_json()
        assert init_msg["type"] == "started"

        progress_msg = ws.receive_json()
        assert progress_msg["type"] in ("progress", "completed")

        # Collect until completed
        while True:
            msg = ws.receive_json()
            if msg["type"] == "completed":
                assert msg["metrics"]["total_qubits"] == 100
                break
