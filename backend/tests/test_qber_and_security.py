"""
Tests for Security Monitoring and Alerting
Validates:
1. QBER exceeding configurable threshold triggers SUSPICIOUS / alert.
2. Low QBER (< threshold) with sufficient bits triggers SECURE.
3. Insufficient sample size (< 10 bits) triggers INCONCLUSIVE.
4. Wilson confidence interval calculation correctness.
5. SecurityMonitor batch timeline logging and alert filtering.
"""

import pytest
from app.models.schemas import SecurityState
from app.core.qber import calculate_qber, wilson_score_interval, theoretical_expected_qber
from app.core.security_monitor import evaluate_security_state, SecurityMonitor


def test_wilson_confidence_interval():
    # 25 errors out of 100 bits: ~25%, interval should bracket 25
    low, high = wilson_score_interval(errors=25, n=100, confidence=0.95)
    assert low < 25.0 < high
    assert 16.0 <= low <= 19.0
    assert 32.0 <= high <= 36.0

    # 0 errors out of 100 bits
    low0, high0 = wilson_score_interval(errors=0, n=100, confidence=0.95)
    assert low0 == 0.0
    assert high0 < 5.0

    # Empty sample edge case
    assert wilson_score_interval(errors=0, n=0) == (0.0, 100.0)


def test_evaluate_security_state_insufficient_sample():
    state, msg = evaluate_security_state(qber=0.0, sample_size=5, threshold=11.0)
    assert state == SecurityState.INCONCLUSIVE
    assert "INCONCLUSIVE" in msg
    assert "Insufficient" in msg


def test_evaluate_security_state_suspicious():
    state, msg = evaluate_security_state(qber=18.5, sample_size=50, threshold=11.0)
    assert state == SecurityState.SUSPICIOUS
    assert "SUSPICIOUS" in msg
    assert "ABORT" in msg


def test_evaluate_security_state_secure():
    state, msg = evaluate_security_state(qber=1.2, sample_size=50, threshold=11.0)
    assert state == SecurityState.SECURE
    assert "SECURE" in msg
    assert "does NOT constitute mathematical proof" in msg


def test_security_monitor_timeline():
    monitor = SecurityMonitor(threshold=11.0)
    
    # Batch 1: normal
    ev1 = monitor.record_batch("sim-1", 1, 100, 300, current_qber=2.0, sample_size=50)
    assert ev1.security_state == SecurityState.SECURE
    assert not ev1.alert

    # Batch 2: attacked
    ev2 = monitor.record_batch("sim-1", 2, 200, 300, current_qber=24.0, sample_size=100)
    assert ev2.security_state == SecurityState.SUSPICIOUS
    assert ev2.alert

    timeline = monitor.get_timeline()
    assert len(timeline) == 2
    alerts = monitor.get_alerts()
    assert len(alerts) == 1
    assert alerts[0].batch_index == 2
