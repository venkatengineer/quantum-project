# BB84 Quantum Key Distribution Protocol & Attack Detection

## 1. Introduction to BB84

Proposed in 1984 by Charles Bennett and Gilles Brassard, **BB84** was the world's first quantum key distribution protocol. Unlike classical asymmetric cryptography (RSA, ECC), whose security relies on unproven mathematical hardness assumptions, BB84 derives its information-theoretic security directly from fundamental laws of quantum mechanics:

1. **The No-Cloning Theorem**: An arbitrary unknown quantum state cannot be cloned identically without perturbing it.
2. **Heisenberg Uncertainty Principle / Wavefunction Collapse**: Measuring a quantum system in a basis non-orthogonal to its preparation basis irreversibly alters its quantum state.

---

## 2. Quantum State Encoding

Alice and Bob utilize two mutually unbiased bases (MUBs):

| Basis Name | Symbol | Basis State 0 | Basis State 1 | Preparation Gates |
| :--- | :---: | :---: | :---: | :---: |
| **Rectilinear (Computational)** | $+$ | $\|0\rangle$ | $\|1\rangle$ | None (0) or $X$ (1) |
| **Diagonal (Hadamard)** | $\times$ | $\|+\rangle = \frac{\|0\rangle + \|1\rangle}{\sqrt{2}}$ | $\|-\rangle = \frac{\|0\rangle - \|1\rangle}{\sqrt{2}}$ | $H$ (0) or $X$ then $H$ (1) |

Inner products between conjugate states:
$$|\langle 0 | + \rangle|^2 = |\langle 0 | - \rangle|^2 = |\langle 1 | + \rangle|^2 = |\langle 1 | - \rangle|^2 = \frac{1}{2}$$

When measured in the conjugate basis, any state produces an outcome of 0 or 1 with equal probability ($50\%$).

---

## 3. Protocol Phases

### Step A: Quantum State Preparation (Alice)
1. Alice generates random bits: $a_i \in \{0, 1\}$.
2. Alice generates independent random bases: $b_{A, i} \in \{+, \times\}$.
3. Alice encodes photon polarization using Qiskit quantum gates:
   - $a_i = 0, b_{A,i} = + \implies |0\rangle$
   - $a_i = 1, b_{A,i} = + \implies X|0\rangle = |1\rangle$
   - $a_i = 0, b_{A,i} = \times \implies H|0\rangle = |+\rangle$
   - $a_i = 1, b_{A,i} = \times \implies H X|0\rangle = |-\rangle$

### Step B: Quantum Transmission & Eavesdropping (Eve)
The photon travels through the quantum channel. If an eavesdropper (Eve) executes an **Intercept-Resend Attack**:
1. With probability $p_{eve}$, Eve intercepts the photon.
2. Eve picks a random basis $b_{E, i} \in \{+, \times\}$.
3. Eve measures the photon:
   - If $b_{E, i} = \times$, Eve applies $H$ prior to computational measurement.
   - The measurement collapses the photon into a classical outcome $e_i \in \{0, 1\}$.
4. Eve prepares a new replacement single photon in state $|e_i, b_{E, i}\rangle$ and resends it to Bob.

### Step C: Quantum State Measurement (Bob)
1. Bob independently chooses random measurement bases $b_{B, i} \in \{+, \times\}$.
2. Bob measures the received photon:
   - If $b_{B, i} = \times$, Bob applies $H$ gate prior to measuring.
3. Bob records classical bit outcome $m_{B, i} \in \{0, 1\}$.

### Step D: Basis Reconciliation (Sifting)
1. Alice and Bob publicly communicate their basis choices ($b_A$ and $b_B$) over an authenticated classical channel.
2. They retain positions where $b_{A, i} == b_{B, i}$ and discard mismatched positions ($b_{A, i} \neq b_{B, i}$).
3. Because bases are chosen uniformly at random, approximately $50\%$ of qubits are sifted.

