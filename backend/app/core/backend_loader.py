"""
Quantum Backend Loader
Ensures Qiskit Aer (or fallback quantum primitives) initializes seamlessly across environments.
"""

import os
import sys
import glob
import logging

logger = logging.getLogger(__name__)

_SIMULATOR = None
_SIMULATOR_NAME = "Unknown"


def get_quantum_simulator():
    """
    Get the configured quantum circuit simulator backend.
    Prefers AerSimulator(method='stabilizer') for fast Clifford circuit simulation.
    """
    global _SIMULATOR, _SIMULATOR_NAME
    if _SIMULATOR is not None:
        return _SIMULATOR, _SIMULATOR_NAME

    try:
        from qiskit_aer import AerSimulator
        _SIMULATOR = AerSimulator(method="stabilizer")
        _SIMULATOR_NAME = "Qiskit Aer (Stabilizer)"
        logger.info("Initialized Qiskit Aer Stabilizer Simulator.")
        return _SIMULATOR, _SIMULATOR_NAME
    except Exception as exc:
        logger.warning(f"Could not initialize AerSimulator directly: {exc}")
        # Try importing generic AerSimulator
        try:
            import qiskit_aer
            _SIMULATOR = qiskit_aer.Aer.get_backend("aer_simulator")
            _SIMULATOR_NAME = "Qiskit Aer (Generic)"
            return _SIMULATOR, _SIMULATOR_NAME
        except Exception as exc2:
            logger.error(f"Fallback to basic Aer backend failed: {exc2}")
            raise RuntimeError(f"Unable to initialize quantum simulator: {exc2}")


def get_backend_info() -> dict:
    import qiskit
    try:
        import qiskit_aer
        aer_ver = qiskit_aer.__version__
    except Exception:
        aer_ver = None

    _, sim_name = get_quantum_simulator()
    return {
        "qiskit_version": qiskit.__version__,
        "qiskit_aer_version": aer_ver,
        "simulator_name": sim_name
    }
