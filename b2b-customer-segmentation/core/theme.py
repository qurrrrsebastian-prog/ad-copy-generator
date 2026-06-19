"""Corporate Light theme (Bintang 5) — CSS injection for Streamlit.

Bright, clean SaaS-dashboard look: professional but with marketing polish.
  bg          #f7f8fb (soft light) with subtle tint
  surface     #ffffff cards, 1px #e6e9ef border, soft shadow
  accent      #4f46e5 (indigo) — modern, marketing-friendly
  text        #0f172a / #64748b
  segments    amber / emerald / orange / red (readable on white, not neon)
"""
import streamlit as st

# Single confident accent + support.
ACCENT = "#4f46e5"          # indigo-600
ACCENT_HOVER = "#4338ca"
ACCENT_SOFT = "#eef2ff"     # indigo-50 tint

# Marketing-friendly but cohesive data palette (indigo-led).
CHART_PALETTE = ["#4f46e5", "#0891b2", "#059669", "#d97706", "#dc2626", "#7c3aed"]
SEGMENT_COLORS = {
    "Champions": "#d97706",   # amber-600 (premium gold)
    "Loyal": "#059669",       # emerald-600
    "At Risk": "#ea580c",     # orange-600
    "Lost": "#dc2626",        # red-600
}

# Shared values for plotly figures (light mode).
PLOTLY_FONT = "#334155"
PLOTLY_GRID = "rgba(15,23,42,0.06)"