### Step E: Parameter Estimation
1. Alice and Bob publicly announce and compare a random subset of sifted bits ($I_{sample} \subset I_{sifted}$, typically 30%).
2. They calculate the sample **Quantum Bit Error Rate (QBER)**.
3. **Crucial Security Step**: All bits in $I_{sample}$ are permanently discarded to ensure zero leakage.
4. Remaining unrevealed bits form the **Candidate Secret Key**: $I_{candidate} = I_{sifted} \setminus I_{sample}$.

---

## 4. Mathematical Derivation of Eavesdropping Error Rate

Suppose Alice and Bob selected matching bases ($b_A == b_B$), which are the only bits retained in the sifted key.

### Scenario 1: No Eavesdropper ($p_{eve} = 0$)
- Bob receives Alice's state unmodified.
- Because $b_B == b_A$, Bob measures the exact bit Alice sent:
  $$P(\text{error}) = 0\%$$

### Scenario 2: Full Intercept-Resend ($p_{eve} = 1.0$)
Eve measures every qubit:
1. **Case 1: Eve's basis matches Alice's basis ($b_E == b_A$)**:
   - Occurs with probability $P(b_E = b_A) = 0.5$.
   - Eve measures the correct bit $e = a$ with certainty.
   - Eve prepares and resends $|a, b_A\rangle$.
   - Bob measures in $b_B = b_A$, obtaining $m_B = a$.
   - Error introduced = $0\%$.

2. **Case 2: Eve's basis mismatches Alice's basis ($b_E \neq b_A$)**:
   - Occurs with probability $P(b_E \neq b_A) = 0.5$.
   - Eve measures in conjugate basis; her measurement outcome is 0 or 1 with probability 0.5 each.
   - Eve collapses the state and prepares replacement $|e, b_E\rangle$.
   - Bob measures $|e, b_E\rangle$ in basis $b_B = b_A$ (conjugate to Eve's).
   - Bob's measurement outcome is random: $P(m_B \neq a) = 0.5$.
   - Error introduced = $50\%$.

### Total Expected QBER for Full Attack:
$$E[\text{QBER}] = P(b_E = b_A) \times 0 + P(b_E \neq b_A) \times 0.5 = 0.5 \times 0 + 0.5 \times 0.5 = 0.25 = \mathbf{25.0\%}$$

### For Partial Attack with probability $p_{eve}$:
$$E[\text{QBER}] = 25.0\% \times p_{eve}$$

---

## 5. QBER Formula & Statistical Confidence

### Formula:
$$\text{QBER} = \left( \frac{\sum_{i \in I_{\text{sifted}}} \mathbb{I}(a_i \neq m_{B, i})}{|I_{\text{sifted}}|} \right) \times 100\%$$

### Wilson Score Interval (95% Confidence):
Because experimental sample sizes are finite, the measured sample QBER $\hat{p}$ has statistical variance. The 95% confidence interval is:

$$w_{\pm} = \frac{\hat{p} + \frac{z^2}{2n} \pm z \sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}$$

where $z = 1.95996$.

---

## 6. The 11.0% Security Threshold Rationale

In Shor & Preskill's rigorous security proof for BB84 (2000), the asymptotic secret key generation rate in the presence of an eavesdropper is bounded by:

$$R \ge 1 - 2 H_2(\text{QBER})$$

where $H_2(p) = -p \log_2(p) - (1-p) \log_2(1-p)$ is the binary entropy function.

Solving $1 - 2 H_2(p) = 0$ yields:
$$H_2(p) = 0.5 \implies p \approx \mathbf{11.0\%}$$

- If $\text{QBER} \le 11.0\%$: The information leaked to Eve can be entirely removed via privacy amplification while leaving a positive secret key rate ($R > 0$).
- If $\text{QBER} > 11.0\%$: Eve potentially possesses more mutual information than Alice and Bob share. Secret key distillation is mathematically impossible; the protocol must **abort**.
