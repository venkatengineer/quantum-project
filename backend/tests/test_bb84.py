"""
Tests for BB84 Protocol Core Engine
Validates:
1. Computational basis preparation and measurement (|0>, |1>).
2. Diagonal basis preparation and measurement (|+>, |->).
3. Basis reconciliation (matching keeps bits, mismatch discards).
4. Approximately zero QBER for ideal communication.
5. Parameter-estimation sample removal from candidate key.
6. Empty/edge case handling.
"""

import pytest
import numpy as np
from app.models.schemas import SimulationConfig, SecurityState
from app.core.bb84 import BB84SimulationEngine, state_label
from app.core.qber import calculate_qber


def test_state_labels():
    assert state_label(0, 0) == "|0⟩"
    assert state_label(1, 0) == "|1⟩"
    assert state_label(0, 1) == "|+⟩"
    assert state_label(1, 1) == "|−⟩"


def test_computational_basis_measurements():
    """Qubits prepared and measured in computational basis must yield identical outcomes in ideal channel."""
    config = SimulationConfig(
        num_qubits=200,
        enable_eve=False,
        enable_noise=False,
        random_seed=42
    )
    engine = BB84SimulationEngine(config)
    _, _, records = engine.run_full_simulation()

    # Filter only those where both Alice and Bob chose rectilinear basis (+)
    rect_records = [r for r in records if r.alice_basis == "+" and r.bob_basis == "+"]
    assert len(rect_records) > 30, "Should have sufficient rectilinear basis matches"
    
    for r in rect_records:
        assert r.alice_bit == r.bob_measured, (
            f"Computational basis bit mismatch at qubit {r.index}: sent {r.alice_bit}, received {r.bob_measured}"
        )


def test_diagonal_basis_measurements():
    """Qubits prepared and measured in diagonal basis must yield identical outcomes in ideal channel."""
    config = SimulationConfig(
        num_qubits=200,
        enable_eve=False,
        enable_noise=False,
        random_seed=123
    )
    engine = BB84SimulationEngine(config)
    _, _, records = engine.run_full_simulation()

    # Filter only those where both Alice and Bob chose diagonal basis (x)
    diag_records = [r for r in records if r.alice_basis == "x" and r.bob_basis == "x"]
    assert len(diag_records) > 30, "Should have sufficient diagonal basis matches"

    for r in diag_records:
        assert r.alice_bit == r.bob_measured, (
            f"Diagonal basis bit mismatch at qubit {r.index}: sent {r.alice_bit}, received {r.bob_measured}"
        )


def test_basis_reconciliation_filtering():
    """Reconciliation keeps only matching basis indices and discards mismatched ones."""
    config = SimulationConfig(
        num_qubits=300,
        enable_eve=False,
        enable_noise=False,
        random_seed=999
    )
    engine = BB84SimulationEngine(config)
    metrics, keys, records = engine.run_full_simulation()

    # Sifted key length must equal number of basis matches
    matching_count = sum(1 for r in records if r.alice_basis == r.bob_basis)
    assert metrics.matching_bases_count == matching_count
    assert metrics.sifted_key_length == matching_count
    assert len(keys.alice_sifted_key) == matching_count
    assert len(keys.bob_sifted_key) == matching_count

    # Bases must match for every sifted bit
    sifted_records = [r for r in records if r.basis_matched]
    for r in sifted_records:
        assert r.alice_basis == r.bob_basis


def test_zero_qber_ideal_communication():
    """Ideal BB84 communication without Eve or channel noise must have 0% QBER."""
    config = SimulationConfig(
        num_qubits=500,
        enable_eve=False,
        enable_noise=False,
        random_seed=777
    )
    engine = BB84SimulationEngine(config)
    metrics, keys, _ = engine.run_full_simulation()

    assert metrics.measured_qber == 0.0
    assert metrics.sifted_errors == 0
    assert metrics.security_state == SecurityState.SECURE
    assert keys.alice_sifted_key == keys.bob_sifted_key


def test_parameter_estimation_sample_removal():
    """Revealed parameter estimation bits must be excised from the candidate key."""
    config = SimulationConfig(
        num_qubits=400,
        sample_fraction=0.4,
        enable_eve=False,
        enable_noise=False,
        random_seed=555
    )
    engine = BB84SimulationEngine(config)
    metrics, keys, records = engine.run_full_simulation()

    assert metrics.parameter_sample_length > 0
    assert metrics.candidate_key_length > 0
    # Candidate key length + parameter sample length must equal total sifted key length
    assert metrics.parameter_sample_length + metrics.candidate_key_length == metrics.sifted_key_length

    # Ensure no index in revealed sample appears in candidate key
    sample_indices = set(keys.revealed_sample_indices)
    for r in records:
        if r.index in sample_indices:
            assert r.in_parameter_estimation is True
            assert r.in_candidate_key is False
        elif r.basis_matched:
            assert r.in_parameter_estimation is False
            assert r.in_candidate_key is True


def test_zero_division_safety():
    """QBER calculation must handle 0 total bits safely without throwing ZeroDivisionError."""
    assert calculate_qber(0, 0) == 0.0
    assert calculate_qber(5, 0) == 0.0
