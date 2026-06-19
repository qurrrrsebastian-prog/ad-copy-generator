"""Personal Finance Tracker — Streamlit · Sage Mint theme.

Enterprise-style UI with glassmorphism KPI cards, Plotly analytics, secure
input handling and a SQLite backend. Replaces the original Flask app
(preserved under ``old_app/``).

Run:  streamlit run app.py

Author: Avatar Putra Sigit
"""
from __future__ import annotations

import datetime
import io

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core.database import (
    add_transaction,
    count_transactions,
    delete_transaction,
    get_history,
    get_summary,
    get_transactions,
    init_db,
)
from core.security import (
    VALID_CATEGORIES,
    ValidationError,
    check_duplicate,
    generate_session_id,
    sanitize_input,
    validate_amount,
    validate_category,
    validate_date,
    validate_type,
)
from core.theme import (
    BALANCE,
    CHART_PALETTE,
    EXPENSE,
    INCOME,
    MINT,
    ORANGE,
    TEXT_SECONDARY,
    format_rupiah,
    inject_phase2_mint_theme,
    responsive_css,
)

MAX_PER_SESSION = 50  # rate limit: max transactions saved per session

# ── Page config & theme ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Personal Finance Tracker",
    layout="wide",
    page_icon="💰",
)
inject_phase2_mint_theme()
init_db()

# ── Session state ────────────────────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = generate_session_id()
if "saves_this_session" not in st.session_state:
    st.session_state.saves_this_session = 0
if "seeded_checked" not in st.session_state:
    # First run with empty DB -> offer / auto seed demo data.
    if count_transactions() == 0:
        from data.seeder import seed_transactions
        seed_transactions(force=True)
    st.session_state.seeded_checked = True


# ── Cached helpers ───────────────────────────────────────────────────────────
@st.cache_data(ttl=1800)
def load_dataframe(_cache_key: int) -> pd.DataFrame:
    """Load all transactions into a typed DataFrame. ``_cache_key`` busts cache."""
    rows = get_transactions()
    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(
            columns=["id", "type", "amount", "category", "date", "note", "created_at"]
        )
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    return df


def cache_key() -> int:
    """Cache key derived from row count + last id, so edits invalidate caches."""
    rows = get_history(1)
    last_id = rows[0]["id"] if rows else 0
    return count_transactions() * 1_000_000 + last_id


# ── Sidebar: add transaction form ────────────────────────────────────────────
def render_sidebar() -> None:
    with st.sidebar:
        st.header("➕ Tambah Transaksi")

        type_choice = st.segmented_control(
            "Tipe",
            ["💚 Pemasukan", "❤️ Pengeluaran"],
            default="❤️ Pengeluaran",
        )
        amount = st.number_input(
            "Jumlah (Rp)",
            min_value=0,
            step=10_000,
            format="%d",
            help="Contoh: 50000 untuk Rp 50.000",
        )
        category = st.selectbox("Kategori", VALID_CATEGORIES)
        date = st.date_input(
            "Tanggal",
            value=datetime.date.today(),
            max_value=datetime.date.today(),
            min_value=datetime.date.today() - datetime.timedelta(days=365),
        )
        note = st.text_input(
            "Catatan (opsional)",
            max_chars=100,
            placeholder="Misal: Makan siang di kantin",
        )

        if st.button("💾 Simpan", type="primary", width="stretch"):
            _handle_save(type_choice, amount, category, date, note)

        st.divider()
        st.header("🕒 Recent")
        recent = get_history(5)
        if not recent:
            st.caption("Belum ada transaksi.")
        for r in recent:
            icon = "💚" if r["type"] == "Pemasukan" else "❤️"
            st.caption(
                f"{r['date']} · {icon} {format_rupiah(r['amount'])} · {r['category']}"
            )


