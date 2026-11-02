"""
Security Monitoring and Real-Time Attack Detection Engine
Evaluates measured QBER against thresholds, calculates confidence bounds,
and generates cybersecurity risk assessments for BB84 transmission.
"""

from typing import Tuple, List, Dict, Any
from datetime import datetime, timezone
from ..models.schemas import SecurityState, TimelineEvent


MIN_SAMPLE_SIZE_FOR_SECURITY = 10


def evaluate_security_state(
    qber: float,
    sample_size: int,
    threshold: float = 11.0
) -> Tuple[SecurityState, str]:
    """
    Evaluate the security state of BB84 transmission based on measured QBER and sample size.
    
    Returns (SecurityState, explanatory_assessment).
    """
    if sample_size < MIN_SAMPLE_SIZE_FOR_SECURITY:
        state = SecurityState.INCONCLUSIVE
        assessment = (
            f"INCONCLUSIVE: Insufficient sifted bits sampled ({sample_size} < {MIN_SAMPLE_SIZE_FOR_SECURITY}). "
            "A statistically sound security assessment cannot be established without adequate sample size."
        )
        return state, assessment

    if qber > threshold:
        state = SecurityState.SUSPICIOUS
        assessment = (
            f"SUSPICIOUS (ATTACK ALERT): Measured QBER of {qber:.2f}% exceeds the configured "
            f"security threshold of {threshold:.2f}%. Quantum disturbance detected, indicating active "
            "eavesdropping (such as an Intercept-Resend attack) or excessive channel decoherence. "
            "Recommendation: ABORT key distribution and discard candidate key material."
        )
    else:
        state = SecurityState.SECURE
        assessment = (
            f"SECURE (WITHIN BOUNDS): Measured QBER of {qber:.2f}% is below the security threshold of {threshold:.2f}%. "
            "Observed disturbance is consistent with normal channel operation. "
            "Security Note: A low measured QBER does NOT constitute mathematical proof of security against "
            "arbitrary side-channel attacks or selective eavesdropping without complete finite-key privacy amplification."
        )

    return state, assessment


class SecurityMonitor:
    """
    Maintains security monitoring timeline, batch logs, and alert history.
    """
    def __init__(self, threshold: float = 11.0):
        self.threshold = threshold
        self.events: List[TimelineEvent] = []

    def record_batch(
        self,
        simulation_id: str,
        batch_index: int,
        qubits_processed: int,
        total_qubits: int,
        current_qber: float,
        sample_size: int
    ) -> TimelineEvent:
        """
        Record a simulation batch progress event and check for anomalies.
        """
        state, assessment = evaluate_security_state(
            qber=current_qber,
            sample_size=sample_size,
            threshold=self.threshold
        )
        is_alert = (state == SecurityState.SUSPICIOUS)
        now_str = datetime.now(timezone.utc).isoformat()
        
        event = TimelineEvent(
            timestamp=now_str,
            simulation_id=simulation_id,
            batch_index=batch_index,
            qubits_processed=qubits_processed,
            total_qubits=total_qubits,
            current_qber=round(current_qber, 2),
            security_state=state,
            alert=is_alert,
            message=assessment
        )
        self.events.append(event)
        return event

    def get_timeline(self) -> List[TimelineEvent]:
        return list(self.events)

    def get_alerts(self) -> List[TimelineEvent]:
        return [e for e in self.events if e.alert]

    def reset(self):
        self.events.clear()
