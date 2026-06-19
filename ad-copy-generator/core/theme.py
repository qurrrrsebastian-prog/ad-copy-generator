"""Royal Purple theme + UI helpers for AI Ad Copy Generator. Author: Avatar Putra Sigit

Phase-2 design system: glassmorphism cards, pink (Fuchsia 400) accents,
violet gradient background, KPI cards, pill tabs, and a pink skeleton loader.
"""
import streamlit as st

# Palette --------------------------------------------------------------------
BG_GRADIENT = "linear-gradient(135deg, #2e1065 0%, #4c1d95 50%, #5b21b6 100%)"
PRIMARY = "#8b5cf6"
SECONDARY = "#7c3aed"
ACCENT = "#e879f9"
TEXT_PRIMARY = "#f5f3ff"
TEXT_SECONDARY = "#ddd6fe"
CHART_PALETTE = ["#e879f9", "#a78bfa", "#8b5cf6", "#c084fc", "#ddd6fe"]


def style_chart(chart):
    """Apply dark-theme-friendly styling to an Altair chart (light labels,
    transparent background, subtle grid) so it reads on the purple cards."""
    return (
        chart.configure(background="transparent")
        .configure_view(strokeWidth=0)
        .configure_axis(
            labelColor=TEXT_SECONDARY,
            titleColor=TEXT_SECONDARY,
            gridColor="rgba(232,121,249,0.15)",
            domainColor="rgba(232,121,249,0.3)",
            tickColor="rgba(232,121,249,0.3)",
        )
        .configure_legend(labelColor=TEXT_SECONDARY, titleColor=TEXT_PRIMARY)
    )