def _handle_save(type_choice, amount, category, date, note) -> None:
    """Validate, guard, and persist a new transaction."""
    if st.session_state.saves_this_session >= MAX_PER_SESSION:
        st.error("Batas 50 transaksi per sesi tercapai. Muat ulang halaman.")
        return

    t_type = "Pemasukan" if "Pemasukan" in type_choice else "Pengeluaran"
    try:
        t_type = validate_type(t_type)
        amount_v = validate_amount(amount)
        date_v = validate_date(date)
        category_v = validate_category(category)
        note_clean = sanitize_input(note)
    except ValidationError as e:
        st.warning(str(e))
        return

    if check_duplicate(amount_v, date_v, note_clean, minutes=1):
        st.warning("⚠️ Transaksi serupa sudah ada 1 menit yang lalu.")
        return

    new_id = add_transaction(
        {
            "type": t_type,
            "amount": amount_v,
            "category": category_v,
            "date": date_v,
            "note": note_clean,
        }
    )
    if new_id is None:
        # Fallback: keep a temporary copy in session_state.
        st.session_state.setdefault("temp_tx", []).append(
            {
                "type": t_type, "amount": amount_v, "category": category_v,
                "date": str(date_v), "note": note_clean,
            }
        )
        st.warning("Tersimpan sementara (DB gagal). Data ada di sesi ini.")
        return

    st.session_state.saves_this_session += 1
    st.toast("✅ Transaksi tersimpan!")
    st.cache_data.clear()
    st.rerun()


# ── KPI cards ────────────────────────────────────────────────────────────────
def render_kpis(summary: dict, df: pd.DataFrame) -> None:
    # Month-over-month delta percentages.
    inc_delta, exp_delta = _mom_deltas(df)
    c1, c2, c3, c4 = st.columns(4, gap="medium")
    with c1:
        st.metric(
            "💚 Pemasukan",
            format_rupiah(summary["income"]),
            delta=f"{inc_delta:+.1f}% MoM" if inc_delta is not None else None,
        )
    with c2:
        st.metric(
            "❤️ Pengeluaran",
            format_rupiah(summary["expense"]),
            delta=f"{exp_delta:+.1f}% MoM" if exp_delta is not None else None,
            delta_color="inverse",
        )
    with c3:
        st.metric("💙 Saldo", format_rupiah(summary["balance"]))
        if summary["balance"] < 0:
            st.caption(f":red[Saldo negatif: {format_rupiah(summary['balance'])}]")
    with c4:
        st.metric(
            "🟠 Terbesar",
            format_rupiah(summary["max_expense"]),
            help=f"Kategori: {summary['max_category']}",
        )
        st.caption(f"Kategori: {summary['max_category']}")


def _mom_deltas(df: pd.DataFrame):
    """Return (income %, expense %) change vs previous calendar month."""
    if df.empty:
        return None, None
    d = df.dropna(subset=["date"]).copy()
    if d.empty:
        return None, None
    d["ym"] = d["date"].dt.to_period("M")
    periods = sorted(d["ym"].unique())
    if len(periods) < 2:
        return None, None
    cur, prev = periods[-1], periods[-2]

    def _pct(t):
        c = d[(d["ym"] == cur) & (d["type"] == t)]["amount"].sum()
        p = d[(d["ym"] == prev) & (d["type"] == t)]["amount"].sum()
        if p == 0:
            return None
        return (c - p) / p * 100

    return _pct("Pemasukan"), _pct("Pengeluaran")


# ── Chart styling helper ─────────────────────────────────────────────────────
def _style(fig: go.Figure, height: int = 360) -> go.Figure:
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f0fdfa", family="sans-serif"),
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        title_font=dict(color="#f0fdfa", size=16),
    )
    fig.update_xaxes(gridcolor="rgba(45,212,191,0.15)", zerolinecolor="rgba(45,212,191,0.25)")
    fig.update_yaxes(gridcolor="rgba(45,212,191,0.15)", zerolinecolor="rgba(45,212,191,0.25)")
    return fig


