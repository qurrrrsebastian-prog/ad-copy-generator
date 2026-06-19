"""B2B Customer Segmentation — Bintang 5 (Slate Corporate).

AI-powered K-Means clustering dashboard for customer lifetime value optimization.
Author: Avatar Putra Sigit.

Preserves the original K-Means clustering approach (StandardScaler + KMeans,
4 segments) while adding a glassmorphism Slate Corporate UI, security hardening,
persistent run history, and graceful rule-based fallback.
"""
import os
import subprocess
import sys
import warnings

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.exceptions import ConvergenceWarning
from sklearn.preprocessing import StandardScaler

from core.database import init_db, save_segmentation, get_history, get_dummy_data
from core.security import (
    sanitize_input,
    validate_numeric,
    validate_select,
    generate_session_id,
    mask_company_name,
)
from core.theme import (
    inject_phase2_slate_theme,
    show_loading_skeleton,
    responsive_css,
    segment_color_css,
    CHART_PALETTE,
    SEGMENT_COLORS,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "data", "clients.csv")
SEEDER_PATH = os.path.join(BASE_DIR, "data", "seeder.py")
FEATURES = ["revenue", "contract_value", "engagement_score", "last_purchase"]
SEGMENT_ORDER = ["Champions", "Loyal", "At Risk", "Lost"]
MAX_RUNS = 5

