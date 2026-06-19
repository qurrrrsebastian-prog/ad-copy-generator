"""Jakarta Water Quality Monitor — Streamlit dashboard (Aqua Marine theme).

Real-time-feel monitoring & anomaly detection for Jakarta water stations.
Author: Avatar Putra Sigit
"""
from __future__ import annotations

import datetime
import os
import sys

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Ensure local package import works regardless of launch dir.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database import get_dummy_data, get_history, init_db, save_filter
from core.security import (
    VALID_LOCATIONS,
    VALID_STATUSES,
    generate_session_id,
    sanitize_input,
    validate_location,
    validate_status,
)
from core.theme import (
    CHART_PALETTE,
    STATUS_COLORS,
    inject_phase2_aqua_theme,
    responsive_css,
    show_loading_skeleton,
)

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "water_quality.csv")

# ---------------------------------------------------------------------------
# Page config + theme
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Jakarta Water Quality Monitor",
    layout="wide",
    page_icon="💧",
)
inject_phase2_aqua_theme()
init_db()

if "session_id" not in st.session_state:
    st.session_state.session_id = generate_session_id()
if "filter_ops" not in st.session_state:
    st.session_state.filter_ops = 0


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def load_data() -> pd.DataFrame:
    """Load water quality CSV, seeding it first if missing. NaN -> median."""
    try:
        if not os.path.exists(DATA_PATH):
            from data.seeder import seed

            seed()
        df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    except Exception as exc:  # pragma: no cover - defensive fallback
        st.warning(f"Gagal memuat data ({exc}). Menggunakan data contoh.")
        df = get_dummy_data("water_readings")
        df["date"] = pd.to_datetime(df["date"])

    # Fill numeric NaNs with median per column.
    for col in ["pH", "turbidity", "TDS", "temperature"]:
        if col in df.columns and df[col].isna().any():
            df[col] = df[col].fillna(df[col].median())
    return df


with st.spinner("Loading water quality data..."):
    df = load_data()

if df.empty:
    st.error("Tidak ada data tersedia.")
    st.stop()


def status_dot(value: float, kind: str) -> str:
    """Return a CSS dot class given a parameter value and its kind."""
    if kind == "pH":
        if value < 6.0 or value > 9.0:
            return "dot-red"
        if value < 6.5 or value > 8.5:
            return "dot-orange"
        return "dot-green"
    if kind == "TDS":
        if value > 1000:
            return "dot-red"
        if value > 500:
            return "dot-orange"
        return "dot-green"
    if kind == "turbidity":
        if value > 50:
            return "dot-red"
        if value > 25:
            return "dot-orange"
        return "dot-green"
    return "dot-green"


# ---------------------------------------------------------------------------
# Sidebar — Filters
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("🎛️ Filter")

    all_locations = sorted(df["location"].unique().tolist())
    location_filter = st.multiselect(
        "Lokasi", all_locations, default=all_locations[:3]
    )
    status_filter = st.multiselect(
        "Status", VALID_STATUSES, default=["Safe", "Alert"]
    )
    param_filter = st.multiselect(
        "Parameter",
        ["pH", "Turbidity", "TDS", "Temperature"],
        default=["pH", "TDS"],
    )
    date_range = st.date_input(
        "Rentang Tanggal",
        [datetime.date(2026, 1, 1), datetime.date.today()],
    )

    apply_clicked = st.button("🔍 Filter Data", type="primary", width="stretch")

    if apply_clicked:
        # Rate limit: max 10 filter ops per session.
        if st.session_state.filter_ops >= 10:
            st.warning("Batas 10 operasi filter per sesi tercapai.")
        elif not validate_location(location_filter) or not validate_status(status_filter):
            st.error("Input filter tidak valid.")
        else:
            st.session_state.filter_ops += 1
            save_filter(
                st.session_state.session_id,
                sanitize_input(str({"loc": location_filter, "status": status_filter})),
            )
            st.session_state.applied = True

    st.divider()
    st.header("📊 Summary")
    total_stations = len(df)
    safe_pct = round((df["status"] == "Safe").mean() * 100, 1)
    critical_count_all = int((df["status"] == "Critical").sum())
    st.metric("Total Stasiun", total_stations)
    st.metric("% Safe", f"{safe_pct}%")
    st.metric(
        "Critical",
        critical_count_all,
        delta="⚠️" if critical_count_all > 0 else None,
    )

    st.divider()
    st.header("🕒 History")
    history = get_history(st.session_state.session_id, limit=5)
    if history:
        for h in history:
            st.caption(f"`{h['created_at']}` — {sanitize_input(h['filters'])[:60]}")
    else:
        st.caption("Belum ada riwayat filter.")