def inject_phase2_slate_theme() -> None:
    """Inject the global Corporate Light stylesheet."""
    st.markdown(
        """
        <style>
        /* ---- Base background (soft light) ---- */
        .stApp {
            background: linear-gradient(180deg, #f7f8fb 0%, #eef1f7 100%);
            background-attachment: fixed;
            color: #0f172a;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }
        .block-container { padding-top: 2rem; max-width: 1240px; }

        /* ---- Typography ---- */
        h1 { color: #0f172a !important; font-size: 30px !important; font-weight: 700 !important;
             letter-spacing: -0.02em; }
        h2 { color: #1e293b !important; font-size: 21px !important; font-weight: 600 !important; }
        h3 { color: #334155 !important; font-size: 17px !important; font-weight: 600 !important; }
        p, label, span, .stMarkdown, li { color: #475569; font-size: 15px; }
        .stCaption, [data-testid="stCaptionContainer"] { color: #94a3b8 !important; font-size: 13px; }

        /* ---- Hero title band (marketing polish) ---- */
        .hero {
            background: linear-gradient(120deg, #4f46e5 0%, #6366f1 55%, #7c3aed 100%);
            border-radius: 16px;
            padding: 22px 26px;
            margin-bottom: 18px;
            box-shadow: 0 8px 24px rgba(79,70,229,0.22);
        }
        .hero h1, .hero .hero-sub { color: #ffffff !important; }
        .hero h1 { font-size: 28px; font-weight: 700; margin: 0; letter-spacing: -0.02em; }
        .hero .hero-sub { font-size: 14px; opacity: 0.92; margin-top: 4px; font-weight: 400; }

        /* ---- Cards ---- */
        .glass-card {
            background: #ffffff;
            border: 1px solid #e6e9ef;
            border-radius: 14px;
            padding: 18px 20px;
            box-shadow: 0 1px 3px rgba(15,23,42,0.06), 0 8px 24px rgba(15,23,42,0.04);
            margin-bottom: 10px;
            animation: fadeIn 0.5s ease both;
        }

        /* ---- KPI cards ---- */
        .kpi-card {
            background: #ffffff;
            border: 1px solid #e6e9ef;
            border-radius: 14px;
            padding: 16px 18px;
            box-shadow: 0 1px 3px rgba(15,23,42,0.06), 0 10px 24px rgba(15,23,42,0.04);
            animation: fadeIn 0.5s ease both;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }
        .kpi-card:hover { transform: translateY(-3px); box-shadow: 0 12px 28px rgba(15,23,42,0.10); }
        .kpi-card .kpi-icon {
            font-size: 18px; width: 38px; height: 38px; border-radius: 10px;
            display: flex; align-items: center; justify-content: center; margin-bottom: 10px;
        }
        .kpi-card .kpi-label { color: #64748b; font-size: 12px; margin-top: 4px;
                               text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; }
        .kpi-card .kpi-value { color: #0f172a; font-size: 30px; font-weight: 700; line-height: 1.1; }
        .kpi-champions { border-top: 3px solid #d97706; }
        .kpi-champions .kpi-icon { background: #fef3c7; }
        .kpi-loyal     { border-top: 3px solid #059669; }
        .kpi-loyal .kpi-icon { background: #d1fae5; }
        .kpi-atrisk    { border-top: 3px solid #ea580c; }
        .kpi-atrisk .kpi-icon { background: #ffedd5; }
        .kpi-lost      { border-top: 3px solid #dc2626; }
        .kpi-lost .kpi-icon { background: #fee2e2; }

        /* ---- Sidebar ---- */
        section[data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid #e6e9ef;
        }
        section[data-testid="stSidebar"] * { color: #334155; }
        section[data-testid="stSidebar"] h2 { color: #0f172a; }

        /* ---- Buttons ---- */
        .stButton > button {
            background: #4f46e5;
            color: #ffffff;
            font-weight: 600;
            border: none;
            border-radius: 9px;
            box-shadow: 0 2px 6px rgba(79,70,229,0.25);
            transition: background 0.18s ease, transform 0.1s ease, box-shadow 0.18s ease;
        }
        .stButton > button:hover { background: #4338ca; color: #ffffff; transform: translateY(-1px);
                                   box-shadow: 0 4px 12px rgba(79,70,229,0.32); }
        .stDownloadButton > button {
            background: #ffffff;
            color: #4f46e5;
            border: 1px solid #c7cbf5;
            border-radius: 9px;
            font-weight: 600;
        }
        .stDownloadButton > button:hover { border-color: #4f46e5; background: #eef2ff; }

        /* ---- Tabs: clean underline ---- */
        .stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid #e6e9ef; }
        .stTabs [data-baseweb="tab"] {
            background: transparent; color: #64748b; border-radius: 8px 8px 0 0;
            padding: 8px 16px; border: none; font-weight: 500;
        }
        .stTabs [data-baseweb="tab"]:hover { color: #1e293b; }
        .stTabs [aria-selected="true"] {
            background: #eef2ff !important; color: #4f46e5 !important; font-weight: 600;
            border-bottom: 2px solid #4f46e5 !important;
        }

        /* ---- Inputs ---- */
        .stMultiSelect [data-baseweb="tag"] { background: #eef2ff !important; color: #4f46e5 !important; }
        div[data-baseweb="slider"] [role="slider"] { background: #4f46e5 !important; }

        /* ---- Dividers ---- */
        hr { border-color: #e6e9ef !important; margin: 1.1rem 0; }

        /* ---- Dataframe ---- */
        .stDataFrame { border-radius: 10px; overflow: hidden; border: 1px solid #e6e9ef; }

        /* ---- Progress bar ---- */
        .stProgress > div > div > div > div { background-color: #4f46e5; }

        /* ---- Animations ---- */
        @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes slideIn { from { opacity: 0; transform: translateX(-8px); } to { opacity: 1; transform: translateX(0); } }
        @keyframes shimmer { 0% { background-position: -400px 0; } 100% { background-position: 400px 0; } }
        .slide-in { animation: slideIn 0.45s ease both; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def segment_color_css() -> None:
    """Inject per-segment helper classes (light-mode pills + cards)."""
    st.markdown(
        """
        <style>
        .seg-pill {
            display: inline-block; padding: 2px 11px; border-radius: 999px;
            font-size: 13px; font-weight: 600;
        }
        .seg-champions { background: #fef3c7; color: #92400e; }
        .seg-loyal     { background: #d1fae5; color: #065f46; }
        .seg-atrisk    { background: #ffedd5; color: #9a3412; }
        .seg-lost      { background: #fee2e2; color: #991b1b; }
        .seg-card {
            border-radius: 12px; padding: 14px 16px; margin-bottom: 8px;
            background: #ffffff; border: 1px solid #e6e9ef;
            box-shadow: 0 1px 3px rgba(15,23,42,0.05);
            animation: slideIn 0.45s ease both;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def responsive_css() -> None:
    """Mobile rules: KPI 2x2, stacked charts, horizontal-scroll tables."""
    st.markdown(
        """
        <style>
        @media (max-width: 768px) {
            h1, .hero h1 { font-size: 23px !important; }
            h2 { font-size: 18px !important; }
            .block-container { padding-left: 0.8rem; padding-right: 0.8rem; }
            div[data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
            div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
                flex: 0 0 48% !important; min-width: 48% !important;
            }
            .stDataFrame { overflow-x: auto; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_loading_skeleton() -> None:
    """Render a subtle light shimmer skeleton while clustering runs."""
    st.markdown(
        """
        <style>
        .skeleton-row {
            height: 20px; border-radius: 8px; margin: 8px 0;
            background: linear-gradient(90deg, #eef1f7 25%, #e2e6ee 50%, #eef1f7 75%);
            background-size: 800px 100%;
            animation: shimmer 1.3s infinite linear;
        }
        .skeleton-row.w80 { width: 80%; }
        .skeleton-row.w60 { width: 60%; }
        .skeleton-row.tall { height: 110px; }
        </style>
        <div class="glass-card">
            <div class="skeleton-row w60"></div>
            <div class="skeleton-row tall"></div>
            <div class="skeleton-row w80"></div>
            <div class="skeleton-row"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
