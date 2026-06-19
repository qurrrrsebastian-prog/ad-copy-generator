"""Sage Mint theme for Personal Finance Tracker (Streamlit).

Provides CSS injection (Inter type system, glassmorphism, mint accents),
responsive rules, a loading skeleton shimmer, and Rupiah formatting.

Typography scale (Inter):
    Hero title   34px / 800   Section header 19px / 600
    KPI value    28px / 700   KPI label      13px / 500 (uppercase)
    Body         15px / 400   Caption        13px / 400
    Button       14px / 600   Tab            14px / 500 (active 600)

Author: Avatar Putra Sigit
"""
from __future__ import annotations

import streamlit as st

# ── Palette constants (importable for charts) ────────────────────────────────
MINT = "#2dd4bf"
TEAL_600 = "#0d9488"
CREAM = "#fef3c7"
TEXT_PRIMARY = "#f0fdfa"
TEXT_SECONDARY = "#99f6e4"
INCOME = "#34d399"
EXPENSE = "#f87171"
BALANCE = "#2dd4bf"
ORANGE = "#fbbf24"
CHART_PALETTE = ["#34d399", "#f87171", "#2dd4bf", "#fbbf24", "#a78bfa"]


# ── Rupiah formatting ────────────────────────────────────────────────────────
def format_rupiah(amount) -> str:
    """Format a number as Indonesian Rupiah, e.g. ``Rp 1.000.000``.

    Negative values render as ``-Rp 1.000.000``. Non-numeric input -> ``Rp 0``.
    """
    try:
        value = float(amount)
    except (TypeError, ValueError):
        return "Rp 0"
    sign = "-" if value < 0 else ""
    whole = int(round(abs(value)))
    return f"{sign}Rp {whole:,.0f}".replace(",", ".")


# ── Theme CSS ────────────────────────────────────────────────────────────────
def inject_phase2_mint_theme() -> None:
    """Inject the full Sage Mint CSS theme (Inter type system) into the page."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        /* ═══ Base / background ═══════════════════════════════════════════ */
        html, body, .stApp, [class*="css"] {
            font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif;
        }
        .stApp {
            background: linear-gradient(135deg, #042f2e 0%, #134e4a 50%, #115e59 100%);
            background-attachment: fixed;
            color: #f0fdfa;
        }
        .main .block-container {
            padding-top: 2.2rem;
            padding-bottom: 4rem;
            max-width: 1280px;
        }

        /* ═══ Typography — clear weight hierarchy ═════════════════════════ */
        /* Base body text: normal weight, comfortable reading. */
        .stApp, p, span, li, .stMarkdown, [data-testid="stMarkdownContainer"] p {
            font-weight: 400;
            font-size: 15px;
            line-height: 1.6;
            color: #f0fdfa;
        }
        /* Hero title (h1): heaviest. */
        .stApp h1 {
            font-weight: 800;
            font-size: 34px;
            letter-spacing: -0.022em;
            line-height: 1.15;
            color: #f0fdfa !important;
            margin-bottom: 0.15rem;
        }
        /* Section headers (h2). */
        .stApp h2 {
            font-weight: 600;
            font-size: 21px;
            letter-spacing: -0.01em;
            color: #f0fdfa !important;
        }
        /* Sub-section headers (h3 / st.subheader). */
        .stApp h3 {
            font-weight: 600;
            font-size: 18px;
            letter-spacing: -0.005em;
            color: #f0fdfa !important;
        }
        .stApp h4 { font-weight: 600; font-size: 15px; color: #f0fdfa !important; }
        /* Captions: light, muted. */
        .stCaption, [data-testid="stCaptionContainer"],
        [data-testid="stCaptionContainer"] p {
            color: #99f6e4 !important;
            font-weight: 400 !important;
            font-size: 13px !important;
            line-height: 1.5;
        }
        /* Widget labels: medium weight, never bold. */
        [data-testid="stWidgetLabel"] p, .stTextInput label, .stNumberInput label,
        .stSelectbox label, .stDateInput label {
            font-weight: 500 !important;
            font-size: 13.5px !important;
            color: #ccfbf1 !important;
        }

        /* ═══ Hero header block ═══════════════════════════════════════════ */
        .app-hero { margin: 0 0 0.4rem 0; }
        .app-hero h1 { margin: 0; }
        .app-hero .subtitle {
            color: #99f6e4;
            font-weight: 400;
            font-size: 15px;
            margin-top: 4px;
        }

        /* ═══ Sidebar ═════════════════════════════════════════════════════ */
        [data-testid="stSidebar"] {
            background: rgba(4,47,46,0.82);
            border-right: 1px solid rgba(45,212,191,0.20);
            backdrop-filter: blur(14px);
        }
        [data-testid="stSidebar"] .block-container { padding-top: 1.6rem; }
        [data-testid="stSidebar"] h2 {
            font-weight: 700;
            font-size: 17px;
            letter-spacing: -0.01em;
        }
        [data-testid="stSidebar"] * { color: #f0fdfa; }

        /* ═══ KPI / metric cards ══════════════════════════════════════════ */
        [data-testid="stMetric"] {
            background: rgba(255,255,255,0.055);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(45,212,191,0.22);
            border-left: 4px solid #2dd4bf;
            border-radius: 16px;
            padding: 20px 22px;
            min-height: 118px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.40);
            transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
            animation: fadeInUp 0.5s ease both;
        }
        [data-testid="stMetric"]:hover {
            transform: translateY(-3px);
            border-color: rgba(45,212,191,0.45);
            box-shadow: 0 14px 42px rgba(0,0,0,0.50);
        }
        /* KPI label: medium, uppercase, tracked — distinct from value. */
        [data-testid="stMetricLabel"] p {
            color: #99f6e4 !important;
            font-weight: 500 !important;
            font-size: 12.5px !important;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }
        /* KPI value: bold, tabular figures for clean number alignment. */
        [data-testid="stMetricValue"] {
            color: #f0fdfa !important;
            font-weight: 700 !important;
            font-size: 27px !important;
            letter-spacing: -0.02em;
            font-variant-numeric: tabular-nums;
            font-feature-settings: "tnum";
        }
        [data-testid="stMetricDelta"] { font-weight: 500 !important; font-size: 13px !important; }

        /* ═══ Buttons ═════════════════════════════════════════════════════ */
        .stButton > button {
            border-radius: 10px;
            font-weight: 600;
            font-size: 14px;
            letter-spacing: 0.01em;
            padding: 0.5rem 1rem;
            border: 1px solid rgba(255,255,255,0.20);
            background: rgba(255,255,255,0.10);
            color: #f0fdfa;
            transition: all 0.2s ease;
        }
        .stButton > button:hover {
            border-color: #2dd4bf;
            color: #f0fdfa;
            transform: translateY(-1px);
        }
        .stButton > button[kind="primary"] {
            background: #2dd4bf;
            color: #042f2e !important;
            border: none;
            box-shadow: 0 4px 14px rgba(45,212,191,0.30);
        }
        .stButton > button[kind="primary"]:hover { background: #14b8a6; }
        .stDownloadButton > button { font-weight: 600; border-radius: 10px; }

        /* ═══ Inputs ══════════════════════════════════════════════════════ */
        .stTextInput input, .stNumberInput input, .stDateInput input,
        [data-baseweb="select"] > div {
            background: rgba(255,255,255,0.08) !important;
            border: 1px solid rgba(255,255,255,0.15) !important;
            border-radius: 10px !important;
            color: #f0fdfa !important;
            font-weight: 400 !important;
            font-size: 14px !important;
        }
        .stTextInput input:focus, .stNumberInput input:focus,
        .stDateInput input:focus {
            border-color: #2dd4bf !important;
            box-shadow: 0 0 0 1px #2dd4bf !important;
        }
        input::placeholder { color: #5eead4 !important; opacity: 0.65; font-weight: 400; }

        /* ═══ Tabs (pill style) ═══════════════════════════════════════════ */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: transparent;
            border-bottom: 1px solid rgba(45,212,191,0.25);
            padding-bottom: 4px;
            margin-bottom: 0.5rem;
        }
        .stTabs [data-baseweb="tab"] {
            background: rgba(255,255,255,0.04);
            color: #99f6e4;
            border-radius: 999px;
            padding: 7px 20px;
            font-weight: 500;
            font-size: 14px;
        }
        .stTabs [data-baseweb="tab"]:hover { color: #f0fdfa; }
        .stTabs [aria-selected="true"] {
            background: #2dd4bf !important;
            color: #042f2e !important;
            font-weight: 600 !important;
        }

        /* ═══ Segmented control ═══════════════════════════════════════════ */
        [data-testid="stSegmentedControl"] button { font-weight: 500; }
        [data-testid="stSegmentedControl"] button[aria-checked="true"] {
            background: #2dd4bf !important;
            color: #042f2e !important;
            font-weight: 600 !important;
        }

        /* ═══ DataFrame ═══════════════════════════════════════════════════ */
        [data-testid="stDataFrame"] {
            border: 1px solid rgba(45,212,191,0.22);
            border-radius: 14px;
            overflow: hidden;
        }

        /* ═══ Plotly chart cards ══════════════════════════════════════════ */
        [data-testid="stPlotlyChart"] {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(45,212,191,0.18);
            border-radius: 14px;
            padding: 8px 10px;
        }

        /* ═══ Dividers ════════════════════════════════════════════════════ */
        hr { border-color: rgba(45,212,191,0.25) !important; margin: 1.3rem 0; }

        /* ═══ Toast tint ══════════════════════════════════════════════════ */
        [data-testid="stToast"] {
            background: rgba(4,47,46,0.95);
            border: 1px solid rgba(45,212,191,0.40);
            color: #f0fdfa;
            font-weight: 500;
        }

        /* ═══ Animations ══════════════════════════════════════════════════ */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(12px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes shimmer {
            0%   { background-position: -468px 0; }
            100% { background-position: 468px 0; }
        }
        .fade-in { animation: fadeInUp 0.5s ease both; }

        /* ═══ Custom KPI card helper ══════════════════════════════════════ */
        .kpi-card {
            background: rgba(255,255,255,0.055);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(45,212,191,0.22);
            border-left: 4px solid #2dd4bf;
            border-radius: 16px;
            padding: 20px 22px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.40);
            animation: fadeInUp 0.5s ease both;
        }
        .kpi-card .kpi-label {
            color: #99f6e4; font-weight: 500; font-size: 12.5px;
            text-transform: uppercase; letter-spacing: 0.06em; margin: 0;
        }
        .kpi-card .kpi-value {
            font-size: 27px; font-weight: 700; letter-spacing: -0.02em;
            margin: 6px 0 0; font-variant-numeric: tabular-nums;
        }
        .kpi-card .kpi-delta { font-size: 13px; font-weight: 500; margin: 2px 0 0; }

        /* ═══ Section label (small caps accent) ═══════════════════════════ */
        .section-label {
            color: #5eead4; font-weight: 600; font-size: 12px;
            text-transform: uppercase; letter-spacing: 0.10em; margin: 0 0 2px;
        }

        /* ═══ Empty state ═════════════════════════════════════════════════ */
        .empty-state { text-align: center; padding: 52px 16px; color: #99f6e4; }
        .empty-state .icon { font-size: 56px; }
        .empty-state h3 { font-weight: 700; }
        .empty-state p { font-weight: 400; color: #99f6e4; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_loading_skeleton(rows: int = 3) -> None:
    """Render a mint shimmer skeleton placeholder."""
    bars = "".join(
        '<div style="height:18px;margin:10px 0;border-radius:8px;'
        "background:linear-gradient(90deg, rgba(45,212,191,0.08) 25%, "
        "rgba(45,212,191,0.25) 50%, rgba(45,212,191,0.08) 75%);"
        'background-size:936px 100%;animation:shimmer 1.2s infinite linear;"></div>'
        for _ in range(rows)
    )
    st.markdown(f'<div class="kpi-card">{bars}</div>', unsafe_allow_html=True)


def responsive_css() -> None:
    """Inject mobile/responsive rules (KPI 2x2, full-width form, stacked charts)."""
    st.markdown(
        """
        <style>
        @media (max-width: 768px) {
            .main .block-container { padding: 1rem 0.6rem; }
            .stApp h1 { font-size: 26px; }
            .stApp h2 { font-size: 18px; }
            [data-testid="stMetric"] { padding: 14px 16px; min-height: 104px; }
            [data-testid="stMetricValue"] { font-size: 22px !important; }
            [data-testid="column"] {
                width: 50% !important;
                flex: 1 1 50% !important;
                min-width: 50% !important;
            }
            .stButton > button { width: 100% !important; }
        }
        @media (max-width: 480px) {
            [data-testid="column"] {
                width: 100% !important;
                flex: 1 1 100% !important;
                min-width: 100% !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
