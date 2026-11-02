"""
QuantumShield Data Models & Schemas
Defines request, response, metric, and transmission record models.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


class Basis(str, Enum):
    RECTILINEAR = "+"  # Computational {|0>, |1>}
    DIAGONAL = "x"     # Hadamard {|+>, |->}


class SecurityState(str, Enum):
    SECURE = "SECURE"
    SUSPICIOUS = "SUSPICIOUS"
    INCONCLUSIVE = "INCONCLUSIVE"


class AttackType(str, Enum):
    NONE = "NONE"
    FULL_INTERCEPT_RESEND = "FULL_INTERCEPT_RESEND"
    PARTIAL_INTERCEPT_RESEND = "PARTIAL_INTERCEPT_RESEND"


class SimulationStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    STOPPED = "STOPPED"
    FAILED = "FAILED"


class SimulationConfig(BaseModel):
    num_qubits: int = Field(default=500, ge=10, le=10000, description="Total qubits transmitted by Alice")
    enable_eve: bool = Field(default=False, description="Enable Eve eavesdropping attack")
    eve_interception_prob: float = Field(default=1.0, ge=0.0, le=1.0, description="Probability of Eve intercepting each qubit")
    enable_noise: bool = Field(default=False, description="Enable realistic quantum channel noise")
    noise_probability: float = Field(default=0.02, ge=0.0, le=1.0, description="Channel depolarizing noise probability")
    qber_threshold: float = Field(default=11.0, ge=0.0, le=50.0, description="QBER alert threshold percentage (default 11%)")
    sample_fraction: float = Field(default=0.30, ge=0.05, le=0.90, description="Fraction of sifted bits revealed for parameter estimation")
    random_seed: Optional[int] = Field(default=None, description="Deterministic random seed for reproducibility")
    batch_size: int = Field(default=100, ge=10, le=2000, description="Qubit batch size for simulation execution and progress streaming")

    @property
    def attack_type(self) -> AttackType:
        if not self.enable_eve or self.eve_interception_prob <= 0.0:
            return AttackType.NONE
        elif self.eve_interception_prob >= 0.999:
            return AttackType.FULL_INTERCEPT_RESEND
        else:
            return AttackType.PARTIAL_INTERCEPT_RESEND


class QubitTransmissionRecord(BaseModel):
    index: int
    alice_bit: int
    alice_basis: str
    alice_state: str
    eve_intercepted: bool = False
    eve_basis: Optional[str] = None
    eve_measured: Optional[int] = None
    eve_resent_state: Optional[str] = None
    bob_basis: str
    bob_measured: int
    basis_matched: bool
    sifted_match: Optional[bool] = None
    in_parameter_estimation: bool = False
    in_candidate_key: bool = False


class SimulationMetrics(BaseModel):
    total_qubits: int
    matching_bases_count: int
    sifted_key_length: int
    parameter_sample_length: int
    candidate_key_length: int
    sifted_errors: int
    sample_errors: int
    measured_qber: float
    sample_qber: float
    qber_confidence_interval_low: float
    qber_confidence_interval_high: float
    theoretical_expected_qber: float
    security_state: SecurityState
    security_assessment: str
    eve_intercepted_count: int
    eve_interception_rate: float
    eve_induced_errors: int
    execution_time_seconds: float
    threshold: float


class KeyDisplay(BaseModel):
    alice_sifted_key: str
    bob_sifted_key: str
    revealed_sample_indices: List[int]
    revealed_alice_sample: str
    revealed_bob_sample: str
    candidate_key: str
    candidate_key_length: int
    final_key_hash: Optional[str] = None
    is_masked: bool = True
    disclaimer: str = "Simulated demonstration keys. Not for cryptographic production."


class TimelineEvent(BaseModel):
    timestamp: str
    simulation_id: str
    batch_index: int
    qubits_processed: int
    total_qubits: int
    current_qber: float
    security_state: SecurityState
    alert: bool
    message: str


class SimulationResponse(BaseModel):
    simulation_id: str
    status: SimulationStatus
    config: SimulationConfig
    metrics: Optional[SimulationMetrics] = None
    keys: Optional[KeyDisplay] = None
    records_sample: Optional[List[QubitTransmissionRecord]] = None
    error_message: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    backend: str
    simulator: str
    qiskit_version: str
    qiskit_aer_version: Optional[str]
    active_simulations: int
    uptime_seconds: float
