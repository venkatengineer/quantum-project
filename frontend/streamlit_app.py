"""
QuantumShield Streamlit Dashboard
Interactive cybersecurity and quantum communication monitoring platform.
Visualizes BB84 protocol execution, real-time QBER monitoring, and Eve intercept-resend attack detection.
"""

import sys
import os
import io
import json
import csv
from datetime import datetime

# Add backend and frontend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
frontend_dir = os.path.abspath(os.path.dirname(__file__))
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

for p in [backend_dir, frontend_dir, project_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st
import numpy as np
import pandas as pd

from app.models.schemas import SimulationConfig, SecurityState
from app.core.bb84 import BB84SimulationEngine
from app.core.backend_loader import get_backend_info
from app.core.qber import wilson_score_interval, theoretical_expected_qber
from components.styles import DARK_THEME_CSS
from components.visualizations import (
    create_qber_gauge,
    create_qber_history_chart,
    create_normal_vs_attack_comparison_chart,
    create_basis_breakdown_chart,
)
from components.results_view import (
    render_transmission_flow,
    render_key_material_panel,
    render_transmission_table,
)

# Page configuration
st.set_page_config(
    page_title="QuantumShield — BB84 QKD & Attack Detection",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS
st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)

# Initialize Session State
if "history" not in st.session_state:
    st.session_state.history = []
if "current_run" not in st.session_state:
    st.session_state.current_run = None
if "normal_comparison_run" not in st.session_state:
    st.session_state.normal_comparison_run = None
if "attack_comparison_run" not in st.session_state:
    st.session_state.attack_comparison_run = None
if "active_timeline" not in st.session_state:
    st.session_state.active_timeline = []

# Fetch Backend Info
backend_info = get_backend_info()


# =====================================================================
# SIDEBAR CONTROLS
# =====================================================================
st.sidebar.markdown("## ⚙️ Simulation Controls")

qubit_choice = st.sidebar.select_slider(
    "Number of Qubits (Alice):",
    options=[100, 500, 1000, 5000],
    value=500,
    help="Total number of single photons/qubits transmitted across the quantum channel."
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🕵️‍♀️ Eavesdropper (Eve) Configuration")

enable_eve = st.sidebar.checkbox(
    "Enable Eve (Intercept-Resend Attack)",
    value=False,
    help="When enabled, Eve intercepts transmitted qubits, measures them in a random basis, and resends replacement states to Bob."
)

eve_interception_prob = 1.0
if enable_eve:
    eve_interception_prob = st.sidebar.slider(
        "Eve Interception Probability:",
        min_value=0.0,
        max_value=1.0,
        value=1.0,
        step=0.05,
        format="%.2f",
        help="Probability (0.0 to 1.0) that Eve intercepts any individual transmitted qubit. 1.0 = Full Attack, <1.0 = Partial Attack."
    )
    if eve_interception_prob >= 0.99:
        st.sidebar.caption("🔴 **Full Intercept-Resend Attack** (Theoretical QBER ≈ 25%)")
    else:
        st.sidebar.caption(f"🟠 **Partial Attack** (Expected QBER ≈ {25.0 * eve_interception_prob:.1f}%)")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🛡️ Security & Channel Parameters")

qber_threshold = st.sidebar.slider(
    "QBER Alert Threshold (%):",
    min_value=1.0,
    max_value=25.0,
    value=11.0,
    step=0.5,
    help="Maximum tolerable Quantum Bit Error Rate before declaring the channel compromised (BB84 theoretical security limit is 11.0%)."
)

sample_fraction = st.sidebar.slider(
    "Parameter Estimation Fraction:",
    min_value=0.10,
    max_value=0.70,
    value=0.30,
    step=0.05,
    help="Fraction of sifted bits randomly announced and permanently discarded to evaluate QBER."
)

enable_noise = st.sidebar.checkbox(
    "Enable Quantum Channel Noise",
    value=False,
    help="Simulates realistic physical depolarizing noise in optical fibers (thermal/polarization drift)."
)

noise_probability = 0.02
if enable_noise:
    noise_probability = st.sidebar.slider(
        "Channel Noise Probability:",
        min_value=0.01,
        max_value=0.15,
        value=0.03,
        step=0.01,
        format="%.2f"
    )

use_seed = st.sidebar.checkbox("Use Deterministic Random Seed", value=False)
random_seed = None
if use_seed:
    random_seed = st.sidebar.number_input("Seed Value:", min_value=1, max_value=999999, value=42)

st.sidebar.markdown("---")

col_btn1, col_btn2 = st.sidebar.columns(2)
start_sim = col_btn1.button("🚀 Launch Run", use_container_width=True, type="primary")
reset_sim = col_btn2.button("🔄 Reset", use_container_width=True)

compare_sim = st.sidebar.button("⚖️ Run Normal vs Attacked Comparison", use_container_width=True)


# =====================================================================
# SIMULATION EXECUTION HANDLERS
# =====================================================================
if reset_sim:
    st.session_state.current_run = None
    st.session_state.active_timeline.clear()
    st.session_state.normal_comparison_run = None
    st.session_state.attack_comparison_run = None
    st.rerun()

if start_sim:
    config = SimulationConfig(
        num_qubits=qubit_choice,
        enable_eve=enable_eve,
        eve_interception_prob=eve_interception_prob,
        enable_noise=enable_noise,
        noise_probability=noise_probability,
        qber_threshold=qber_threshold,
        sample_fraction=sample_fraction,
        random_seed=random_seed
    )
    with st.spinner("Simulating Qiskit quantum circuits and basis reconciliation..."):
        engine = BB84SimulationEngine(config)
        metrics, keys, records = engine.run_full_simulation()

        st.session_state.current_run = {
            "config": config,
            "metrics": metrics,
            "keys": keys,
            "records": records,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }

        # Record timeline event
        st.session_state.active_timeline.append({
            "batch_index": len(st.session_state.active_timeline) + 1,
            "current_qber": metrics.measured_qber,
            "alert": (metrics.security_state == SecurityState.SUSPICIOUS),
            "state": metrics.security_state.value
        })
        st.session_state.history.append(st.session_state.current_run)

if compare_sim:
    with st.spinner("Executing comparative simulation runs (Normal vs Attacked)..."):
        # 1. Normal run
        cfg_normal = SimulationConfig(
            num_qubits=qubit_choice,
            enable_eve=False,
            enable_noise=enable_noise,
            noise_probability=noise_probability,
            qber_threshold=qber_threshold,
            sample_fraction=sample_fraction,
            random_seed=42
        )
        m_normal, k_normal, r_normal = BB84SimulationEngine(cfg_normal).run_full_simulation()
        st.session_state.normal_comparison_run = m_normal.model_dump()

        # 2. Attacked run
        cfg_attack = SimulationConfig(
            num_qubits=qubit_choice,
            enable_eve=True,
            eve_interception_prob=1.0,
            enable_noise=enable_noise,
            noise_probability=noise_probability,
            qber_threshold=qber_threshold,
            sample_fraction=sample_fraction,
            random_seed=42
        )
        m_attack, k_attack, r_attack = BB84SimulationEngine(cfg_attack).run_full_simulation()
        st.session_state.attack_comparison_run = m_attack.model_dump()


# =====================================================================
# HEADER
# =====================================================================
st.markdown(
    f"""
    <div class="quantum-header">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                <h1 class="quantum-title">QUANTUMSHIELD</h1>
                <div class="quantum-subtitle">BB84 Quantum Key Distribution & Real-Time Eavesdropping Attack Detection</div>
            </div>
            <div style="text-align: right; margin-top: 8px;">
                <span style="background: rgba(124, 58, 237, 0.2); border: 1px solid #7C3AED; color: #C4B5FD; padding: 4px 10px; border-radius: 6px; font-size: 0.8rem;">
                    Backend: Qiskit 2.6.0
                </span>
                <span style="background: rgba(6, 182, 212, 0.2); border: 1px solid #06B6D4; color: #67E8F9; padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; margin-left: 6px;">
                    Simulator: {backend_info['simulator_name']}
                </span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# =====================================================================
# DEFAULT RUN INITIALIZATION IF EMPTY
# =====================================================================
if st.session_state.current_run is None:
    # Run default baseline simulation on launch
    default_config = SimulationConfig(
        num_qubits=qubit_choice,
        enable_eve=enable_eve,
        eve_interception_prob=eve_interception_prob,
        qber_threshold=qber_threshold,
        sample_fraction=sample_fraction
    )
    engine = BB84SimulationEngine(default_config)
    m, k, r = engine.run_full_simulation()
    st.session_state.current_run = {
        "config": default_config,
        "metrics": m,
        "keys": k,
        "records": r,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }
    st.session_state.active_timeline.append({
        "batch_index": 1,
        "current_qber": m.measured_qber,
        "alert": (m.security_state == SecurityState.SUSPICIOUS),
        "state": m.security_state.value
    })


run = st.session_state.current_run
metrics = run["metrics"]
keys = run["keys"]
records = run["records"]
config = run["config"]


# =====================================================================
# METRIC CARDS ROW
# =====================================================================
c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Qubits Transmitted</div>
            <div class="metric-value">{metrics.total_qubits:,}</div>
            <div class="metric-sub" style="color: #94A3B8;">Alice → Bob</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Sifted Key Length</div>
            <div class="metric-value">{metrics.sifted_key_length:,}</div>
            <div class="metric-sub" style="color: #38BDF8;">Yield: {(metrics.sifted_key_length / metrics.total_qubits) * 100:.1f}%</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c3:
    qber_color = "#10B981" if metrics.measured_qber <= metrics.threshold else "#EF4444"
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Measured QBER</div>
            <div class="metric-value" style="color: {qber_color};">{metrics.measured_qber:.2f}%</div>
            <div class="metric-sub" style="color: #94A3B8;">Threshold: {metrics.threshold:.1f}%</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c4:
    badge_html = ""
    if metrics.security_state == SecurityState.SECURE:
        badge_html = '<span class="badge-secure">🛡️ SECURE</span>'
    elif metrics.security_state == SecurityState.SUSPICIOUS:
        badge_html = '<span class="badge-suspicious">🚨 SUSPICIOUS</span>'
    else:
        badge_html = '<span class="badge-inconclusive">⚠️ INCONCLUSIVE</span>'

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Security Assessment</div>
            <div style="margin-top: 6px;">{badge_html}</div>
            <div class="metric-sub" style="color: #94A3B8; margin-top: 8px;">Confidence: 95%</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c5:
    eve_color = "#EF4444" if metrics.eve_intercepted_count > 0 else "#64748B"
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Eve Interception Rate</div>
            <div class="metric-value" style="color: {eve_color};">{metrics.eve_interception_rate:.1f}%</div>
            <div class="metric-sub" style="color: #94A3B8;">{metrics.eve_intercepted_count:,} Qubits tapped</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c6:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Candidate Key Length</div>
            <div class="metric-value" style="color: #34D399;">{metrics.candidate_key_length:,}</div>
            <div class="metric-sub" style="color: #94A3B8;">Unrevealed bits</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =====================================================================
# QUANTUM TRANSMISSION VISUAL PIPELINE
# =====================================================================
render_transmission_flow(records, config.enable_eve)


# =====================================================================
# LIVE CHARTS SECTION
# =====================================================================
col_gauge, col_chart, col_donut = st.columns([1.1, 1.8, 1.1])

with col_gauge:
    fig_gauge = create_qber_gauge(
        current_qber=metrics.measured_qber,
        threshold=metrics.threshold,
        ci_low=metrics.qber_confidence_interval_low,
        ci_high=metrics.qber_confidence_interval_high,
        theoretical_qber=metrics.theoretical_expected_qber
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

with col_chart:
    fig_history = create_qber_history_chart(
        timeline=st.session_state.active_timeline,
        threshold=metrics.threshold
    )
    st.plotly_chart(fig_history, use_container_width=True)

with col_donut:
    fig_donut = create_basis_breakdown_chart(
        matching_bases=metrics.matching_bases_count,
        total_qubits=metrics.total_qubits
    )
    st.plotly_chart(fig_donut, use_container_width=True)


# =====================================================================
# NORMAL VS ATTACKED COMPARISON (IF TRIGGERED)
# =====================================================================
if st.session_state.normal_comparison_run and st.session_state.attack_comparison_run:
    st.markdown("### ⚖️ Side-by-Side Experiment Comparison: Normal vs Attacked")
    fig_comp = create_normal_vs_attack_comparison_chart(
        normal_metrics=st.session_state.normal_comparison_run,
        attack_metrics=st.session_state.attack_comparison_run
    )
    st.plotly_chart(fig_comp, use_container_width=True)


# =====================================================================
# TABS: KEY MATERIAL, INSPECTION, ANALYSIS & EXPORT
# =====================================================================
tab_keys, tab_table, tab_analysis, tab_export = st.tabs([
    "🔑 Cryptographic Keys",
    "🔬 Transmission Records",
    "📊 Statistical Analysis & Threat Model",
    "💾 Export Experiment Data"
])

with tab_keys:
    render_key_material_panel(keys, metrics.security_state.value)

with tab_table:
    render_transmission_table(records, limit=100)

with tab_analysis:
    st.markdown("### 📐 Theoretical & Statistical Bounds")
    
    st.markdown(
        f"""
        - **Empirical Measured QBER**: `{metrics.measured_qber:.2f}%`
        - **Theoretical Expected QBER**: `{metrics.theoretical_expected_qber:.2f}%`
        - **Wilson Score 95% Confidence Interval**: `[{metrics.qber_confidence_interval_low:.2f}%, {metrics.qber_confidence_interval_high:.2f}%]`
        - **Configured Security Threshold**: `{metrics.threshold:.2f}%` (Shor-Preskill asymptotic proof limit: 11.0%)
        """
    )
    
    st.markdown(
        f"""
        <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid #334155; border-radius: 8px; padding: 16px; margin: 12px 0;">
            <div style="font-weight: 700; color: #38BDF8; margin-bottom: 6px;">Evaluation Rationale:</div>
            <div style="color: #E2E8F0; font-size: 0.9rem;">{metrics.security_assessment}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("#### 🛡️ Cybersecurity Threat Model & Assumptions")
    st.markdown(
        """
        - **No-Cloning Theorem**: In quantum mechanics, an unknown quantum state cannot be cloned identically. When Eve measures single photons in the wrong basis (which happens 50% of the time), she irreparably collapses the wavefunction, inducing a 25% error rate on matching bases.
        - **Low QBER Caveat**: As emphasized in quantum cybersecurity research, a measured QBER below 11% does **not** prove total security. Adversaries could perform beam-splitting attacks on multi-photon pulses or exploit detector side channels.
        - **Finite Key Correction**: In finite-key regimes (e.g. 100 to 5,000 qubits), statistical fluctuations necessitate Wilson confidence intervals to prevent false-negative attack detection.
        """
    )

with tab_export:
    st.markdown("### 💾 Export Simulation Results")
    st.markdown("Download full qubit-by-qubit datasets and metrics for external analysis or verification.")

    col_exp1, col_exp2 = st.columns(2)

    # Export JSON
    json_export = {
        "simulation_timestamp": datetime.now().isoformat(),
        "config": config.model_dump(),
        "metrics": metrics.model_dump(),
        "keys": keys.model_dump(),
        "total_records": len(records),
        "records": [r.model_dump() for r in records]
    }
    json_str = json.dumps(json_export, indent=2)

    col_exp1.download_button(
        label="📥 Download Complete Experiment (JSON)",
        data=json_str,
        file_name=f"quantumshield_qkd_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        use_container_width=True
    )

    # Export CSV
    csv_output = io.StringIO()
    writer = csv.writer(csv_output)
    writer.writerow([
        "index", "alice_bit", "alice_basis", "alice_state",
        "eve_intercepted", "eve_basis", "eve_measured", "eve_resent_state",
        "bob_basis", "bob_measured", "basis_matched", "sifted_match",
        "in_parameter_estimation", "in_candidate_key"
    ])
    for r in records:
        writer.writerow([
            r.index, r.alice_bit, r.alice_basis, r.alice_state,
            r.eve_intercepted, r.eve_basis or "", r.eve_measured if r.eve_measured is not None else "",
            r.eve_resent_state or "", r.bob_basis, r.bob_measured,
            r.basis_matched, r.sifted_match if r.sifted_match is not None else "",
            r.in_parameter_estimation, r.in_candidate_key
        ])
    csv_str = csv_output.getvalue()

    col_exp2.download_button(
        label="📥 Download Qubit Records (CSV)",
        data=csv_str,
        file_name=f"quantumshield_qubits_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )
