"""Aqua Marine theme: CSS injection, loading skeleton, responsive & badge styles.

Author: Avatar Putra Sigit
"""
from __future__ import annotations

import streamlit as st

# ---------------------------------------------------------------------------
# Palette (Aqua Marine)
# ---------------------------------------------------------------------------
BG_GRADIENT = "linear-gradient(135deg, #083344 0%, #164e63 50%, #155e75 100%)"
PRIMARY = "#06b6d4"
SECONDARY = "#0891b2"
ACCENT = "#67e8f9"
TEXT_PRIMARY = "#ecfeff"
TEXT_SECONDARY = "#a5f3fc"
CARD_BG = "rgba(255,255,255,0.06)"
CARD_BORDER = "rgba(103,232,249,0.25)"

# Plotly chart palette
CHART_PALETTE = ["#06b6d4", "#67e8f9", "#22d3ee", "#a5f3fc", "#ecfeff"]
STATUS_COLORS = {"Safe": "#34d399", "Alert": "#fbbf24", "Critical": "#f87171"}


def inject_phase2_aqua_theme() -> None:
    """Inject the global Aqua Marine CSS."""
    st.markdown(
        f"""
        <style>
        /* ---- App background ---- */
        .stApp {{
            background: {BG_GRADIENT};
            background-attachment: fixed;
            color: {TEXT_PRIMARY};
            font-family: 'Segoe UI', system-ui, sans-serif;
        }}
        .block-container {{ padding-top: 2rem; }}

        h1 {{ color: {TEXT_PRIMARY}; font-size: 32px; font-weight: 700; }}
        h2 {{ color: {TEXT_PRIMARY}; font-size: 22px; font-weight: 600; }}
        h3 {{ color: {TEXT_SECONDARY}; }}
        p, label, .stMarkdown {{ color: {TEXT_PRIMARY}; font-size: 16px; }}
        .stCaption, .caption {{ color: {TEXT_SECONDARY}; font-size: 14px; }}

        /* ---- Sidebar ---- */
        section[data-testid="stSidebar"] {{
            background: rgba(8,51,68,0.85);
            border-right: 1px solid rgba(6,182,212,0.2);
        }}
        section[data-testid="stSidebar"] * {{ color: {TEXT_PRIMARY}; }}

        /* ---- Glassmorphism cards ---- */
        .aqua-card {{
            background: {CARD_BG};
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid {CARD_BORDER};
            border-radius: 16px;
            border-left: 4px solid {PRIMARY};
            padding: 18px 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.4);
            animation: fadeIn 0.6s ease both;
        }}
        .aqua-card .kpi-icon {{ font-size: 24px; }}
        .aqua-card .kpi-label {{ color: {TEXT_SECONDARY}; font-size: 14px; margin: 2px 0; }}
        .aqua-card .kpi-value {{ color: {TEXT_PRIMARY}; font-size: 28px; font-weight: 700; }}

        /* status dot */
        .status-dot {{
            display: inline-block; width: 12px; height: 12px;
            border-radius: 50%; margin-left: 6px; vertical-align: middle;
        }}
        .dot-green {{ background: #34d399; box-shadow: 0 0 8px #34d399; }}
        .dot-orange {{ background: #fbbf24; box-shadow: 0 0 8px #fbbf24; }}
        .dot-red {{ background: #f87171; box-shadow: 0 0 8px #f87171; animation: blink 1s infinite; }}

        /* ---- Buttons ---- */
        .stButton > button {{
            background: {PRIMARY}; color: #083344; font-weight: 600;
            border: none; border-radius: 10px;
        }}
        .stButton > button:hover {{ background: {SECONDARY}; color: #083344; }}
        .stDownloadButton > button {{
            background: rgba(255,255,255,0.1); color: {TEXT_PRIMARY};
            border: 1px solid rgba(255,255,255,0.2); border-radius: 10px;
        }}

        /* ---- Tabs (pill style) ---- */
        .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
        .stTabs [data-baseweb="tab"] {{
            background: transparent; color: {TEXT_SECONDARY};
            border-radius: 999px; padding: 6px 18px; border: 1px solid {CARD_BORDER};
        }}
        .stTabs [aria-selected="true"] {{
            background: {PRIMARY} !important; color: #083344 !important;
            font-weight: 600;
        }}

        /* ---- Dataframe ---- */
        [data-testid="stDataFrame"] {{
            border-radius: 8px; overflow: hidden;
            border: 1px solid {CARD_BORDER};
        }}

        /* ---- Metric ---- */
        [data-testid="stMetricValue"] {{ color: {TEXT_PRIMARY}; }}
        [data-testid="stMetricLabel"] {{ color: {TEXT_SECONDARY}; }}

        /* ---- Divider ---- */
        hr {{ border-color: rgba(6,182,212,0.3); }}

        /* ---- Alert banner ---- */
        .stAlert {{
            border-radius: 12px;
            animation: slideDown 0.5s ease both;
        }}

        /* ---- Animations ---- */
        @keyframes blink {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:0.25; }} }}
        @keyframes fadeIn {{ from {{ opacity:0; transform: translateY(8px); }} to {{ opacity:1; transform:none; }} }}
        @keyframes slideDown {{ from {{ opacity:0; transform: translateY(-12px); }} to {{ opacity:1; transform:none; }} }}
        @keyframes slideUp {{ from {{ opacity:0; transform: translateY(12px); }} to {{ opacity:1; transform:none; }} }}
        @keyframes shimmer {{ 0% {{ background-position:-468px 0; }} 100% {{ background-position:468px 0; }} }}

        .slide-up {{ animation: slideUp 0.6s ease both; }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    status_badge_css()


def status_badge_css() -> None:
    """Pill badge styles for Safe / Alert / Critical (Critical blinks)."""
    st.markdown(
        """
        <style>
        .badge {
            display: inline-block; padding: 3px 12px; border-radius: 999px;
            font-size: 13px; font-weight: 600; color: #083344;
        }
        .badge-safe { background: #34d399; }
        .badge-alert { background: #fbbf24; }
        .badge-critical { background: #f87171; color: #fff; animation: blink 1s infinite; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_loading_skeleton() -> None:
    """Aqua shimmer skeleton placeholder while data loads."""
    st.markdown(
        """
        <style>
        .skeleton {
            height: 90px; border-radius: 16px; margin-bottom: 12px;
            background: linear-gradient(90deg,
                rgba(6,182,212,0.08) 25%,
                rgba(103,232,249,0.25) 50%,
                rgba(6,182,212,0.08) 75%);
            background-size: 936px 100px;
            animation: shimmer 1.4s infinite linear;
        }
        </style>
        <div class="skeleton"></div>
        <div class="skeleton"></div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("💧 Loading water quality data...")


def responsive_css() -> None:
    """Mobile tweaks: 2x2 KPI grid, stacked charts, shorter map, scrollable tabs/table."""
    st.markdown(
        """
        <style>
        /* Tabs scroll horizontally instead of wrapping on small screens. */
        .stTabs [data-baseweb="tab-list"] {
            overflow-x: auto;
            flex-wrap: nowrap;
            scrollbar-width: thin;
        }
        .stTabs [data-baseweb="tab"] { flex: 0 0 auto; }

        @media (max-width: 768px) {
            .block-container { padding: 1rem 0.6rem; }
            h1 { font-size: 24px; line-height: 1.15; }
            h2 { font-size: 19px; }

            /* Stack KPI cards and chart columns full width for readability. */
            [data-testid="stHorizontalBlock"] { flex-wrap: wrap; }
            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
                flex: 1 1 100% !important;
                min-width: 100% !important;
            }
            .aqua-card { padding: 12px 14px; }
            .aqua-card .kpi-value { font-size: 22px; }

            /* Keep the folium map compact on phones. */
            iframe { height: 320px !important; }

            [data-testid="stDataFrame"] { overflow-x: auto; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
