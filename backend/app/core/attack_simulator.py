"""
Eve Eavesdropping Attack Simulation (Intercept-Resend)
Simulates an active quantum eavesdropper performing intercept-resend attacks
on transmitted qubits using Qiskit quantum circuits.
"""

from typing import List, Optional, Tuple
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister


class EveAttacker:
    """
    Simulates Eve performing an intercept-resend attack.
    Supports no attack, partial attack (0% - 100%), and full intercept-resend.
    """
    def __init__(self, enable_eve: bool = False, interception_probability: float = 1.0):
        self.enable_eve = enable_eve
        self.interception_probability = max(0.0, min(1.0, interception_probability)) if enable_eve else 0.0

    def should_intercept(self, rng: np.random.Generator) -> bool:
        """Determines if Eve intercepts a specific qubit based on probability."""
        if not self.enable_eve or self.interception_probability <= 0.0:
            return False
        return bool(rng.random() < self.interception_probability)

    def generate_interceptions_and_bases(
        self,
        num_qubits: int,
        rng: np.random.Generator
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate boolean mask of intercepted qubits and independent random measurement bases.
        0: Rectilinear (+), 1: Diagonal (x)
        """
        if not self.enable_eve or self.interception_probability <= 0.0:
            intercepts = np.zeros(num_qubits, dtype=bool)
            bases = np.zeros(num_qubits, dtype=int)
            return intercepts, bases

        intercepts = rng.random(num_qubits) < self.interception_probability
        bases = rng.integers(0, 2, num_qubits)
        return intercepts, bases

    def apply_intercept_resend(
        self,
        circuit: QuantumCircuit,
        qubit: QuantumRegister,
        eve_cbit: ClassicalRegister,
        eve_basis: int
    ):
        """
        Applies Eve's intercept and resend operations in-circuit:
        1. Eve rotates into her chosen basis (Hadamard if diagonal).
        2. Eve measures the qubit into her classical register.
        3. Eve resets the qubit.
        4. Eve prepares a replacement state matching her outcome and chosen basis:
           - Outcome 0, Basis + -> |0>
           - Outcome 1, Basis + -> |1>
           - Outcome 0, Basis x -> |+>
           - Outcome 1, Basis x -> |->
        5. Eve sends the replacement qubit forward to Bob.
        """
        # Step 1: Rotate to measurement basis
        if eve_basis == 1:  # Diagonal basis
            circuit.h(qubit)

        # Step 2: Measure into Eve's classical bit
        circuit.measure(qubit, eve_cbit)

        # Step 3: Reset quantum state
        circuit.reset(qubit)

        # Step 4: Conditionally apply X if measured bit was 1
        with circuit.if_test((eve_cbit, 1)):
            circuit.x(qubit)

        # Step 5: Rotate back to diagonal basis if Eve's basis was diagonal
        if eve_basis == 1:
            circuit.h(qubit)
