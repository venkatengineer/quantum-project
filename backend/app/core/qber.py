"""
Quantum Bit Error Rate (QBER) and Statistical Estimation
Provides mathematically rigorous QBER calculations, Wilson score intervals,
and theoretical expectation modeling for BB84 QKD.
"""

import math
from typing import Tuple


def calculate_qber(error_count: int, total_bits: int) -> float:
    """
    Calculate the Quantum Bit Error Rate as a percentage.
    
    QBER = (number of mismatched bits / total number of bits) * 100
    
    Gracefully handles total_bits == 0 without DivisionByZero error.
    """
    if total_bits <= 0:
        return 0.0
    return float((error_count / total_bits) * 100.0)


def wilson_score_interval(errors: int, n: int, confidence: float = 0.95) -> Tuple[float, float]:
    """
    Calculate the Wilson score confidence interval for binomial error rate.
    Accounts for finite sample size uncertainty in QBER estimation.
    
    Returns (lower_bound_percent, upper_bound_percent).
    """
    if n <= 0:
        return (0.0, 100.0)
    
    # z-score for standard confidence levels
    if math.isclose(confidence, 0.95, rel_tol=1e-2):
        z = 1.95996
    elif math.isclose(confidence, 0.99, rel_tol=1e-2):
        z = 2.57583
    elif math.isclose(confidence, 0.90, rel_tol=1e-2):
        z = 1.64485
    else:
        # Default fallback to 95%
        z = 1.96

    p_hat = errors / n
    z2 = z * z
    denom = 1.0 + z2 / n
    center = (p_hat + z2 / (2.0 * n)) / denom
    margin = (z / denom) * math.sqrt((p_hat * (1.0 - p_hat) / n) + (z2 / (4.0 * n * n)))
    
    low = max(0.0, (center - margin) * 100.0)
    high = min(100.0, (center + margin) * 100.0)
    return (round(low, 2), round(high, 2))


def theoretical_expected_qber(
    enable_eve: bool,
    interception_prob: float,
    enable_noise: bool,
    noise_probability: float
) -> float:
    """
    Compute theoretical expected QBER for BB84 given interception and channel parameters.
    
    - Ideal channel, no eavesdropper: 0.0%
    - Ideal channel, full intercept-resend (p=1.0): 25.0%
      Explanation: Eve chooses wrong basis 50% of the time. When Eve chooses wrong basis,
      Bob gets a 50% chance of error on matching bases. 0.5 * 0.5 = 25%.
    - Partial intercept-resend: 25.0% * interception_prob
    - Noise contribution: For depolarizing channel with noise_probability p_n,
      the single-qubit error rate adds approximately 0.5 * p_n on average.
    """
    eve_rate = 0.0
    if enable_eve:
        eve_rate = 25.0 * max(0.0, min(1.0, interception_prob))
        
    noise_rate = 0.0
    if enable_noise:
        # Depolarizing channel: with probability noise_probability, state is randomized
        # Random measurement outcome gives 50% error rate
        noise_rate = 50.0 * max(0.0, min(1.0, noise_probability))
        
    # Combined error rate: (1 - e_noise) * e_eve + e_noise * (1 - e_eve * 0.01) approx
    if enable_noise and enable_eve:
        e_n = noise_rate / 100.0
        e_e = eve_rate / 100.0
        combined = (e_n * (1.0 - e_e) + e_e * (1.0 - e_n) + 0.5 * e_n * e_e) * 100.0
        return round(min(100.0, combined), 2)
    
    return round(eve_rate + noise_rate, 2)
