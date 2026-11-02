"""
Plotly Visualizations for QuantumShield
Renders real-time quantum communication charts, QBER monitoring, and attack comparisons.
"""

import plotly.graph_objects as go
import plotly.express as px
from typing import List, Optional, Dict, Any


def create_qber_gauge(
    current_qber: float,
    threshold: float,
    ci_low: float,
    ci_high: float,
    theoretical_qber: float
) -> go.Figure:
    """Creates a sleek cybersecurity radial gauge for QBER with threshold bands."""
    bar_color = "#10B981" if current_qber <= threshold else "#EF4444"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=current_qber,
        delta={
            "reference": threshold,
            "increasing": {"color": "#EF4444"},
            "decreasing": {"color": "#10B981"}
        },
        number={"suffix": "%", "font": {"size": 40, "color": "#F8FAFC"}},
        title={"text": "MEASURED QBER (ERROR RATE)", "font": {"size": 13, "color": "#94A3B8"}},
        gauge={
            "axis": {"range": [0, 50], "tickwidth": 1, "tickcolor": "#475569"},
            "bar": {"color": bar_color, "thickness": 0.3},
            "bgcolor": "#0F172A",
            "borderwidth": 1,
            "bordercolor": "#334155",
            "steps": [
                {"range": [0, threshold], "color": "rgba(16, 185, 129, 0.15)"},
                {"range": [threshold, 50], "color": "rgba(239, 68, 68, 0.20)"}
            ],
            "threshold": {
                "line": {"color": "#F59E0B", "width": 3},
                "thickness": 0.8,
                "value": threshold
            }
        }
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=30, r=30, t=40, b=20),
        height=240,
        font=dict(family="JetBrains Mono, monospace")
    )
    return fig


def create_qber_history_chart(
    timeline: List[Any],
    threshold: float
) -> go.Figure:
    """Line chart tracking QBER over simulation batches with alert threshold line."""
    if not timeline:
        fig = go.Figure()
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            title="Awaiting simulation batches...",
            font=dict(color="#64748B")
        )
        return fig

    batch_indices = [e.batch_index if hasattr(e, "batch_index") else e.get("batch_index", 0) for e in timeline]
    qbers = [e.current_qber if hasattr(e, "current_qber") else e.get("current_qber", 0.0) for e in timeline]
    alerts = [e.alert if hasattr(e, "alert") else e.get("alert", False) for e in timeline]

    colors = ["#EF4444" if a else "#10B981" for a in alerts]

    fig = go.Figure()

    # Threshold horizontal line
    fig.add_hline(
        y=threshold,
        line_dash="dash",
        line_color="#F59E0B",
        annotation_text=f"Security Threshold ({threshold}%)",
        annotation_position="top left",
        annotation_font_color="#F59E0B"
    )

    # QBER trace
    fig.add_trace(go.Scatter(
        x=batch_indices,
        y=qbers,
        mode="lines+markers",
        name="Batch QBER",
        line=dict(color="#38BDF8", width=2.5),
        marker=dict(size=8, color=colors, line=dict(width=1.5, color="#0F172A")),
        hovertemplate="Batch %{x}<br>QBER: %{y:.2f}%<extra></extra>"
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 23, 42, 0.6)",
        title=dict(text="Real-Time QBER Batch Progression", font=dict(color="#E2E8F0", size=14)),
        xaxis=dict(
            title="Batch Sequence",
            gridcolor="#1E293B",
            color="#94A3B8"
        ),
        yaxis=dict(
            title="Measured QBER (%)",
            range=[0, max(35, max(qbers, default=15) + 5)],
            gridcolor="#1E293B",
            color="#94A3B8"
        ),
        margin=dict(l=40, r=20, t=40, b=40),
        height=260,
        font=dict(family="JetBrains Mono, monospace")
    )
    return fig


def create_normal_vs_attack_comparison_chart(
    normal_metrics: Dict[str, Any],
    attack_metrics: Dict[str, Any]
) -> go.Figure:
    """Grouped bar chart comparing key metrics between normal and attacked communication."""
    categories = [
        "Measured QBER (%)",
        "Theoretical QBER (%)",
        "Eve Intercept Rate (%)",
        "Sifted Errors (count)",
        "Candidate Key Length"
    ]

    normal_vals = [
        normal_metrics.get("measured_qber", 0.0),
        normal_metrics.get("theoretical_expected_qber", 0.0),
        normal_metrics.get("eve_interception_rate", 0.0),
        normal_metrics.get("sifted_errors", 0),
        normal_metrics.get("candidate_key_length", 0)
    ]

    attack_vals = [
        attack_metrics.get("measured_qber", 0.0),
        attack_metrics.get("theoretical_expected_qber", 25.0),
        attack_metrics.get("eve_interception_rate", 100.0),
        attack_metrics.get("sifted_errors", 0),
        attack_metrics.get("candidate_key_length", 0)
    ]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Normal (No Attack)",
        x=categories,
        y=normal_vals,
        marker_color="#10B981",
        text=[f"{v:.1f}" if isinstance(v, float) else str(v) for v in normal_vals],
        textposition="auto"
    ))

    fig.add_trace(go.Bar(
        name="Attacked (Intercept-Resend)",
        x=categories,
        y=attack_vals,
        marker_color="#EF4444",
        text=[f"{v:.1f}" if isinstance(v, float) else str(v) for v in attack_vals],
        textposition="auto"
    ))

    fig.update_layout(
        barmode="group",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 23, 42, 0.6)",
        title=dict(text="Empirical Security Comparison: Normal vs Attacked", font=dict(color="#E2E8F0", size=14)),
        xaxis=dict(color="#94A3B8", gridcolor="#1E293B"),
        yaxis=dict(color="#94A3B8", gridcolor="#1E293B"),
        legend=dict(font=dict(color="#E2E8F0")),
        margin=dict(l=40, r=20, t=50, b=40),
        height=320,
        font=dict(family="JetBrains Mono, monospace")
    )
    return fig


def create_basis_breakdown_chart(matching_bases: int, total_qubits: int) -> go.Figure:
    """Donut chart illustrating basis matching and sifting efficiency."""
    mismatched = max(0, total_qubits - matching_bases)
    labels = ["Matching Bases (Sifted)", "Mismatched Bases (Discarded)"]
    values = [matching_bases, mismatched]
    colors = ["#38BDF8", "#334155"]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        marker=dict(colors=colors, line=dict(color="#0F172A", width=2)),
        textinfo="percent+label",
        hoverinfo="label+value+percent",
        textfont=dict(color="#F8FAFC", size=12)
    ))

    fig.update_layout(
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title=dict(text="Basis Reconciliation Sifting Yield", font=dict(color="#E2E8F0", size=14)),
        margin=dict(l=20, r=20, t=40, b=20),
        height=240,
        font=dict(family="JetBrains Mono, monospace")
    )
    return fig