# ── Tab: Dashboard ───────────────────────────────────────────────────────────
def tab_dashboard(df: pd.DataFrame) -> None:
    exp = df[df["type"] == "Pengeluaran"]
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Pengeluaran per Kategori")
        if exp.empty:
            st.caption("Belum ada pengeluaran.")
        else:
            by_cat = exp.groupby("category")["amount"].sum().reset_index()
            fig = px.pie(
                by_cat, names="category", values="amount", hole=0.45,
                color_discrete_sequence=["#f87171", "#fbbf24", "#a78bfa", "#2dd4bf",
                                         "#34d399", "#fb923c", "#f472b6", "#60a5fa"],
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(_style(fig), width="stretch")

    with col2:
        st.subheader("Pemasukan vs Pengeluaran (Bulanan)")
        if df.empty:
            st.caption("Belum ada data.")
        else:
            m = df.dropna(subset=["date"]).copy()
            m["bulan"] = m["date"].dt.strftime("%Y-%m")
            grp = m.groupby(["bulan", "type"])["amount"].sum().reset_index()
            fig = px.bar(
                grp, x="bulan", y="amount", color="type", barmode="group",
                color_discrete_map={"Pemasukan": INCOME, "Pengeluaran": EXPENSE},
            )
            fig.update_layout(legend_title_text="")
            st.plotly_chart(_style(fig), width="stretch")

    st.subheader("Tren Saldo Harian")
    if df.empty:
        st.caption("Belum ada data.")
    else:
        d = df.dropna(subset=["date"]).copy()
        d["signed"] = np.where(d["type"] == "Pemasukan", d["amount"], -d["amount"])
        daily = d.groupby(d["date"].dt.date)["signed"].sum().sort_index().cumsum()
        line = pd.DataFrame({"tanggal": daily.index, "saldo": daily.values})
        fig = px.area(line, x="tanggal", y="saldo")
        fig.update_traces(line_color=MINT, fillcolor="rgba(45,212,191,0.15)")
        st.plotly_chart(_style(fig), width="stretch")


# ── Tab: Trends ──────────────────────────────────────────────────────────────
def tab_trends(df: pd.DataFrame, summary: dict) -> None:
    exp = df[df["type"] == "Pengeluaran"].dropna(subset=["date"])
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Tren Pengeluaran Mingguan")
        if exp.empty:
            st.caption("Belum ada pengeluaran.")
        else:
            w = exp.copy()
            w["minggu"] = w["date"].dt.to_period("W").dt.start_time
            weekly = w.groupby("minggu")["amount"].sum().reset_index()
            fig = px.bar(weekly, x="minggu", y="amount")
            fig.update_traces(marker_color=EXPENSE)
            st.plotly_chart(_style(fig), width="stretch")

    with col2:
        st.subheader("Tingkat Tabungan")
        income = summary["income"]
        rate = ((summary["balance"] / income) * 100) if income > 0 else 0
        gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=round(rate, 1),
                number={"suffix": "%", "font": {"color": "#f0fdfa"}},
                gauge={
                    "axis": {"range": [-50, 100], "tickcolor": "#99f6e4"},
                    "bar": {"color": MINT},
                    "bgcolor": "rgba(255,255,255,0.05)",
                    "steps": [
                        {"range": [-50, 0], "color": "rgba(248,113,113,0.35)"},
                        {"range": [0, 30], "color": "rgba(251,191,36,0.30)"},
                        {"range": [30, 100], "color": "rgba(52,211,153,0.30)"},
                    ],
                },
            )
        )
        st.plotly_chart(_style(gauge), width="stretch")

    st.subheader("Tren Kategori dari Waktu ke Waktu")
    if exp.empty:
        st.caption("Belum ada pengeluaran.")
    else:
        c = exp.copy()
        c["bulan"] = c["date"].dt.strftime("%Y-%m")
        grp = c.groupby(["bulan", "category"])["amount"].sum().reset_index()
        fig = px.line(
            grp, x="bulan", y="amount", color="category", markers=True,
            color_discrete_sequence=CHART_PALETTE,
        )
        fig.update_layout(legend_title_text="")
        st.plotly_chart(_style(fig), width="stretch")


# ── Tab: Transaksi ───────────────────────────────────────────────────────────
def tab_transactions(df: pd.DataFrame) -> None:
    st.subheader("Semua Transaksi")
    if df.empty:
        _empty_state()
        return

    show = df.copy()
    show["Tanggal"] = show["date"].dt.strftime("%Y-%m-%d")
    show["Jumlah"] = show["amount"].apply(format_rupiah)
    show = show.rename(columns={
        "type": "Tipe", "category": "Kategori", "note": "Catatan", "id": "ID",
    })[["ID", "Tanggal", "Tipe", "Kategori", "Jumlah", "Catatan"]]

    def _row_style(row):
        color = ("rgba(52,211,153,0.10)" if row["Tipe"] == "Pemasukan"
                 else "rgba(248,113,113,0.10)")
        return [f"background-color: {color}"] * len(row)

    styled = show.style.apply(_row_style, axis=1)
    st.dataframe(styled, height=400, width="stretch", hide_index=True)

    # Download CSV.
    csv_buf = io.StringIO()
    show.to_csv(csv_buf, index=False)
    st.download_button(
        "⬇️ Download CSV",
        data=csv_buf.getvalue(),
        file_name=f"transaksi_{datetime.date.today().isoformat()}.csv",
        mime="text/csv",
    )

    # Delete a transaction.
    st.divider()
    st.markdown("**Hapus Transaksi**")
    col_a, col_b = st.columns([3, 1])
    with col_a:
        ids = show["ID"].tolist()
        del_id = st.selectbox("Pilih ID transaksi", ids, key="del_select")
    with col_b:
        st.write("")
        st.write("")
        if st.button("🗑️ Hapus", width="stretch"):
            if delete_transaction(del_id):
                st.toast("🗑️ Transaksi dihapus.")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Gagal menghapus transaksi.")