# ---------------------------------------------------------------------------
# Apply filters
# ---------------------------------------------------------------------------
def apply_filters(data: pd.DataFrame) -> pd.DataFrame:
    out = data.copy()
    if location_filter:
        out = out[out["location"].isin(location_filter)]
    if status_filter:
        out = out[out["status"].isin(status_filter)]
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
        out = out[(out["date"] >= start) & (out["date"] <= end)]
    return out


filtered = apply_filters(df)

# ---------------------------------------------------------------------------
# Main header
# ---------------------------------------------------------------------------
st.title("💧 Jakarta Water Quality Monitor")
st.caption("Real-time monitoring & anomaly detection for Jakarta water stations")

# Empty-state guidance.
if filtered.empty:
    st.info("💧 Pilih filter untuk melihat data — tidak ada baris yang cocok dengan filter saat ini.")
    sample = df.head(50)
    fig = px.scatter(
        sample, x="pH", y="TDS", color="status",
        color_discrete_map=STATUS_COLORS, title="Contoh data (sample)",
    )
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", height=380,
                      font=dict(family="Segoe UI, sans-serif", color="#ecfeff"))
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    responsive_css()
    st.stop()

critical_count = int((filtered["status"] == "Critical").sum())
if critical_count > 0:
    st.error(f"⚠️ {critical_count} stasiun dalam status CRITICAL! Segera periksa.")

# ---------------------------------------------------------------------------
# KPI cards
# ---------------------------------------------------------------------------
avg_ph = filtered["pH"].mean()
avg_tds = filtered["TDS"].mean()
avg_turb = filtered["turbidity"].mean()
avg_temp = filtered["temperature"].mean()

kpi_cols = st.columns(4)
kpi_data = [
    ("🧪", "Avg pH", f"{avg_ph:.2f}", status_dot(avg_ph, "pH")),
    ("💧", "Avg TDS", f"{avg_tds:.0f} ppm", status_dot(avg_tds, "TDS")),
    ("🌫️", "Avg Turbidity", f"{avg_turb:.1f} NTU", status_dot(avg_turb, "turbidity")),
    ("🌡️", "Avg Temp", f"{avg_temp:.1f}°C", "dot-green"),
]
for col, (icon, label, value, dot) in zip(kpi_cols, kpi_data):
    col.markdown(
        f"""
        <div class="aqua-card">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-label">{label}<span class="status-dot {dot}"></span></div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab_overview, tab_map, tab_trends, tab_data, tab_corr = st.tabs(
    ["📊 Overview", "📍 Map", "📈 Trends", "📋 Data", "🔥 Correlation"]
)


PLOTLY_CONFIG = {"displayModeBar": False, "responsive": True}


def dark_layout(fig: go.Figure, height: int = 420) -> go.Figure:
    """Apply consistent professional Aqua Marine styling to a plotly figure."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI, system-ui, sans-serif", color="#ecfeff", size=13),
        title=dict(font=dict(size=17, color="#ecfeff"), x=0.01, xanchor="left", y=0.97),
        height=height,
        margin=dict(l=20, r=20, t=70, b=20),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            bgcolor="rgba(0,0,0,0)", font=dict(size=12), title_text="",
        ),
        hoverlabel=dict(
            bgcolor="#083344", bordercolor="#67e8f9",
            font=dict(color="#ecfeff", size=12, family="Segoe UI, sans-serif"),
        ),
        hovermode="closest",
    )
    axis_style = dict(
        gridcolor="rgba(103,232,249,0.12)",
        zerolinecolor="rgba(103,232,249,0.2)",
        title_font=dict(size=13, color="#a5f3fc"),
        tickfont=dict(size=11, color="#a5f3fc"),
    )
    fig.update_xaxes(**axis_style)
    fig.update_yaxes(**axis_style)
    return fig


