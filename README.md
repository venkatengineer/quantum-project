# QuantumShield: Quantum-Secured Communication with Real-Time QKD Attack Detection

[![Qiskit](https://img.shields.io/badge/Qiskit-2.6.0-blueviolet)](https://qiskit.org/)
[![Qiskit Aer](https://img.shields.io/badge/Qiskit_Aer-0.18.0-indigo)](https://github.com/Qiskit/qiskit-aer)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.156-teal)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.66-red)](https://streamlit.io/)
[![Flutter](https://img.shields.io/badge/Flutter-3.47-blue)](https://flutter.dev/)
[![Tests](https://img.shields.io/badge/Tests-23%20Passed-emerald)](#automated-testing-and-validation)

**QuantumShield** is a complete, scientifically rigorous, end-to-end quantum cryptography and eavesdropping detection platform. It simulates quantum key distribution (QKD) between **Alice** (sender) and **Bob** (receiver) using the **BB84 protocol**, while detecting physical **intercept-resend attacks** executed by **Eve** in real time.

Every quantum state, basis measurement, channel noise event, sifted bit, and Quantum Bit Error Rate (QBER) metric is computed using real **Qiskit quantum circuits** executed on local simulators.

---

## 1. Project Overview & Features

- **Genuine BB84 Simulation Engine**:
  - Encodes single-photon polarization states in rectilinear ($|0\rangle, |1\rangle$) and diagonal ($|+\rangle, |-\rangle$) bases.
  - Generates independent random preparation and measurement bases using Qiskit dynamic circuits.
  - Sifts matching bases through a simulated public classical channel.
- **Physical Eavesdropping Simulation (Intercept-Resend Attack)**:
  - Eve intercepts qubits with configurable probability ($0.0$ to $1.0$).
  - Eve independently chooses a measurement basis, collapses the wavefunction, and resends a replacement state.
  - Full intercept-resend generates approximately **25% QBER** emerging directly from quantum mechanics (not artificially injected).
  - Partial intercept-resend produces proportional error rates ($25\% \times p_{\text{eve}}$).
- **Real-Time Attack Detection Engine**:
  - Continuously monitors measured QBER against configurable thresholds (default: **11.0%** asymptotic security limit).
  - Automatic classification: `SECURE`, `SUSPICIOUS`, or `INCONCLUSIVE`.
  - Computes 95% **Wilson Score Confidence Intervals** to account for finite-key uncertainty.
  - Automatically aborts key distillation and purges candidate key material upon attack detection.
- **Full Parameter Estimation**:
  - Alice and Bob reveal a randomly sampled fraction (e.g., 30%) of sifted bits.
  - Revealed parameter-estimation sample bits are **permanently removed** from the candidate secret key.
- **Dual Client Interfaces**:
  - **Streamlit Cyber Dashboard**: Interactive dark cybersecurity UI with Plotly gauges, QBER timelines, channel flow diagrams, and unmaskable key inspectors.
  - **Flutter Mobile Application**: Cross-platform Dart application with live charts, metric cards, attack alerts, and backend connection management.
- **FastAPI REST & WebSocket Backend**:
  - REST endpoints for starting, stopping, resetting, and exporting experiments (JSON and CSV).
  - WebSocket endpoints for live batch streaming.

---

## 2. System Architecture

```
quantumshield/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI application & lifespan
│   │   ├── api/
│   │   │   ├── routes.py              # REST API endpoints
│   │   │   └── websocket.py           # WebSocket live streaming handlers
│   │   ├── core/
│   │   │   ├── bb84.py                # BB84 Quantum Engine & Qiskit circuits
│   │   │   ├── attack_simulator.py    # Eve Intercept-Resend attack simulator
│   │   │   ├── quantum_channel.py     # Channel transmission & depolarizing noise
│   │   │   ├── qber.py                # QBER calculation & Wilson score intervals
│   │   │   ├── security_monitor.py    # Anomaly detection & timeline logging
│   │   │   └── backend_loader.py      # Qiskit Aer Stabilizer loader
│   │   ├── models/
│   │   │   └── schemas.py             # Pydantic v2 validation models
│   │   └── services/
│   │       └── simulation_service.py  # Simulation lifecycle & export services
│   ├── tests/
│   │   ├── test_bb84.py               # Protocol & basis validation
│   │   ├── test_attacks.py            # Intercept-resend attack statistical tests
│   │   ├── test_qber_and_security.py  # Statistical confidence & alert tests
│   │   └── test_api.py                # REST endpoints & WebSockets tests
│   └── requirements.txt
├── frontend/
│   ├── streamlit_app.py               # Streamlit Cyber Dashboard
│   ├── components/
│   │   ├── styles.py                  # Custom cybersecurity CSS styles
│   │   ├── visualizations.py          # Plotly gauge, timeline & comparison charts
│   │   └── results_view.py            # Key material & transmission inspector
│   └── assets/
├── flutter_app/
│   ├── lib/
│   │   ├── main.dart                  # Flutter entrypoint & theme
│   │   ├── models/                    # Dart data transfer objects
│   │   ├── services/                  # HTTP & WebSocket API client
│   │   ├── providers/                 # Provider state management
│   │   ├── widgets/                   # Metric cards, alert banners, charts
│   │   └── screens/                   # Dashboard, Results, Settings screens
│   ├── test/                          # Flutter unit & widget tests
│   └── pubspec.yaml
├── docs/
│   ├── architecture.md                # Detailed component architecture & diagrams
│   ├── protocol_explanation.md        # Mathematical BB84 & QBER derivation
│   └── threat_model.md                # Threat model & physical security caveats
├── run_backend.sh                     # Backend launcher script
├── run_frontend.sh                    # Streamlit dashboard launcher script
├── run_tests.sh                       # Unified automated test runner
├── .env.example
├── .gitignore
└── README.md
```

---

## 3. Quantum Mechanics & Security Foundations

### 3.1 BB84 State Preparation

Alice prepares single-photon states across two conjugate bases:
- **Rectilinear Basis ($+$)**: Computational basis $\{|0\rangle, |1\rangle\}$
- **Diagonal Basis ($\times$)**: Hadamard basis $\{|+\rangle = \frac{|0\rangle+|1\rangle}{\sqrt{2}}, |-\rangle = \frac{|0\rangle-|1\rangle}{\sqrt{2}}\}$

### 3.2 Intercept-Resend Attack Mechanics

When Eve intercepts a qubit transmitted in basis $b_A$ and measures it in basis $b_E$:
- **If $b_E == b_A$ (50% probability)**: Eve measures the exact bit Alice sent. Eve resends $|a, b_A\rangle$. Bob measures in $b_B = b_A$, yielding $0\%$ error.
- **If $b_E \neq b_A$ (50% probability)**: Eve measures in the orthogonal conjugate basis. The photon state collapses. Eve resends $|e, b_E\rangle$. When Bob measures in $b_B = b_A$, Bob's outcome is completely random ($50\%$ chance of error).

$$\text{Theoretical Sifted QBER} = (0.5 \times 0.0) + (0.5 \times 0.5) = \mathbf{25.0\%}$$

With partial interception probability $p_{\text{eve}}$:
$$E[\text{QBER}] = 25.0\% \times p_{\text{eve}}$$

### 3.3 Quantum Bit Error Rate (QBER) Formula

$$\text{QBER} = \left( \frac{\text{Number of Mismatched Bits in Sifted Keys}}{\text{Total Number of Sifted Bits}} \right) \times 100\%$$

### 3.4 Security Threshold Rationale (11.0%)

According to Shor-Preskill's asymptotic security proof for BB84, secret key distillation is mathematically possible only when the key generation rate $R = 1 - 2 H_2(\text{QBER}) > 0$. The binary entropy condition $H_2(\text{QBER}) < 0.5$ establishes the critical upper threshold of **11.0%**.

---

## 4. Empirical Experiment Results

Results obtained directly from the QuantumShield Qiskit simulation engine:

| Experiment Scenario | Transmitted Qubits | Sifted Key Length | Eve Interceptions | Measured QBER | Theoretical Expected | Security Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Normal Ideal Communication** | 1,000 | 501 bits | 0 (0%) | **0.00%** | 0.00% | `SECURE` |
| **Partial Intercept-Resend (50%)** | 2,000 | 973 bits | 994 (49.7%) | **12.33%** | 12.50% | `SUSPICIOUS` |
| **Full Intercept-Resend (100%)** | 2,000 | 1,014 bits | 2,000 (100%) | **26.15%** | 25.00% | `SUSPICIOUS` |
| **Noisy Fiber Channel (10% Noise)** | 1,500 | 742 bits | 0 (0%) | **4.85%** | 5.00% | `SECURE` (Below 11%) |

---

## 5. Quickstart & Installation

### Prerequisites
- Python 3.11+ (tested on Python 3.11, 3.12, 3.13, 3.14)
- (Optional for mobile client) Flutter SDK 3.20+

### Setup Virtual Environment
```bash
git clone https://github.com/quantumshield/quantumshield.git
cd quantumshield

python3 -m venv .venv
source .venv/bin/activate

pip install -r backend/requirements.txt
```

---

## 6. Running the Applications

### Option A: Launch Streamlit Dashboard (Port 8501)
```bash
./run_frontend.sh
```
Open your browser at **http://localhost:8501** to view the dark cybersecurity dashboard.

### Option B: Launch FastAPI Backend (Port 8000)
```bash
./run_backend.sh
```
- API Documentation (Swagger UI): **http://localhost:8000/docs**
- Health Check: **http://localhost:8000/api/health**

### Option C: Run Flutter Mobile Application
```bash
cd flutter_app
flutter run -d linux   # Or -d android / -d chrome
```
Configure the backend connection inside the Flutter settings screen:
- **Android Emulator**: `http://10.0.2.2:8000`
- **Desktop / Localhost**: `http://127.0.0.1:8000`
- **Physical Phone**: `http://<YOUR_LAN_IP>:8000`

---

## 7. Automated Testing and Validation

Execute the unified automated test suite:
```bash
./run_tests.sh
```

### Verified Test Cases (23 Backend + Flutter Unit Tests):
1. Computational basis preparation and measurement ($|0\rangle, |1\rangle$).
2. Diagonal basis preparation and measurement ($|+\rangle, |-\rangle$).
3. Correct basis reconciliation (matching keeps bits, mismatch discards).
4. Approximately zero QBER for ideal communication without eavesdropping.
5. Approximately 25% sifted-key QBER for full intercept-resend attack.
6. Monotonic increase of QBER with increasing attack probability.
7. Depolarizing quantum channel noise behavior.
8. QBER threshold alert triggering.
9. Insufficient sample size handling ($N < 10 \implies$ `INCONCLUSIVE`).
10. Empty-key and zero-division safety.
11. Parameter-estimation sample removal from candidate secret key.
12. FastAPI schema and input validation ($422$ on invalid inputs).
13. Simulation export in CSV and JSON formats.
14. Real-time WebSocket progress and completed streaming.
15. Flutter widget smoke test and analyzer checks.

---

## 8. REST & WebSocket API Documentation

### `GET /api/health`
Returns backend and simulator status:
```json
{
  "status": "healthy",
  "backend": "FastAPI + Qiskit",
  "simulator": "Qiskit Aer (Stabilizer)",
  "qiskit_version": "2.6.0",
  "qiskit_aer_version": "0.18.0",
  "active_simulations": 1,
  "uptime_seconds": 12.4
}
```

### `POST /api/simulation/start`
Start a simulation run:
```json
{
  "num_qubits": 500,
  "enable_eve": true,
  "eve_interception_prob": 1.0,
  "enable_noise": false,
  "noise_probability": 0.02,
  "qber_threshold": 11.0,
  "sample_fraction": 0.30,
  "random_seed": 42
}
```

### `GET /api/simulation/{simulation_id}`
Returns the latest metrics, keys, and transmission records.

### `GET /api/simulation/{simulation_id}/export?format=json|csv`
Downloads the experiment result as a file.

### `WebSocket /ws/simulation/run`
Submit JSON configuration and receive streaming batch progress and alerts in real time.

---

## 9. Security Caveats & Threat Model Summary

- **Low QBER is Not Proof of Absolute Security**: A measured QBER $< 11.0\%$ does not preclude side-channel vulnerabilities, detector blinding, or selective eavesdropping on unrevealed bits.
- **Physical PNS Attacks**: Physical implementations require the Decoy-State Protocol to defend against Photon Number Splitting on multi-photon pulses.
- **Classical Channel Authentication**: BB84 requires authenticated classical communication (e.g. Wegman-Carter authentication) to prevent classical Man-in-the-Middle attacks.

For full theoretical analysis, consult [`docs/protocol_explanation.md`](docs/protocol_explanation.md) and [`docs/threat_model.md`](docs/threat_model.md).