# ── Tab: Kalender ────────────────────────────────────────────────────────────
def tab_calendar(df: pd.DataFrame) -> None:
    st.subheader("Intensitas Pengeluaran (90 Hari)")
    exp = df[df["type"] == "Pengeluaran"].dropna(subset=["date"])
    if exp.empty:
        st.caption("Belum ada pengeluaran.")
        return

    today = pd.Timestamp(datetime.date.today())
    start = today - pd.Timedelta(days=90)
    window = exp[exp["date"] >= start]
    daily = window.groupby(window["date"].dt.normalize())["amount"].sum()

    # Build a calendar grid: weekday (row) x week (col).
    full = pd.date_range(start=start.normalize(), end=today.normalize(), freq="D")
    series = daily.reindex(full, fill_value=0)
    weekdays = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
    z, customtext = [[None] * 0 for _ in range(7)], [[None] * 0 for _ in range(7)]
    weeks: dict = {}
    for ts, val in series.items():
        wk = ts.isocalendar().week
        weeks.setdefault(wk, {})[ts.weekday()] = (val, ts)

    week_keys = sorted(weeks.keys())
    matrix = [[0] * len(week_keys) for _ in range(7)]
    labels = [[""] * len(week_keys) for _ in range(7)]
    for ci, wk in enumerate(week_keys):
        for wd in range(7):
            if wd in weeks[wk]:
                val, ts = weeks[wk][wd]
                matrix[wd][ci] = val
                labels[wd][ci] = f"{ts.date()}<br>{format_rupiah(val)}"

    fig = go.Figure(
        go.Heatmap(
            z=matrix,
            y=weekdays,
            text=labels,
            hoverinfo="text",
            colorscale=[
                [0.0, "rgba(52,211,153,0.15)"],
                [0.5, "#fbbf24"],
                [1.0, "#f87171"],
            ],
            showscale=True,
            xgap=3, ygap=3,
        )
    )
    fig.update_layout(xaxis_showticklabels=False)
    st.plotly_chart(_style(fig, height=300), width="stretch")

    # Clickable-style date drilldown via selector.
    st.markdown("**Lihat transaksi pada tanggal tertentu**")
    avail = sorted(window["date"].dt.date.unique(), reverse=True)
    if avail:
        pick = st.selectbox("Tanggal", avail, key="cal_date")
        day = window[window["date"].dt.date == pick]
        for _, r in day.iterrows():
            st.text(f"{r['category']} · {format_rupiah(r['amount'])} · {r['note']}")


# ── Empty state ──────────────────────────────────────────────────────────────
def _empty_state() -> None:
    st.markdown(
        """
        <div class="empty-state">
            <div class="icon">👛</div>
            <h3>Belum ada transaksi</h3>
            <p>Tambahkan transaksi pertamamu lewat form di sidebar.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Main ─────────────────────────────────────────────────────────────────────
def main() -> None:
    render_sidebar()

    st.markdown(
        """
        <div class="app-hero">
            <h1>💰 Personal Finance Tracker</h1>
            <p class="subtitle">Kelola pemasukan &amp; pengeluaran harian dengan mudah</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df = load_dataframe(cache_key())
    summary = get_summary()

    st.markdown('<p class="section-label">Ringkasan</p>', unsafe_allow_html=True)
    render_kpis(summary, df)
    st.divider()

    t1, t2, t3, t4 = st.tabs(["📊 Dashboard", "📈 Trends", "📋 Transaksi", "📅 Kalender"])
    with t1:
        tab_dashboard(df)
    with t2:
        tab_trends(df, summary)
    with t3:
        tab_transactions(df)
    with t4:
        tab_calendar(df)

    responsive_css()


if __name__ == "__main__":
    main()