def inject_phase2_purple_theme() -> None:
    """Inject the full Royal Purple CSS theme."""
    st.markdown(
        f"""
        <style>
        /* ---- Base background + typography ---- */
        .stApp {{
            background: {BG_GRADIENT};
            background-attachment: fixed;
            color: {TEXT_PRIMARY};
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }}
        /* Transparent toolbar so it never sits as a solid bar over content */
        [data-testid="stHeader"] {{ background: transparent !important; }}
        [data-testid="stToolbar"] {{ right: 1rem; }}
        .block-container {{
            padding-top: 3.5rem;
            padding-bottom: 4rem;
            max-width: 1200px;
        }}
        h1, h2, h3, h4, h5 {{ color: {TEXT_PRIMARY} !important; font-weight: 600; }}
        h1 {{ font-size: 32px !important; font-weight: 700 !important; margin-bottom: 0.2rem !important; }}
        h2 {{ font-size: 22px !important; }}
        h5 {{ font-size: 15px !important; font-weight: 600 !important; margin: 0.2rem 0 0.4rem 0 !important; }}
        p, span, label, .stMarkdown {{ color: {TEXT_SECONDARY}; }}
        .stCaption, [data-testid="stCaptionContainer"] {{ color: {TEXT_SECONDARY} !important; }}

        /* ---- Sidebar ---- */
        [data-testid="stSidebar"] {{
            background: rgba(46,16,101,0.8);
            backdrop-filter: blur(12px);
            border-right: 1px solid rgba(232,121,249,0.2);
        }}
        [data-testid="stSidebar"] * {{ color: {TEXT_PRIMARY}; }}

        /* ---- Glassmorphism cards ---- */
        .glass-card {{
            background: rgba(255,255,255,0.06);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(232,121,249,0.25);
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.4);
            margin-bottom: 16px;
        }}

        /* ---- KPI cards (equal height, tidy alignment) ---- */
        .kpi-card {{
            background: rgba(255,255,255,0.06);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(232,121,249,0.25);
            border-left: 4px solid {ACCENT};
            border-radius: 16px;
            padding: 16px 18px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.4);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            animation: fadeIn 0.6s ease both;
            min-height: 118px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 2px;
        }}
        .kpi-card:hover {{
            transform: scale(1.02);
            box-shadow: 0 12px 40px rgba(232,121,249,0.25);
        }}
        .kpi-icon {{ font-size: 24px; line-height: 1; }}
        .kpi-value {{
            font-size: 26px; font-weight: 700; color: {TEXT_PRIMARY};
            margin: 2px 0 0 0; line-height: 1.15;
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        }}
        .kpi-label {{ font-size: 13px; color: {TEXT_SECONDARY}; }}

        /* ---- Bordered containers rendered as glass "copy" cards ---- */
        [data-testid="stVerticalBlockBorderWrapper"] {{
            background: rgba(232,121,249,0.10);
            border: 1px solid rgba(232,121,249,0.25) !important;
            border-left: 4px solid {ACCENT} !important;
            border-radius: 14px !important;
            box-shadow: 0 8px 32px rgba(0,0,0,0.35);
        }}
        .copy-headline {{ font-size: 20px; font-weight: 700; color: {TEXT_PRIMARY}; }}

        /* ---- Inputs ---- */
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {{
            background: rgba(255,255,255,0.08) !important;
            border: 1px solid rgba(255,255,255,0.15) !important;
            border-radius: 10px !important;
            color: {TEXT_PRIMARY} !important;
        }}
        .stTextInput input:focus, .stTextArea textarea:focus {{
            border-color: {ACCENT} !important;
            box-shadow: 0 0 0 1px {ACCENT} !important;
        }}
        .stTextInput input::placeholder, .stTextArea textarea::placeholder {{ color: #a78bfa !important; }}

        /* ---- Buttons ---- */
        .stButton > button {{
            border-radius: 10px;
            font-weight: 600;
            border: 1px solid rgba(255,255,255,0.2);
            background: rgba(255,255,255,0.1);
            color: {TEXT_PRIMARY};
            transition: all 0.2s ease;
        }}
        .stButton > button:hover {{ border-color: {ACCENT}; transform: translateY(-1px); }}
        .stButton > button[kind="primary"] {{
            background: {ACCENT};
            color: #2e1065;
            border: none;
        }}
        .stButton > button[kind="primary"]:hover {{ background: #d946ef; color: #2e1065; }}

        /* ---- Tabs (pill-style) ---- */
        .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
        .stTabs [data-baseweb="tab"] {{
            background: transparent;
            color: {TEXT_SECONDARY};
            border-radius: 999px;
            padding: 6px 18px;
        }}
        .stTabs [aria-selected="true"] {{
            background: {ACCENT} !important;
            color: #2e1065 !important;
            font-weight: 600;
        }}

        /* ---- Segmented control ---- */
        [data-testid="stSegmentedControl"] button[aria-checked="true"] {{
            background: {ACCENT} !important;
            color: #2e1065 !important;
        }}

        /* ---- Tables ---- */
        .stDataFrame thead tr th {{ background: rgba(232,121,249,0.15) !important; color: {TEXT_PRIMARY} !important; }}
        .stDataFrame tbody tr:hover {{ background: rgba(255,255,255,0.05) !important; }}

        /* ---- Divider ---- */
        hr {{ border-color: rgba(232,121,249,0.3) !important; }}

        /* ---- Progress bar ---- */
        .stProgress > div > div > div > div {{ background: {ACCENT}; }}

        /* ---- Skeleton shimmer ---- */
        .skeleton {{
            height: 18px;
            border-radius: 8px;
            margin: 10px 0;
            background: linear-gradient(90deg,
                rgba(232,121,249,0.15) 25%,
                rgba(232,121,249,0.35) 50%,
                rgba(232,121,249,0.15) 75%);
            background-size: 200% 100%;
            animation: shimmer 1.2s infinite;
        }}
        .skeleton.short {{ width: 45%; }}
        .skeleton.medium {{ width: 70%; }}

        /* ---- Animations ---- */
        @keyframes shimmer {{ 0% {{ background-position: 200% 0; }} 100% {{ background-position: -200% 0; }} }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(icon: str, value, label: str) -> None:
    """Render a single glassmorphism KPI card."""
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_loading_skeleton() -> None:
    """Render a pink shimmer skeleton (3 pulses) for the generating state."""
    st.markdown(
        """
        <div class="glass-card">
            <div class="skeleton short"></div>
            <div class="skeleton"></div>
            <div class="skeleton medium"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def responsive_css() -> None:
    """Mobile media query: collapse sidebar feel, full-width form."""
    st.markdown(
        """
        <style>
        @media (max-width: 768px) {
            .block-container { padding: 1rem 0.5rem !important; }
            .kpi-card { margin-bottom: 12px; }
            h1 { font-size: 26px !important; }
            .stButton > button { width: 100% !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def copy_to_clipboard_js(text: str) -> None:
    """Render a code block (with Streamlit's built-in copy icon) for easy copy."""
    st.code(text, language=None)
