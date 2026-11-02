# QuantumShield Threat Model & Security Caveats

## 1. Security Scope: What QuantumShield Models

QuantumShield is an educational, research-grade quantum communication simulation platform. It simulates:

1. **BB84 Single-Photon Polarization Encoding**:
   Quantum state preparation and measurement across two conjugate bases using exact Qiskit quantum circuits.
2. **Intercept-Resend Attacks (Full & Partial)**:
   Individual eavesdropping where Eve intercepts single photons, measures them in a randomly chosen basis, and re-prepares replacement states.
3. **Depolarizing Quantum Channel Noise**:
   Stochastic Pauli $X, Y, Z$ perturbations simulating fiber birefringence, thermal fluctuations, and optical component misalignment.
4. **Finite-Sample Statistical Fluctuations**:
   Wilson score confidence intervals accounting for finite parameter estimation sampling.
5. **Threshold-Based Attack Detection**:
   Automated detection comparing measured QBER against the theoretical asymptotic Shor-Preskill threshold (11.0%).

---

## 2. Real-World Attacks & Caveats NOT Modeled

In physical quantum key distribution deployments, an adversary is not restricted to naive intercept-resend attacks. Real-world QKD systems face physical device imperfections:

### 2.1 Photon Number Splitting (PNS) Attacks
- **Physical Reality**: Practical single-photon sources use attenuated weak coherent laser pulses ($|\alpha\rangle$) rather than true single-photon Fock states. Some pulses contain multiple photons ($n \ge 2$) with Poisson probability $P(n) = \frac{\mu^n e^{-\mu}}{n!}$.
- **PNS Vulnerability**: Eve can split off one photon from multi-photon pulses, store it in a quantum memory, and send the remaining photon to Bob without inducing any error!
- **Countermeasure**: Physical QKD uses the **Decoy-State Protocol** (varying pulse intensities $\mu, \nu$) to detect PNS attacks.

### 2.2 Quantum Memory & Coherent/Collective Attacks
- **Vulnerability**: Eve can entangle an ancilla qubit with Alice's photon (probe state) and store the probe in a coherent quantum memory until Alice and Bob announce their bases over the classical channel. Eve then measures her ancilla in the correct announced basis.
- **Defense**: Rigorous privacy amplification bounds.

### 2.3 Detector Blinding & Side-Channel Attacks
- **Vulnerability**: Single-Photon Avalanche Diodes (SPADs) can be blinded by high-intensity classical laser illumination, forcing detectors into linear Geiger mode where Eve completely dictates which detector clicks.
- **Defense**: Measurement-Device-Independent QKD (MDI-QKD) and Device-Independent QKD (DI-QKD) based on Bell inequality violations.

### 2.4 Classical Man-in-the-Middle (MitM) Attacks
- **Assumption**: BB84 assumes an **authenticated public classical channel** (e.g., using pre-shared key material via Wegman-Carter authentication). If the classical channel is unauthenticated, an active attacker can MitM the entire protocol.

---

## 3. Important Quantum Cybersecurity Statement

> [!CAUTION]
> **A low measured QBER is NOT mathematical proof of the absence of an eavesdropper.**
> 
> In finite-key regimes, an adversary who intercepts only a tiny fraction of qubits might introduce errors below statistical detection thresholds. 
> Furthermore, physical implementation loopholes (timing side channels, backflash emission, detector efficiency mismatch) allow information leakage without disturbing transmitted qubits.
> 
> Therefore, BB84 candidate keys must undergo rigorous Information Reconciliation (error correction) followed by Privacy Amplification (universal hash compression) to ensure composable cryptographic security ($\epsilon$-security).
