"""
Quantum Channel Simulation
Simulates the transmission of polarized single photons over a quantum channel,
including optional channel noise (depolarizing / Pauli channel errors).
"""

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister


class QuantumChannel:
    """
    Simulates a quantum communication channel between Alice and Bob.
    Supports ideal lossless transmission or physical depolarizing channel noise.
    """
    def __init__(self, enable_noise: bool = False, noise_probability: float = 0.02):
        self.enable_noise = enable_noise
        self.noise_probability = max(0.0, min(1.0, noise_probability))

    def apply_channel_noise(
        self,
        circuit: QuantumCircuit,
        qubit: QuantumRegister,
        rng: np.random.Generator
    ) -> str:
        """
        Apply channel noise to a qubit line.
        If noise occurs, randomly applies Pauli X (bit-flip), Pauli Z (phase-flip),
        or Pauli Y (both bit and phase flip).
        
        Returns the type of noise applied: 'NONE', 'BIT_FLIP_X', 'PHASE_FLIP_Z', 'BIT_PHASE_FLIP_Y'.
        """
        if not self.enable_noise or self.noise_probability <= 0.0:
            return "NONE"

        if rng.random() < self.noise_probability:
            # Depolarizing channel: 1/3 X, 1/3 Y, 1/3 Z
            noise_type = rng.choice(["X", "Y", "Z"])
            if noise_type == "X":
                circuit.x(qubit)
                return "BIT_FLIP_X"
            elif noise_type == "Y":
                circuit.y(qubit)
                return "BIT_PHASE_FLIP_Y"
            elif noise_type == "Z":
                circuit.z(qubit)
                return "PHASE_FLIP_Z"

        return "NONE"
