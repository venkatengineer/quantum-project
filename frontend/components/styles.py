"""
QuantumShield Cyber Dashboard Styling
Custom dark cybersecurity theme with near-black background, deep violet and electric blue accents,
emerald green for secure status, amber for warning, and crimson for attack detection.
"""

DARK_THEME_CSS = """
<style>
    /* Global Background & Font */
    .stApp {
        background-color: #07090E;
        color: #E2E8F0;
        font-family: 'JetBrains Mono', 'Fira Code', 'Segoe UI', monospace;
    }
    
    /* Top Header Bar */
    .quantum-header {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(124, 58, 237, 0.3);
        border-radius: 12px;
        padding: 24px 30px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(8px);
    }
    .quantum-title {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        background: linear-gradient(90deg, #A78BFA 0%, #38BDF8 50%, #818CF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .quantum-subtitle {
        color: #94A3B8;
        font-size: 0.95rem;
        margin-top: 6px;
        letter-spacing: 0.5px;
    }

    /* Metric Cards Grid */
    .metric-card {
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid rgba(51, 65, 85, 0.7);
        border-radius: 10px;
        padding: 16px 20px;
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.6);
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.15);
    }
    .metric-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #64748B;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.65rem;
        font-weight: 700;
        color: #F8FAFC;
    }
    .metric-sub {
        font-size: 0.75rem;
        margin-top: 4px;
    }

    /* Status Badges */
    .badge-secure {
        background: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.4);
        border-radius: 6px;
        padding: 4px 12px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .badge-suspicious {
        background: rgba(239, 68, 68, 0.15);
        color: #EF4444;
        border: 1px solid rgba(239, 68, 68, 0.5);
        border-radius: 6px;
        padding: 4px 12px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        animation: pulse-red 2s infinite;
    }
    .badge-inconclusive {
        background: rgba(245, 158, 11, 0.15);
        color: #F59E0B;
        border: 1px solid rgba(245, 158, 11, 0.4);
        border-radius: 6px;
        padding: 4px 12px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    @keyframes pulse-red {
        0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
        70% { box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); }
        100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }

    /* Channel Flow Diagram Container */
    .channel-container {
        background: rgba(15, 23, 42, 0.5);
        border: 1px solid rgba(51, 65, 85, 0.6);
        border-radius: 12px;
        padding: 20px;
        margin: 20px 0;
    }

    /* Key Display Box */
    .key-box {
        background: #030712;
        border: 1px solid #1F2937;
        border-radius: 8px;
        padding: 12px 16px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        word-break: break-all;
        color: #38BDF8;
        max-height: 120px;
        overflow-y: auto;
    }
    .key-box-candidate {
        color: #34D399;
        border-color: rgba(52, 211, 153, 0.3);
    }
    .key-box-aborted {
        color: #F87171;
        border-color: rgba(248, 113, 113, 0.3);
        background: rgba(239, 68, 68, 0.05);
    }

    /* Alert Banner */
    .alert-banner-attack {
        background: linear-gradient(90deg, rgba(239, 68, 68, 0.2) 0%, rgba(185, 28, 28, 0.1) 100%);
        border-left: 4px solid #EF4444;
        padding: 16px 20px;
        border-radius: 4px 8px 8px 4px;
        margin: 16px 0;
    }
    .alert-banner-secure {
        background: linear-gradient(90deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.05) 100%);
        border-left: 4px solid #10B981;
        padding: 16px 20px;
        border-radius: 4px 8px 8px 4px;
        margin: 16px 0;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #0F172A;
        padding: 6px;
        border-radius: 8px;
        border: 1px solid #1E293B;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        color: #94A3B8;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E293B !important;
        color: #38BDF8 !important;
        font-weight: 600;
    }
</style>
"""
