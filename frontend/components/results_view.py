"""
Results and Quantum Channel View Components
Renders key displays, masked candidate keys, transmission inspectors, and channel flow visualizers.
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional


def render_transmission_flow(records_sample: List[Any], enable_eve: bool):
    """
    Renders the quantum channel transmission pathway:
    Alice -> Quantum Channel (Eve if active) -> Bob.
    """
    st.markdown("### 📡 Quantum Channel Transmission Pipeline")
    
    col_a, col_c, col_b = st.columns([1.2, 2.2, 1.2])
    
    with col_a:
        st.markdown(
            """
            <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.4); border-radius: 8px; padding: 14px; text-align: center;">
                <div style="font-size: 1.5rem;">👩‍💻</div>
                <div style="font-weight: 700; color: #60A5FA;">ALICE (Sender)</div>
                <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 4px;">Prepares Single Photons (|0⟩, |1⟩, |+⟩, |−⟩)</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_c:
        eve_badge = ""
        if enable_eve:
            eve_badge = """
            <div style="background: rgba(239, 68, 68, 0.2); border: 1px solid #EF4444; border-radius: 6px; padding: 8px; margin: 8px auto; max-width: 240px; text-align: center;">
                <span style="font-size: 1.1rem;">🕵️‍♀️</span>
                <span style="font-weight: 700; color: #F87171; font-size: 0.85rem;">EVE INTERCEPT-RESEND</span>
                <div style="font-size: 0.7rem; color: #FCA5A5;">Measures & Collapses State</div>
            </div>
            """
        else:
            eve_badge = """
            <div style="background: rgba(16, 185, 129, 0.1); border: 1px dashed rgba(16, 185, 129, 0.4); border-radius: 6px; padding: 6px; margin: 8px auto; max-width: 240px; text-align: center;">
                <span style="color: #34D399; font-size: 0.8rem;">🛡️ UNTAPPED FIBER OPTIC LINE</span>
            </div>
            """

        st.markdown(
            f"""
            <div style="background: rgba(15, 23, 42, 0.5); border: 1px solid #334155; border-radius: 8px; padding: 12px; text-align: center;">
                <div style="font-size: 0.8rem; color: #94A3B8; letter-spacing: 1px;">QUANTUM TRANSMISSION CHANNEL</div>
                {eve_badge}
                <div style="font-size: 0.75rem; color: #64748B;">Polarization State Preserved / Perturbed</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_b:
        st.markdown(
            """
            <div style="background: rgba(6, 182, 212, 0.1); border: 1px solid rgba(6, 182, 212, 0.4); border-radius: 8px; padding: 14px; text-align: center;">
                <div style="font-size: 1.5rem;">👨‍💻</div>
                <div style="font-weight: 700; color: #38BDF8;">BOB (Receiver)</div>
                <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 4px;">Independent Random Basis Measurement (+ / ×)</div>
            </div>
            """,
            unsafe_allow_html=True
        )


def render_key_material_panel(keys: Any, security_state: str):
    """
    Renders sifted keys, revealed estimation samples, candidate keys, and security status.
    Default display is masked with user-controlled reveal.
    """
    st.markdown("### 🔑 Cryptographic Key Material & Post-Processing")

    st.caption(
        "⚠️ **Educational Simulator Notice**: All displayed keys are simulated demonstration material. "
        "Production BB84 requires authenticated classical channels, hardware detectors, error reconciliation (Cascade), "
        "and privacy amplification (Toeplitz hashing)."
    )

    col1, col2 = st.columns(2)

    reveal_keys = st.checkbox("🔓 Reveal simulated key bitstrings (Unmask)", value=False)

    alice_sifted = keys.alice_sifted_key if hasattr(keys, "alice_sifted_key") else keys.get("alice_sifted_key", "")
    bob_sifted = keys.bob_sifted_key if hasattr(keys, "bob_sifted_key") else keys.get("bob_sifted_key", "")
    candidate_key = keys.candidate_key if hasattr(keys, "candidate_key") else keys.get("candidate_key", "")
    revealed_indices = keys.revealed_sample_indices if hasattr(keys, "revealed_sample_indices") else keys.get("revealed_sample_indices", [])
    revealed_alice = keys.revealed_alice_sample if hasattr(keys, "revealed_alice_sample") else keys.get("revealed_alice_sample", "")
    revealed_bob = keys.revealed_bob_sample if hasattr(keys, "revealed_bob_sample") else keys.get("revealed_bob_sample", "")
    final_hash = keys.final_key_hash if hasattr(keys, "final_key_hash") else keys.get("final_key_hash", None)

    mask_fn = lambda s: s if reveal_keys else ("•" * len(s) if s and not s.startswith("DISCARDED") else s)

    with col1:
        st.markdown("**Alice's Sifted Key (Matching Bases):**")
        st.markdown(f'<div class="key-box">{mask_fn(alice_sifted) or "(Empty)"}</div>', unsafe_allow_html=True)
        st.caption(f"Length: {len(alice_sifted)} bits")

        st.markdown("**Revealed Parameter Estimation Sample (Alice):**")
        st.markdown(f'<div class="key-box">{mask_fn(revealed_alice) or "(None)"}</div>', unsafe_allow_html=True)
        st.caption(f"Sample length: {len(revealed_alice)} bits (Publicly announced & permanently discarded)")

    with col2:
        st.markdown("**Bob's Sifted Key (Matching Bases):**")
        st.markdown(f'<div class="key-box">{mask_fn(bob_sifted) or "(Empty)"}</div>', unsafe_allow_html=True)
        st.caption(f"Length: {len(bob_sifted)} bits")

        st.markdown("**Revealed Parameter Estimation Sample (Bob):**")
        st.markdown(f'<div class="key-box">{mask_fn(revealed_bob) or "(None)"}</div>', unsafe_allow_html=True)
        st.caption(f"Sample length: {len(revealed_bob)} bits (Publicly announced & permanently discarded)")

    st.markdown("---")
    
    # Candidate / Final Key Status
    if security_state == "SUSPICIOUS":
        st.markdown(
            """
            <div class="alert-banner-attack">
                <strong>🚨 CRITICAL ALERT — CANDIDATE KEY DESTROYED:</strong><br>
                Because the measured QBER exceeded the security threshold, eavesdropping was confirmed. 
                In compliance with the BB84 protocol specification, the candidate key has been 
                <strong>immediately purged and invalidated</strong>. No secret key is generated.
            </div>
            """,
            unsafe_allow_html=True
        )
    elif security_state == "SECURE":
        st.markdown(
            f"""
            <div class="alert-banner-secure">
                <strong>✅ CANDIDATE KEY RETAINED (SECURE BOUNDS):</strong><br>
                QBER remained within acceptable noise thresholds. Revealed test bits were stripped. 
                Remaining candidate key length: <strong>{len(candidate_key)} bits</strong>.
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("**Remaining Candidate Secret Key (Unrevealed Bits):**")
        st.markdown(f'<div class="key-box key-box-candidate">{mask_fn(candidate_key)}</div>', unsafe_allow_html=True)
        if final_hash:
            st.markdown(f"**Demonstration SHA-256 Key Fingerprint:** `{final_hash}`")
    else:
        st.markdown(
            """
            <div style="background: rgba(245, 158, 11, 0.15); border-left: 4px solid #F59E0B; padding: 14px; border-radius: 4px; margin: 12px 0;">
                <strong>⚠️ INCONCLUSIVE SESSION:</strong> Insufficient sifted bits available for statistical verification.
            </div>
            """,
            unsafe_allow_html=True
        )


def render_transmission_table(records: List[Any], limit: int = 100):
    """Renders a structured, searchable transmission table with quantum properties."""
    st.markdown(f"### 🔬 Qubit-Level Transmission Inspector (Showing first {min(limit, len(records))} qubits)")

    if not records:
        st.info("No transmission records available. Launch a simulation to view quantum qubit records.")
        return

    data = []
    for r in records[:limit]:
        idx = r.index if hasattr(r, "index") else r.get("index", 0)
        a_bit = r.alice_bit if hasattr(r, "alice_bit") else r.get("alice_bit", 0)
        a_basis = r.alice_basis if hasattr(r, "alice_basis") else r.get("alice_basis", "+")
        a_state = r.alice_state if hasattr(r, "alice_state") else r.get("alice_state", "|0⟩")
        
        eve_int = r.eve_intercepted if hasattr(r, "eve_intercepted") else r.get("eve_intercepted", False)
        eve_basis = (r.eve_basis if hasattr(r, "eve_basis") else r.get("eve_basis")) or "-"
        eve_meas = (r.eve_measured if hasattr(r, "eve_measured") else r.get("eve_measured"))
        eve_meas_str = str(eve_meas) if eve_meas is not None else "-"
        eve_state = (r.eve_resent_state if hasattr(r, "eve_resent_state") else r.get("eve_resent_state")) or "-"

        b_basis = r.bob_basis if hasattr(r, "bob_basis") else r.get("bob_basis", "+")
        b_meas = r.bob_measured if hasattr(r, "bob_measured") else r.get("bob_measured", 0)
        matched = r.basis_matched if hasattr(r, "basis_matched") else r.get("basis_matched", False)
        sift_match = r.sifted_match if hasattr(r, "sifted_match") else r.get("sifted_match", None)

        sift_status = "N/A (Bases Disagree)"
        if matched:
            sift_status = "✅ Bit Match" if sift_match else "❌ Error (Mismatch)"

        in_param = r.in_parameter_estimation if hasattr(r, "in_parameter_estimation") else r.get("in_parameter_estimation", False)
        in_cand = r.in_candidate_key if hasattr(r, "in_candidate_key") else r.get("in_candidate_key", False)

        role = "Discarded (Basis Mismatch)"
        if in_param:
            role = "Revealed Parameter Sample"
        elif in_cand:
            role = "Candidate Secret Key"

        data.append({
            "Qubit #": idx,
            "Alice Bit": a_bit,
            "Alice Basis": a_basis,
            "Alice State": a_state,
            "Eve Intercepted": "🚨 YES" if eve_int else "No",
            "Eve Basis": eve_basis,
            "Eve Measured": eve_meas_str,
            "Eve Resent": eve_state,
            "Bob Basis": b_basis,
            "Bob Measured": b_meas,
            "Basis Match": "MATCH" if matched else "MISMATCH",
            "Sifted Status": sift_status,
            "Key Allocation": role
        })

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, height=360)
