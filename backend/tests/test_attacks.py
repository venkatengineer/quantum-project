"""
Tests for Eavesdropping Attack Simulation (Intercept-Resend)
Validates:
1. Approximately 25% sifted-key QBER for full intercept-resend (100% interception).
2. Proportional QBER scaling with partial interception probability (e.g. 50% -> ~12.5%).
3. Increasing interception probability strictly increases average QBER.
4. Channel noise adds expected error baseline.
5. Eve interception metrics tracking.
"""

import pytest
import numpy as np
from app.models.schemas import SimulationConfig, SecurityState
from app.core.bb84 import BB84SimulationEngine


def test_full_intercept_resend_qber():
    """
    Theoretical BB84 prediction: 100% intercept-resend causes ~25% QBER in sifted key.
    Within 99% binomial statistical confidence tolerance for N=2000.
    """
    config = SimulationConfig(
        num_qubits=2000,
        enable_eve=True,
        eve_interception_prob=1.0,
        enable_noise=False,
        random_seed=42
    )
    engine = BB84SimulationEngine(config)
    metrics, keys, records = engine.run_full_simulation()

    assert metrics.eve_intercepted_count == 2000
    assert metrics.sifted_key_length > 800
    # Expected QBER is 25%. For N ~ 1000 sifted bits, std dev is sqrt(0.25*0.75/1000) = ~1.37%.
    # 3 sigma range is [20.9%, 29.1%].
    assert 21.0 <= metrics.measured_qber <= 29.0, (
        f"Observed QBER {metrics.measured_qber}% outside expected 25% ± 4% band"
    )
    assert metrics.security_state == SecurityState.SUSPICIOUS


def test_partial_intercept_resend_qber():
    """
    With 50% interception probability, expected QBER is 25% * 0.5 = 12.5%.
    """
    config = SimulationConfig(
        num_qubits=2000,
        enable_eve=True,
        eve_interception_prob=0.5,
        enable_noise=False,
        random_seed=101
    )
    engine = BB84SimulationEngine(config)
    metrics, _, records = engine.run_full_simulation()

    # Interceptions should be roughly half
    assert 850 <= metrics.eve_intercepted_count <= 1150
    # Expected QBER around 12.5% ± 3.5%
    assert 9.0 <= metrics.measured_qber <= 16.0, (
        f"Observed QBER {metrics.measured_qber}% outside expected 12.5% ± 3.5% band"
    )


def test_monotonic_qber_increase_with_attack_probability():
    """Higher interception probability must result in higher average QBER."""
    # Test across multiple seeds or large sample
    qber_0 = 0.0
    
    config_low = SimulationConfig(num_qubits=2000, enable_eve=True, eve_interception_prob=0.25, random_seed=7)
    metrics_low, _, _ = BB84SimulationEngine(config_low).run_full_simulation()

    config_mid = SimulationConfig(num_qubits=2000, enable_eve=True, eve_interception_prob=0.60, random_seed=7)
    metrics_mid, _, _ = BB84SimulationEngine(config_mid).run_full_simulation()

    config_high = SimulationConfig(num_qubits=2000, enable_eve=True, eve_interception_prob=1.0, random_seed=7)
    metrics_high, _, _ = BB84SimulationEngine(config_high).run_full_simulation()

    assert qber_0 < metrics_low.measured_qber < metrics_mid.measured_qber < metrics_high.measured_qber, (
        f"QBER ordering violated: 0 < {metrics_low.measured_qber} < {metrics_mid.measured_qber} < {metrics_high.measured_qber}"
    )


def test_noisy_channel_behavior():
    """Noisy channel introduces errors even without Eve."""
    noise_prob = 0.10  # 10% depolarizing channel noise
    config = SimulationConfig(
        num_qubits=1500,
        enable_eve=False,
        enable_noise=True,
        noise_probability=noise_prob,
        random_seed=303
    )
    engine = BB84SimulationEngine(config)
    metrics, _, _ = engine.run_full_simulation()

    # Depolarizing noise produces approximately 0.5 * 10% = 5% QBER
    assert metrics.sifted_errors > 0
    assert 2.0 <= metrics.measured_qber <= 8.5


def test_eve_record_attributes():
    """Check that Eve's interception details are properly populated in transmission records."""
    config = SimulationConfig(
        num_qubits=100,
        enable_eve=True,
        eve_interception_prob=1.0,
        random_seed=42
    )
    engine = BB84SimulationEngine(config)
    _, _, records = engine.run_full_simulation()

    for r in records:
        assert r.eve_intercepted is True
        assert r.eve_basis in ("+", "x")
        assert r.eve_measured in (0, 1)
        assert r.eve_resent_state in ("|0⟩", "|1⟩", "|+⟩", "|−⟩")