# ---- Overview ----
with tab_overview:
    try:
        # Hero chart — full width so bubbles have room to breathe.
        scatter = px.scatter(
            filtered, x="pH", y="TDS", color="status", size="turbidity",
            size_max=18, color_discrete_map=STATUS_COLORS, hover_name="station_name",
            hover_data={"location": True, "temperature": True, "turbidity": True},
            labels={"pH": "pH", "TDS": "TDS (ppm)", "status": "Status"},
            title="pH vs TDS  ·  ukuran titik = turbidity",
        )
        scatter.update_traces(
            marker=dict(opacity=0.75, line=dict(width=0.6, color="rgba(8,51,68,0.7)"))
        )
        st.plotly_chart(dark_layout(scatter, height=440), width="stretch", config=PLOTLY_CONFIG)

        c1, c2 = st.columns(2)
        box = px.box(
            filtered, x="location", y="TDS", color="status",
            color_discrete_map=STATUS_COLORS,
            labels={"location": "Lokasi", "TDS": "TDS (ppm)", "status": "Status"},
            title="Distribusi TDS per Lokasi",
        )
        box.update_xaxes(tickangle=-25)
        c1.plotly_chart(dark_layout(box, height=400), width="stretch", config=PLOTLY_CONFIG)

        hist = px.histogram(
            filtered, x="pH", nbins=30, title="Distribusi pH + kurva normal",
            labels={"pH": "pH", "count": "Jumlah"},
            color_discrete_sequence=[CHART_PALETTE[0]],
        )
        hist.update_traces(marker_line_color="rgba(8,51,68,0.6)", marker_line_width=0.5)
        # Normal curve overlay.
        mu, sigma = filtered["pH"].mean(), filtered["pH"].std()
        if sigma and not np.isnan(sigma):
            xs = np.linspace(filtered["pH"].min(), filtered["pH"].max(), 100)
            ys = (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((xs - mu) / sigma) ** 2)
            ys = ys * len(filtered) * (filtered["pH"].max() - filtered["pH"].min()) / 30
            hist.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name="Normal",
                                      line=dict(color=CHART_PALETTE[4], width=3)))
        c2.plotly_chart(dark_layout(hist, height=400), width="stretch", config=PLOTLY_CONFIG)
    except Exception as exc:
        st.warning(f"Grafik gagal dirender ({exc}). Menampilkan statistik:")
        st.dataframe(filtered[["pH", "TDS", "turbidity", "temperature"]].describe())


# ---- Map ----
with tab_map:
    try:
        import folium
        from streamlit_folium import st_folium

        center = [filtered["lat"].mean(), filtered["lon"].mean()]
        fmap = folium.Map(location=center, zoom_start=10, tiles="CartoDB dark_matter")

        for _, row in filtered.iterrows():
            color = STATUS_COLORS.get(row["status"], "#06b6d4")
            radius = 10 if row["status"] == "Critical" else 6
            popup_html = (
                f"<b>{sanitize_input(row['station_name'])}</b><br>"
                f"Lokasi: {sanitize_input(row['location'])}<br>"
                f"pH: {row['pH']} | TDS: {row['TDS']} ppm<br>"
                f"Turbidity: {row['turbidity']} NTU | Temp: {row['temperature']}°C<br>"
                f"Status: <b>{row['status']}</b>"
            )
            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=radius,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.85 if row["status"] == "Critical" else 0.6,
                weight=3 if row["status"] == "Critical" else 1,
                popup=folium.Popup(popup_html, max_width=260),
            ).add_to(fmap)

        # Legend (bottom-right).
        legend = """
        <div style="position: fixed; bottom: 24px; right: 24px; z-index: 9999;
            background: rgba(8,51,68,0.9); border: 1px solid rgba(103,232,249,0.25);
            border-radius: 10px; padding: 10px 14px; color: #ecfeff; font-size: 13px;">
            <b>Legend</b><br>
            <span style="color:#34d399;">●</span> Safe&nbsp;
            <span style="color:#fbbf24;">●</span> Alert&nbsp;
            <span style="color:#f87171;">●</span> Critical
        </div>"""
        fmap.get_root().html.add_child(folium.Element(legend))
        st_folium(fmap, use_container_width=True, height=520, returned_objects=[])
    except Exception as exc:
        st.warning(f"Peta gagal dirender ({exc}). Daftar lokasi & status:")
        st.dataframe(
            filtered.groupby(["location", "status"]).size().reset_index(name="count"),
            width="stretch",
        )


