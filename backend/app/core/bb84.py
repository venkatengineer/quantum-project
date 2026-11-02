"""
BB84 Quantum Key Distribution Protocol Engine
Implements authentic quantum state preparation, transmission, measurement,
basis reconciliation, parameter estimation, and candidate key generation using Qiskit.
"""

import time
import hashlib
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

from .backend_loader import get_quantum_simulator
from .attack_simulator import EveAttacker
from .quantum_channel import QuantumChannel
from .qber import calculate_qber, wilson_score_interval, theoretical_expected_qber
from .security_monitor import evaluate_security_state
from ..models.schemas import (
    SimulationConfig,
    SimulationMetrics,
    QubitTransmissionRecord,
    KeyDisplay,
    SecurityState,
    Basis,
)


def state_label(bit: int, basis: int) -> str:
    """Returns the Dirac notation for the BB84 state."""
    if basis == 0:  # Rectilinear (+)
        return "|0⟩" if bit == 0 else "|1⟩"
    else:           # Diagonal (x)
        return "|+⟩" if bit == 0 else "|−⟩"


class BB84SimulationEngine:
    """
    Simulates the end-to-end BB84 protocol using Qiskit quantum circuits.
    """
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.rng = np.random.default_rng(config.random_seed)
        self.attacker = EveAttacker(
            enable_eve=config.enable_eve,
            interception_probability=config.eve_interception_prob
        )
        self.channel = QuantumChannel(
            enable_noise=config.enable_noise,
            noise_probability=config.noise_probability
        )
        self.simulator, self.simulator_name = get_quantum_simulator()

    def run_batch(
        self,
        batch_size: int,
        start_index: int
    ) -> List[Dict[str, Any]]:
        """
        Build and execute a batch of BB84 qubit circuits in Qiskit.
        Returns a list of raw qubit outcome dictionaries.
        """
        # Step A: Alice generates random bits and preparation bases (0: +, 1: x)
        alice_bits = self.rng.integers(0, 2, batch_size)
        alice_bases = self.rng.integers(0, 2, batch_size)

        # Step B: Bob chooses random measurement bases (0: +, 1: x)
        bob_bases = self.rng.integers(0, 2, batch_size)

        # Eve interception decisions and bases
        eve_intercepts, eve_bases = self.attacker.generate_interceptions_and_bases(batch_size, self.rng)

        # Construct quantum circuit
        qr = QuantumRegister(batch_size, "q")
        cr_eve = ClassicalRegister(batch_size, "eve")
        cr_bob = ClassicalRegister(batch_size, "bob")
        qc = QuantumCircuit(qr, cr_eve, cr_bob)

        # Track channel noise labels
        channel_noise_types = []

        for i in range(batch_size):
            # Step A: Alice prepares qubit state
            # If bit == 1, apply Pauli-X: |0> -> |1>
            if alice_bits[i] == 1:
                qc.x(qr[i])
            # If basis == diagonal (1), apply Hadamard: |0> -> |+>, |1> -> |->
            if alice_bases[i] == 1:
                qc.h(qr[i])

            # Eve Intercept-Resend Attack (if intercepted)
            if eve_intercepts[i]:
                self.attacker.apply_intercept_resend(
                    circuit=qc,
                    qubit=qr[i],
                    eve_cbit=cr_eve[i],
                    eve_basis=int(eve_bases[i])
                )

            # Quantum Channel Transmission & Noise
            noise_type = self.channel.apply_channel_noise(qc, qr[i], self.rng)
            channel_noise_types.append(noise_type)

            # Step B: Bob measures the incoming qubit
            # If Bob's basis is diagonal (1), apply Hadamard before measuring in computational basis
            if bob_bases[i] == 1:
                qc.h(qr[i])
            qc.measure(qr[i], cr_bob[i])

        # Execute circuit on local Qiskit quantum simulator
        job = self.simulator.run(qc, shots=1)
        result = job.result()
        counts_dict = result.get_counts()
        bitstring = list(counts_dict.keys())[0]

        # Aer formats multiple classical registers as space-separated bitstrings: "cr_bob cr_eve"
        # and bitstrings are in reverse order (qubit N-1 down to 0)
        parts = bitstring.split(" ")
        bob_str = parts[0]
        eve_str = parts[1] if len(parts) > 1 else "0" * batch_size

        bob_outcomes = [int(b) for b in reversed(bob_str)]
        eve_outcomes = [int(b) for b in reversed(eve_str)]

        records = []
        for i in range(batch_size):
            global_idx = start_index + i
            a_bit = int(alice_bits[i])
            a_basis = int(alice_bases[i])
            b_basis = int(bob_bases[i])
            b_meas = int(bob_outcomes[i])
            e_inter = bool(eve_intercepts[i])
            e_basis = int(eve_bases[i]) if e_inter else None
            e_meas = int(eve_outcomes[i]) if e_inter else None
            
            basis_match = (a_basis == b_basis)
            sift_match = (a_bit == b_meas) if basis_match else None

            a_basis_str = "+" if a_basis == 0 else "x"
            b_basis_str = "+" if b_basis == 0 else "x"
            e_basis_str = ("+" if e_basis == 0 else "x") if e_inter else None
            
            e_resent_str = state_label(e_meas, e_basis) if e_inter and e_meas is not None and e_basis is not None else None

            records.append({
                "index": global_idx,
                "alice_bit": a_bit,
                "alice_basis": a_basis_str,
                "alice_state": state_label(a_bit, a_basis),
                "eve_intercepted": e_inter,
                "eve_basis": e_basis_str,
                "eve_measured": e_meas,
                "eve_resent_state": e_resent_str,
                "bob_basis": b_basis_str,
                "bob_measured": b_meas,
                "basis_matched": basis_match,
                "sifted_match": sift_match,
                "noise_type": channel_noise_types[i]
            })

        return records

    def run_full_simulation(self) -> Tuple[SimulationMetrics, KeyDisplay, List[QubitTransmissionRecord]]:
        """
        Executes the full BB84 simulation across all configured qubits.
        Performs basis reconciliation, parameter estimation, and security assessment.
        """
        start_time = time.time()
        num_qubits = self.config.num_qubits
        batch_size = min(self.config.batch_size, num_qubits)
        
        all_raw_records: List[Dict[str, Any]] = []
        processed = 0

        while processed < num_qubits:
            current_batch = min(batch_size, num_qubits - processed)
            batch_records = self.run_batch(current_batch, start_index=processed)
            all_raw_records.extend(batch_records)
            processed += current_batch

        # Step C: Basis Reconciliation
        # Keep only positions where Alice's and Bob's bases matched
        sifted_indices = [i for i, r in enumerate(all_raw_records) if r["basis_matched"]]
        sifted_count = len(sifted_indices)

        alice_sifted_bits = [all_raw_records[i]["alice_bit"] for i in sifted_indices]
        bob_sifted_bits = [all_raw_records[i]["bob_measured"] for i in sifted_indices]

        # Calculate overall sifted key errors and QBER
        sifted_errors = sum(1 for a, b in zip(alice_sifted_bits, bob_sifted_bits) if a != b)
        measured_qber = calculate_qber(sifted_errors, sifted_count)

        # Step D: Parameter Estimation (revealed sample)
        # Alice and Bob randomly reveal a subset of sifted bits to estimate error rate
        revealed_sample_indices: List[int] = []
        candidate_indices: List[int] = []
        sample_errors = 0
        sample_qber = 0.0

        if sifted_count > 0:
            sample_size = max(1, int(round(sifted_count * self.config.sample_fraction)))
            sample_size = min(sample_size, sifted_count)
            # Permute indices randomly to pick sample
            permuted = self.rng.permutation(sifted_count)
            sample_subset_positions = set(permuted[:sample_size])

            for pos, idx in enumerate(sifted_indices):
                if pos in sample_subset_positions:
                    revealed_sample_indices.append(idx)
                    all_raw_records[idx]["in_parameter_estimation"] = True
                    all_raw_records[idx]["in_candidate_key"] = False
                    if all_raw_records[idx]["alice_bit"] != all_raw_records[idx]["bob_measured"]:
                        sample_errors += 1
                else:
                    candidate_indices.append(idx)
                    all_raw_records[idx]["in_parameter_estimation"] = False
                    all_raw_records[idx]["in_candidate_key"] = True

            sample_qber = calculate_qber(sample_errors, len(revealed_sample_indices))
        else:
            sample_qber = 0.0

        # Confidence Interval based on revealed parameter estimation sample
        ci_low, ci_high = wilson_score_interval(
            sample_errors,
            len(revealed_sample_indices),
            confidence=0.95
        )

        # Security State Assessment
        security_state, security_assessment = evaluate_security_state(
            qber=sample_qber if len(revealed_sample_indices) >= 10 else measured_qber,
            sample_size=len(revealed_sample_indices),
            threshold=self.config.qber_threshold
        )

        # Calculate theoretical expectation
        theo_qber = theoretical_expected_qber(
            enable_eve=self.config.enable_eve,
            interception_prob=self.config.eve_interception_prob,
            enable_noise=self.config.enable_noise,
            noise_probability=self.config.noise_probability
        )

        # Count Eve metrics
        eve_intercepted_count = sum(1 for r in all_raw_records if r["eve_intercepted"])
        eve_rate = (eve_intercepted_count / num_qubits) * 100.0 if num_qubits > 0 else 0.0

        # Construct Keys
        alice_sifted_str = "".join(str(b) for b in alice_sifted_bits)
        bob_sifted_str = "".join(str(b) for b in bob_sifted_bits)
        
        revealed_alice = "".join(str(all_raw_records[i]["alice_bit"]) for i in revealed_sample_indices)
        revealed_bob = "".join(str(all_raw_records[i]["bob_measured"]) for i in revealed_sample_indices)

        candidate_key_bits = [str(all_raw_records[i]["alice_bit"]) for i in candidate_indices]
        candidate_key_str = "".join(candidate_key_bits)

        final_key_hash = None
        if security_state == SecurityState.SECURE and len(candidate_key_str) > 0:
            final_key_hash = hashlib.sha256(candidate_key_str.encode("utf-8")).hexdigest()

        keys = KeyDisplay(
            alice_sifted_key=alice_sifted_str,
            bob_sifted_key=bob_sifted_str,
            revealed_sample_indices=revealed_sample_indices,
            revealed_alice_sample=revealed_alice,
            revealed_bob_sample=revealed_bob,
            candidate_key=candidate_key_str if security_state != SecurityState.SUSPICIOUS else "DISCARDED_ATTACK_DETECTED",
            candidate_key_length=len(candidate_indices) if security_state != SecurityState.SUSPICIOUS else 0,
            final_key_hash=final_key_hash,
            is_masked=True
        )

        duration = time.time() - start_time

        metrics = SimulationMetrics(
            total_qubits=num_qubits,
            matching_bases_count=sifted_count,
            sifted_key_length=sifted_count,
            parameter_sample_length=len(revealed_sample_indices),
            candidate_key_length=keys.candidate_key_length,
            sifted_errors=sifted_errors,
            sample_errors=sample_errors,
            measured_qber=round(measured_qber, 2),
            sample_qber=round(sample_qber, 2),
            qber_confidence_interval_low=ci_low,
            qber_confidence_interval_high=ci_high,
            theoretical_expected_qber=theo_qber,
            security_state=security_state,
            security_assessment=security_assessment,
            eve_intercepted_count=eve_intercepted_count,
            eve_interception_rate=round(eve_rate, 2),
            eve_induced_errors=sifted_errors,
            execution_time_seconds=round(duration, 4),
            threshold=self.config.qber_threshold
        )

        records_models = [
            QubitTransmissionRecord(
                index=r["index"],
                alice_bit=r["alice_bit"],
                alice_basis=r["alice_basis"],
                alice_state=r["alice_state"],
                eve_intercepted=r["eve_intercepted"],
                eve_basis=r["eve_basis"],
                eve_measured=r["eve_measured"],
                eve_resent_state=r["eve_resent_state"],
                bob_basis=r["bob_basis"],
                bob_measured=r["bob_measured"],
                basis_matched=r["basis_matched"],
                sifted_match=r["sifted_match"],
                in_parameter_estimation=r.get("in_parameter_estimation", False),
                in_candidate_key=r.get("in_candidate_key", False)
            )
            for r in all_raw_records
        ]

        return metrics, keys, records_models
