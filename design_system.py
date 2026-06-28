import streamlit as st

def inject_design_system():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@500;700&display=swap');

    :root {
        --color-primary: #5757f8;
        --color-primary-light: #5757f8;
        --color-secondary: #5757f8;
        --color-cta: #5757f8;
        --color-success: #10B981;
        --color-background: #f5f5f5;
        --color-surface: #ffffff;
        --color-border: #202020;
        --color-text: #202020;
        --color-text-body: #202020;
        --color-text-muted: #333333;
        --shadow-card: none;
        --shadow-hover: none;
        --radius-md: 8px;
        --radius-lg: 8px;
        --font-sans: 'Inter', ui-sans-serif, system-ui, sans-serif;
        --font-display: 'Space Grotesk', ui-sans-serif, system-ui, sans-serif;
    }

    .stApp {
        background-color: var(--color-background) !important;
        font-family: var(--font-sans) !important;
        color: var(--color-text-body) !important;
    }
    .stMain {
        background-color: var(--color-background) !important;
        max-width: 1400px;
        margin: 0 auto;
    }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    h1, h2, h3, h4, h5, h6 {
        font-family: var(--font-sans) !important;
        font-weight: 700 !important;
        color: var(--color-text) !important;
    }
    h1 { font-size: 2rem !important; line-height: 1.2 !important; }
    h2 { font-size: 1.5rem !important; line-height: 1.25 !important; }

    .ds-card, .card {
        background: var(--color-surface) !important;
        border-radius: var(--radius-md) !important;
        padding: 20px !important;
        box-shadow: var(--shadow-card) !important;
        border: 1px solid var(--color-border) !important;
        margin-bottom: 16px !important;
    }
    .ds-card h4, .card h4 {
        color: var(--color-primary) !important;
        margin-top: 0 !important;
        font-weight: 600 !important;
    }

    .ds-section-header {
        background: var(--color-text) !important;
        color: white !important;
        padding: 24px 28px !important;
        border-radius: 8px !important;
        margin: 0 0 24px 0 !important;
        border: 1px solid var(--color-border) !important;
    }
    .ds-section-header h1, .ds-section-header p {
        color: white !important;
        margin: 0 !important;
    }

    .page-hero {
        background: var(--color-surface);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-lg);
        padding: 28px 32px;
        margin-bottom: 24px;
        box-shadow: var(--shadow-card);
    }
    .page-hero h1 {
        font-size: 1.75rem !important;
        margin-bottom: 8px !important;
    }
    .page-hero p {
        color: var(--color-text-muted) !important;
        font-size: 1rem !important;
        margin: 0 !important;
    }

    .empty-canvas {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        min-height: 480px;
        color: var(--color-text-muted);
        border: 2px dashed var(--color-border);
        border-radius: var(--radius-lg);
        background: var(--color-surface);
        padding: 32px;
        text-align: center;
    }
    .empty-canvas h3 {
        color: var(--color-text) !important;
        font-size: 1.25rem !important;
        margin-bottom: 8px !important;
    }

    .stButton > button[kind="primary"], .stButton > button {
        background: var(--color-primary) !important;
        color: white !important;
        border-radius: 8px !important;
        border: 1px solid var(--color-border) !important;
        font-weight: 500 !important;
        font-family: var(--font-sans) !important;
        box-shadow: none !important;
    }
    .stButton > button:hover {
        opacity: 0.9 !important;
        transform: none !important;
        box-shadow: none !important;
    }

    .stTextInput input, .stSelectbox > div > div, textarea {
        border-radius: 8px !important;
        border: 1px solid var(--color-border) !important;
        font-family: var(--font-sans) !important;
    }
    .stFileUploader > div {
        border-radius: var(--radius-md) !important;
        border: 2px dashed var(--color-primary-light) !important;
        background: var(--color-surface) !important;
    }

    .stSidebar, [data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {
        background-color: var(--color-surface) !important;
        border-right: 1px solid var(--color-border) !important;
    }

    .metric-value {
        color: var(--color-primary) !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    .metric-label {
        color: var(--color-text-muted) !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
    }

    .sidebar-section {
        background: var(--color-surface-muted, #f1f5f9);
        border-radius: var(--radius-sm, 8px);
        padding: 10px 12px;
        margin-bottom: 8px;
        font-size: 0.875rem;
        border: 1px solid var(--color-border);
    }

    .footer {
        text-align: center;
        padding: 24px;
        color: var(--color-text-muted);
        font-size: 0.875rem;
    }

    iframe[title="magic_hub.magic_hub"] {
        width: 100% !important;
        border: none !important;
        display: block !important;
        overflow: hidden !important;
    }
    div[data-testid="stCustomComponentV1"] {
        overflow: hidden !important;
    }
    .stMainBlockContainer {
        padding-top: 1rem !important;
        max-width: 1400px !important;
    }

    @media (prefers-reduced-motion: reduce) {
        * { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
    }
    </style>
    """, unsafe_allow_html=True)