# ---- Trends ----
with tab_trends:
    try:
        ts = filtered.copy()
        ts["month"] = ts["date"].dt.to_period("M").dt.to_timestamp()
        monthly = ts.groupby("month")[["pH", "TDS", "turbidity"]].mean().reset_index()

        line = go.Figure()
        line.add_trace(go.Scatter(x=monthly["month"], y=monthly["pH"], name="pH",
                                  mode="lines+markers",
                                  line=dict(color=CHART_PALETTE[0], width=3),
                                  marker=dict(size=7)))
        line.add_trace(go.Scatter(x=monthly["month"], y=monthly["turbidity"], name="Turbidity (NTU)",
                                  mode="lines+markers",
                                  line=dict(color=CHART_PALETTE[3], width=3),
                                  marker=dict(size=7)))
        line.add_trace(go.Scatter(x=monthly["month"], y=monthly["TDS"], name="TDS (ppm)",
                                  mode="lines+markers",
                                  line=dict(color=CHART_PALETTE[2], width=3),
                                  marker=dict(size=7), yaxis="y2"))
        line.update_layout(
            title="Rata-rata bulanan (pH / Turbidity / TDS)",
            yaxis=dict(title="pH · Turbidity (NTU)"),
            yaxis2=dict(title="TDS (ppm)", overlaying="y", side="right", showgrid=False),
        )
        # Anomaly highlight: mark months where avg pH falls outside the safe band.
        anomalies = monthly[(monthly["pH"] < 6.5) | (monthly["pH"] > 8.5)]
        if not anomalies.empty:
            line.add_trace(go.Scatter(
                x=anomalies["month"], y=anomalies["pH"], name="pH anomali",
                mode="markers",
                marker=dict(size=14, color="rgba(248,113,113,0.0)",
                            line=dict(color="#f87171", width=2.5), symbol="circle"),
            ))
        st.plotly_chart(dark_layout(line, height=420), width="stretch", config=PLOTLY_CONFIG)

        # Area chart: status distribution over time.
        status_ts = ts.groupby(["month", "status"]).size().reset_index(name="count")
        area = px.area(
            status_ts, x="month", y="count", color="status",
            color_discrete_map=STATUS_COLORS,
            labels={"month": "Bulan", "count": "Jumlah stasiun", "status": "Status"},
            title="Distribusi status dari waktu ke waktu",
        )
        st.plotly_chart(dark_layout(area, height=380), width="stretch", config=PLOTLY_CONFIG)
    except Exception as exc:
        st.warning(f"Tren gagal dirender ({exc}).")
        st.dataframe(filtered.describe())


# ---- Data ----
with tab_data:
    try:
        def highlight_status(row):
            colors = {
                "Safe": "background-color: rgba(52,211,153,0.12)",
                "Alert": "background-color: rgba(251,191,36,0.12)",
                "Critical": "background-color: rgba(248,113,113,0.18)",
            }
            return [colors.get(row["status"], "")] * len(row)

        show_cols = ["id", "station_name", "location", "pH", "turbidity", "TDS",
                     "temperature", "date", "status"]
        styled = filtered[show_cols].style.apply(highlight_status, axis=1)
        st.dataframe(styled, height=400, width="stretch")

        csv = filtered[show_cols].to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download CSV", csv, file_name="water_quality_filtered.csv",
            mime="text/csv",
        )
    except Exception as exc:
        st.warning(f"Tabel gagal dirender ({exc}).")
        st.dataframe(filtered)


# ---- Correlation ----
with tab_corr:
    try:
        num_cols = ["pH", "turbidity", "TDS", "temperature"]
        corr = filtered[num_cols].corr()
        heat = px.imshow(
            corr, text_auto=".2f", aspect="auto",
            color_continuous_scale=["#083344", "#0891b2", "#06b6d4", "#67e8f9"],
            title="Matriks korelasi parameter",
        )
        heat.update_xaxes(side="bottom")
        st.plotly_chart(dark_layout(heat, height=380), width="stretch", config=PLOTLY_CONFIG)

        c1, c2 = st.columns([2, 1])
        matrix = px.scatter_matrix(
            filtered, dimensions=num_cols, color="status",
            color_discrete_map=STATUS_COLORS, title="Scatter matrix",
        )
        matrix.update_traces(diagonal_visible=False, showupperhalf=False,
                             marker=dict(size=4, opacity=0.6))
        c1.plotly_chart(dark_layout(matrix, height=480), width="stretch", config=PLOTLY_CONFIG)

        with c2:
            st.markdown("**Koefisien korelasi**")
            pairs = []
            for i in range(len(num_cols)):
                for j in range(i + 1, len(num_cols)):
                    pairs.append({
                        "Pair": f"{num_cols[i]} ↔ {num_cols[j]}",
                        "r": round(corr.iloc[i, j], 3),
                    })
            st.dataframe(pd.DataFrame(pairs), width="stretch", hide_index=True)
    except Exception as exc:
        st.warning(f"Korelasi gagal dirender ({exc}).")
        st.dataframe(filtered.describe())


responsive_css()