# ---------------------------------------------------------------------------
# Page config + theme
# ---------------------------------------------------------------------------
st.set_page_config(page_title="B2B Customer Segmentation", layout="wide", page_icon="🎯")
inject_phase2_slate_theme()
segment_color_css()
init_db()


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    """Load data/clients.csv, seeding it on first run. NaN-safe."""
    try:
        if not os.path.exists(CSV_PATH):
            subprocess.run([sys.executable, SEEDER_PATH], check=True)
        df = pd.read_csv(CSV_PATH)
        # Numeric columns: fill NaN with median to keep K-Means happy.
        for col in FEATURES + ["employees"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
                if df[col].isna().any():
                    df[col] = df[col].fillna(df[col].median())
        if "churn_risk" in df.columns:
            df["churn_risk"] = df["churn_risk"].fillna("Medium")
        return df
    except Exception as e:
        st.error(f"Error loading data: {sanitize_input(str(e))}")
        return pd.DataFrame()


def _label_clusters(df: pd.DataFrame) -> pd.Series:
    """Map cluster ids to business segments via composite centroid score."""
    stats = df.groupby("cluster").agg(
        revenue=("revenue", "mean"),
        contract_value=("contract_value", "mean"),
        engagement_score=("engagement_score", "mean"),
        last_purchase=("last_purchase", "mean"),
    )
    norm = (stats - stats.min()) / (stats.max() - stats.min() + 1e-9)
    score = (
        norm["revenue"] + norm["contract_value"] + norm["engagement_score"]
        + (1 - norm["last_purchase"])
    )
    ranked = score.sort_values(ascending=False).index.tolist()
    mapping = {cid: SEGMENT_ORDER[i] for i, cid in enumerate(ranked)}
    return df["cluster"].map(mapping)


def _rule_based_segments(df: pd.DataFrame) -> pd.Series:
    """Fallback segmentation (if-else) when K-Means cannot converge."""
    def classify(row):
        rev, eng, rec = row["revenue"], row["engagement_score"], row["last_purchase"]
        if rev > 20_000_000_000 and eng > 60:
            return "Champions"
        if eng > 50 and rec < 120:
            return "Loyal"
        if rec > 240 or eng < 30:
            return "Lost"
        return "At Risk"
    return df.apply(classify, axis=1)


@st.cache_resource(show_spinner=False)
def _fit_kmeans(values: tuple, shape: tuple):
    """Cache a fitted KMeans model keyed by the (hashable) scaled data."""
    X = np.array(values).reshape(shape)
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        model = KMeans(n_clusters=4, random_state=42, n_init=10)
        model.fit(X)
    return model


def run_segmentation(df: pd.DataFrame) -> pd.DataFrame:
    """Cluster the filtered data, labelling segments. Falls back to rules."""
    work = df.copy().reset_index(drop=True)
    if len(work) < 4:
        # Not enough rows for 4 clusters — rule-based only.
        work["segment"] = _rule_based_segments(work)
        return work
    try:
        scaler = StandardScaler()
        X = scaler.fit_transform(work[FEATURES])
        model = _fit_kmeans(tuple(X.flatten().tolist()), X.shape)
        work["cluster"] = model.predict(X)
        work["segment"] = _label_clusters(work)
    except (ValueError, ConvergenceWarning) as e:
        st.warning(f"K-Means fallback (rule-based): {sanitize_input(str(e))}")
        work["segment"] = _rule_based_segments(work)
    return work


def kpi_card(col, css_class: str, icon: str, label: str, value) -> None:
    """Render a single glass KPI card with a segment-coloured left border."""
    col.markdown(
        f"""
        <div class="kpi-card {css_class}">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-value">{int(value)}</div>
            <div class="kpi-label">{sanitize_input(label)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def segmented_to_csv(df: pd.DataFrame, segment: str) -> bytes:
    """Return masked CSV bytes for one segment (privacy: mask company names)."""
    sub = df[df["segment"] == segment].copy()
    if "company_name" in sub.columns:
        sub["company_name"] = sub["company_name"].apply(mask_company_name)
    return sub.to_csv(index=False).encode("utf-8")


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = generate_session_id()
if "run_count" not in st.session_state:
    st.session_state.run_count = 0

df = load_data()
if df.empty:
    st.error("No data available. Please check data/clients.csv or the seeder.")
    st.stop()


# ---------------------------------------------------------------------------
# Sidebar — filters + history
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("🎛️ Filters")

    industries = sorted(df["industry"].dropna().unique().tolist())
    industry = st.multiselect("Industry", industries, default=industries)

    rev_min = int(df["revenue"].min() / 1e6)
    rev_max = int(df["revenue"].max() / 1e6)
    revenue_range = st.slider(
        "Revenue (Rp juta)", rev_min, rev_max, (rev_min, rev_max)
    )

    con_min = int(df["contract_value"].min() / 1e6)
    con_max = int(df["contract_value"].max() / 1e6)
    contract_range = st.slider(
        "Contract Value (Rp juta)", con_min, con_max, (con_min, con_max)
    )

    churn_options = ["Low", "Medium", "High"]
    churn_risk = st.multiselect("Churn Risk", churn_options, default=["Low", "Medium"])

    demo_mode = st.toggle("🕶️ Demo mode (mask names)", value=False)

    run_clicked = st.button("🎯 Run Segmentation", type="primary", use_container_width=True)

    st.divider()
    st.header("🕒 History")
    history = get_history(st.session_state.session_id)
    if history:
        for h in history:
            st.caption(f"{h['created_at']}: {sanitize_input(h['filter_summary'])}")
    else:
        st.caption("No runs yet.")


# ---------------------------------------------------------------------------
# Run segmentation (button handler)
# ---------------------------------------------------------------------------
if run_clicked:
    # Validate inputs against known option sets.
    if not validate_select(industry, industries):
        st.sidebar.error("Invalid industry selection.")
    elif not validate_select(churn_risk, churn_options):
        st.sidebar.error("Invalid churn risk selection.")
    elif st.session_state.run_count >= MAX_RUNS:
        st.error(f"Rate limit: max {MAX_RUNS} segmentation runs per session.")
    else:
        st.session_state.run_count += 1

        skeleton = st.empty()
        with skeleton.container():
            show_loading_skeleton()
        progress = st.progress(0)
        status = st.info("🎯 Running K-Means clustering...")

        # Filter
        progress.progress(25)
        mask = (
            df["industry"].isin(industry)
            & df["revenue"].between(revenue_range[0] * 1e6, revenue_range[1] * 1e6)
            & df["contract_value"].between(contract_range[0] * 1e6, contract_range[1] * 1e6)
            & df["churn_risk"].isin(churn_risk)
        )
        filtered = df[mask]

        progress.progress(60)
        if filtered.empty:
            progress.empty()
            skeleton.empty()
            status.empty()
            st.warning("No clients match the selected filters. Try widening them.")
        else:
            segmented = run_segmentation(filtered)
            segmented["demo_mode"] = demo_mode
            progress.progress(100)

            counts = segmented["segment"].value_counts().to_dict()
            filter_summary = (
                f"Industry={len(industry)} | Rev {revenue_range} | "
                f"Contract {contract_range} | Churn={','.join(churn_risk)}"
            )
            save_segmentation(st.session_state.session_id, filter_summary, counts)
            st.session_state.segments = segmented

            status.success("✅ Segmentation complete!")
            skeleton.empty()
            progress.empty()


# ---------------------------------------------------------------------------
# Main view
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <h1>🎯 B2B Customer Segmentation</h1>
        <div class="hero-sub">AI-powered K-Means clustering for customer lifetime value optimization</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if "segments" in st.session_state:
    seg_df = st.session_state.segments
    is_demo = bool(seg_df.get("demo_mode", pd.Series([False])).iloc[0]) if "demo_mode" in seg_df else False
    counts = seg_df["segment"].value_counts()

    # ---- KPI cards ----
    c1, c2, c3, c4 = st.columns(4)
    kpi_card(c1, "kpi-champions", "🏆", "Champions", counts.get("Champions", 0))
    kpi_card(c2, "kpi-loyal", "💚", "Loyal", counts.get("Loyal", 0))
    kpi_card(c3, "kpi-atrisk", "⚠️", "At Risk", counts.get("At Risk", 0))
    kpi_card(c4, "kpi-lost", "❌", "Lost", counts.get("Lost", 0))

    st.divider()

    tab_seg, tab_scatter, tab_list, tab_risk = st.tabs(
        ["📊 Segments", "📈 Scatter Plot", "📋 Client List", "⚠️ At Risk"]
    )

    # display name helper (respects demo mode)
    def disp_name(s: pd.Series) -> pd.Series:
        return s.apply(mask_company_name) if is_demo else s

    # ---- Tab: Segments ----
    with tab_seg:
        col_a, col_b = st.columns(2)
        with col_a:
            pie = px.pie(
                values=counts.values,
                names=counts.index,
                title="Segment Distribution",
                color=counts.index,
                color_discrete_map=SEGMENT_COLORS,
                hole=0.45,
            )
            pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#334155",
            )
            st.plotly_chart(pie, use_container_width=True)
        with col_b:
            avg_contract = (
                seg_df.groupby("segment")["contract_value"].mean()
                .reindex([s for s in SEGMENT_ORDER if s in counts.index])
            )
            bar = px.bar(
                x=avg_contract.index,
                y=avg_contract.values,
                title="Avg Contract Value per Segment",
                color=avg_contract.index,
                color_discrete_map=SEGMENT_COLORS,
                labels={"x": "Segment", "y": "Avg Contract (Rp)"},
            )
            bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#334155",
                showlegend=False,
            )
            st.plotly_chart(bar, use_container_width=True)

        summary = (
            seg_df.groupby("segment")
            .agg(
                clients=("id", "count"),
                avg_revenue=("revenue", "mean"),
                avg_contract=("contract_value", "mean"),
                avg_engagement=("engagement_score", "mean"),
                avg_recency_days=("last_purchase", "mean"),
            )
            .reindex([s for s in SEGMENT_ORDER if s in counts.index])
            .round(1)
        )
        st.dataframe(summary, use_container_width=True)

    # ---- Tab: Scatter Plot ----
    with tab_scatter:
        plot_df = seg_df.copy()
        plot_df["display_name"] = disp_name(plot_df["company_name"])
        scatter = px.scatter(
            plot_df,
            x="revenue",
            y="engagement_score",
            color="segment",
            size="contract_value",
            color_discrete_map=SEGMENT_COLORS,
            hover_data={
                "display_name": True,
                "revenue": ":,.0f",
                "engagement_score": ":.1f",
                "contract_value": ":,.0f",
                "segment": True,
            },
            title="Revenue vs Engagement (size = contract value)",
            size_max=30,
        )
        scatter.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#334155",
            xaxis=dict(gridcolor="rgba(15,23,42,0.06)"),
            yaxis=dict(gridcolor="rgba(15,23,42,0.06)"),
        )
        st.plotly_chart(scatter, use_container_width=True)

    # ---- Tab: Client List ----
    with tab_list:
        fcol, scol = st.columns([1, 2])
        with fcol:
            seg_filter = st.multiselect(
                "Filter by segment",
                [s for s in SEGMENT_ORDER if s in counts.index],
                default=[s for s in SEGMENT_ORDER if s in counts.index],
            )
        with scol:
            search = sanitize_input(st.text_input("🔍 Search company name", ""))

        list_df = seg_df[seg_df["segment"].isin(seg_filter)].copy()
        if search:
            list_df = list_df[
                list_df["company_name"].str.contains(search, case=False, na=False)
            ]
        list_df["company_name"] = disp_name(list_df["company_name"])
        show_cols = [
            "id", "company_name", "industry", "revenue", "employees",
            "contract_value", "engagement_score", "last_purchase",
            "churn_risk", "segment",
        ]
        st.dataframe(
            list_df[[c for c in show_cols if c in list_df.columns]],
            height=400,
            use_container_width=True,
        )

    # ---- Tab: At Risk ----
    with tab_risk:
        risk_df = seg_df[seg_df["segment"] == "At Risk"].copy()
        if risk_df.empty:
            st.success("🎉 No At Risk clients in this run.")
        else:
            def action(row):
                if row["last_purchase"] > 200:
                    return "📞 Call personally"
                if row["engagement_score"] < 40:
                    return "🎁 Send discount offer"
                if row["contract_value"] > 200_000_000:
                    return "🤝 Schedule account review"
                return "✉️ Send re-engagement email"
            risk_df["recommended_action"] = risk_df.apply(action, axis=1)
            risk_df["company_name"] = disp_name(risk_df["company_name"])
            st.dataframe(
                risk_df[
                    ["id", "company_name", "industry", "contract_value",
                     "engagement_score", "last_purchase", "recommended_action"]
                ],
                use_container_width=True,
            )
            st.download_button(
                "⬇️ Download At Risk CSV",
                segmented_to_csv(seg_df, "At Risk"),
                "at_risk.csv",
                "text/csv",
            )

    st.divider()

    # ---- Download buttons (4 segments) ----
    st.subheader("📥 Export Segments")
    d1, d2, d3, d4 = st.columns(4)
    d1.download_button(
        "Download Champions", segmented_to_csv(seg_df, "Champions"),
        "champions.csv", "text/csv", use_container_width=True,
    )
    d2.download_button(
        "Download Loyal", segmented_to_csv(seg_df, "Loyal"),
        "loyal.csv", "text/csv", use_container_width=True,
    )
    d3.download_button(
        "Download At Risk", segmented_to_csv(seg_df, "At Risk"),
        "at_risk.csv", "text/csv", use_container_width=True,
    )
    d4.download_button(
        "Download Lost", segmented_to_csv(seg_df, "Lost"),
        "lost.csv", "text/csv", use_container_width=True,
    )

else:
    # ---- Empty state ----
    st.info("🎯 Select filters and run segmentation to see results")
    st.markdown(
        '<div class="glass-card slide-in">'
        '<h3>🎯 Select filters to run segmentation</h3>'
        '<p>Configure the filters in the sidebar, then click '
        '<b>Run Segmentation</b> to cluster your B2B clients with K-Means.</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    # Sample preview scatter from the full dataset (pre-labelled by seeder).
    if "segment" in df.columns:
        preview = df.copy()
        preview["display_name"] = preview["company_name"].apply(mask_company_name)
        sample = px.scatter(
            preview,
            x="revenue",
            y="engagement_score",
            color="segment",
            size="contract_value",
            color_discrete_map=SEGMENT_COLORS,
            title="Preview — sample segmentation",
            size_max=28,
            opacity=0.7,
        )
        sample.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#334155",
            xaxis=dict(gridcolor="rgba(15,23,42,0.06)"),
            yaxis=dict(gridcolor="rgba(15,23,42,0.06)"),
        )
        st.plotly_chart(sample, use_container_width=True)

responsive_css()
