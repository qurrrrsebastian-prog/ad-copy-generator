"""AI Ad Copy Generator — Royal Purple edition. Author: Avatar Putra Sigit

Multi-framework (AIDA / PAS / 4U / Storytelling) ad-copy generator with
glassmorphism UI, input sanitization, rate limiting, SQLite history, and
analytics. Original AIDA template engine in templates.py is preserved.
"""
import os
import sys
from datetime import datetime

import altair as alt
import pandas as pd
import streamlit as st

# Ensure local package imports resolve regardless of launch dir.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database import (
    init_db, save_generation, get_history, get_all_history, get_dummy_data,
)
from core.security import (
    sanitize_input, validate_select, validate_text_length, generate_session_id,
)
from core.theme import (
    inject_phase2_purple_theme, show_loading_skeleton, responsive_css,
    kpi_card, copy_to_clipboard_js, style_chart, CHART_PALETTE,
)
from templates import generate

AUDIENCES = ["B2B", "B2C", "F&B", "Property", "Tech", "Health", "Fashion"]
FRAMEWORKS = ["AIDA", "PAS", "4U", "Storytelling"]
TONES = ["Professional", "Casual", "Urgent", "Friendly", "Luxury"]
CTAS = ["Hubungi Kami", "Dapatkan Penawaran", "Pesan Sekarang", "Download Gratis", "Daftar Trial"]
RATE_LIMIT = 20

st.set_page_config(page_title="AI Ad Copy Generator", layout="wide", page_icon="✍️")
inject_phase2_purple_theme()
init_db()

# ---- Session state ----------------------------------------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = generate_session_id()
if "gen_count" not in st.session_state:
    st.session_state.gen_count = 0

dummy_df = get_dummy_data("ad_copies")


@st.cache_data(ttl=1800, show_spinner=False)
def cached_generate(product: str, audience: str, pain_point: str, framework: str, tone: str, cta: str) -> dict:
    """Cache generated copy per unique input combination (30 min TTL)."""
    return generate(product, audience, pain_point, framework, tone, cta)


def _fallback_copy(product: str) -> dict:
    """Template fallback drawn from the seed dataset when generation fails."""
    if not dummy_df.empty:
        row = dummy_df.iloc[0]
        return {
            "headline": f"{row['product_name']} — {row['target_audience']}",
            "body": str(row["ad_copy"]),
            "cta": str(row["cta"]),
        }
    return {
        "headline": f"{product} — solusi tepat untuk Anda",
        "body": "Template fallback: lengkapi brief untuk hasil yang dipersonalisasi.",
        "cta": "Hubungi Kami",
    }


def do_generate() -> None:
    """Validate brief, enforce rate limit, generate copy, persist history."""
    raw_product = st.session_state.get("in_product", "")
    product = sanitize_input(raw_product)
    pain_point = sanitize_input(st.session_state.get("in_pain", "")) or "tantangan operasional sehari-hari"
    audience = st.session_state.get("in_audience", AUDIENCES[0])
    framework = st.session_state.get("in_framework", "AIDA")
    tone = st.session_state.get("in_tone", "Professional")
    cta = st.session_state.get("in_cta", CTAS[0])

    # ---- Validation (raises -> surfaced to user) ----
    try:
        validate_text_length(product, min=3, max=100)
        validate_select(audience, AUDIENCES)
        validate_select(framework, FRAMEWORKS)
        validate_select(tone, TONES)
        validate_select(cta, CTAS)
    except ValueError as e:
        st.session_state.gen_error = str(e)
        return
    st.session_state.pop("gen_error", None)

    # ---- Rate limit ----
    if st.session_state.gen_count >= RATE_LIMIT:
        st.session_state.gen_error = "Rate limit reached (max 20 generasi / sesi)."
        return
    st.session_state.gen_count += 1

    # ---- Generate (with fallback) ----
    try:
        result = cached_generate(product, audience, pain_point, framework, tone, cta)
        st.session_state.used_fallback = False
    except Exception as e:
        print(f"[app] generation failed: {e}")
        result = _fallback_copy(product)
        st.session_state.used_fallback = True

    full_copy = f"{result['headline']}\n\n{result['body']}\n\n➡ {result['cta']}"
    st.session_state.generated = {
        "headline": result["headline"],
        "body": result["body"],
        "cta": result["cta"],
        "full": full_copy,
    }
    st.session_state.last_meta = {
        "product_name": product, "audience": audience,
        "framework": framework, "tone": tone, "cta": cta,
    }

    save_generation(st.session_state.session_id, {
        "product_name": product, "audience": audience, "framework": framework,
        "tone": tone, "generated_copy": full_copy, "cta": cta,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    })


# ---- Sidebar: Creative Brief -----------------------------------------------
with st.sidebar:
    st.header("🎯 Creative Brief")
    st.text_input("Product Name", key="in_product",
                  placeholder="e.g. Jasa Pembersihan Kaca RKARI", max_chars=100)
    st.selectbox("Target Audience", AUDIENCES, key="in_audience")
    st.text_area("Pain Point", key="in_pain",
                 placeholder="Masalah yang dipecahkan...", max_chars=200, height=100)
    st.segmented_control("Framework", FRAMEWORKS, default="AIDA", key="in_framework")
    st.segmented_control("Tone", TONES, default="Professional", key="in_tone")
    st.selectbox("Call to Action", CTAS, key="in_cta")
    st.button("✨ Generate Copy", type="primary", width="stretch", on_click=do_generate)
    st.caption(f"Generasi: {st.session_state.gen_count}/{RATE_LIMIT}")

    st.divider()
    st.header("🕒 History")
    history = get_history(st.session_state.session_id, limit=5)
    if history:
        for h in history:
            st.caption(f"{h['tone']} | {h['framework']} | {h['product_name'][:30]}")
    else:
        st.caption("Belum ada riwayat di sesi ini.")

# ---- Main -------------------------------------------------------------------
st.title("✍️ AI Ad Copy Generator")
st.caption("Generate high-converting ad copy with proven frameworks")

# Surface validation / rate-limit errors raised during generation.
if st.session_state.get("gen_error"):
    st.error(st.session_state.gen_error)
if st.session_state.get("used_fallback"):
    st.warning("Using template fallback")

# ---- KPI cards (combine seed data + this session's history) ----
hist_df = get_all_history(st.session_state.session_id)
combined = pd.concat([
    dummy_df.rename(columns={"target_audience": "audience"})[
        [c for c in ["product_name", "audience", "framework", "tone", "ad_copy"] if c in dummy_df.columns]
    ] if not dummy_df.empty else pd.DataFrame(),
    hist_df.rename(columns={}) if not hist_df.empty else pd.DataFrame(),
], ignore_index=True)

copies_count = int(len(combined))
if not combined.empty and "ad_copy" in combined.columns:
    lengths = combined["ad_copy"].dropna().astype(str).map(len)
    avg_len = int(lengths.mean()) if not lengths.empty else 0
else:
    avg_len = 0
top_framework = combined["framework"].mode().iloc[0] if ("framework" in combined.columns and not combined["framework"].dropna().empty) else "—"
top_tone = combined["tone"].mode().iloc[0] if ("tone" in combined.columns and not combined["tone"].dropna().empty) else "—"

k1, k2, k3, k4 = st.columns(4)
with k1:
    kpi_card("✨", copies_count, "Copies")
with k2:
    kpi_card("📝", f"{avg_len}", "Avg Length (chars)")
with k3:
    kpi_card("🎯", top_framework, "Top Framework")
with k4:
    kpi_card("🎨", top_tone, "Top Tone")

st.divider()

# ---- Tabs -------------------------------------------------------------------
tab_copy, tab_hist, tab_analytics = st.tabs(["✍️ Generated Copy", "📋 History", "📊 Analytics"])

with tab_copy:
    if "generated" in st.session_state:
        g = st.session_state.generated
        with st.container(border=True):
            st.markdown("##### 🎯 Headline")
            st.markdown(f"**{g['headline']}**", unsafe_allow_html=False)
            st.markdown("##### 📝 Body")
            st.text_area("Copy", g["body"], height=200, disabled=True, label_visibility="collapsed")
            st.markdown("##### 🔗 Call to Action")
            st.markdown(f"**{g['cta']}**", unsafe_allow_html=False)

        st.markdown("**📋 Salin teks (klik ikon di pojok kanan):**")
        copy_to_clipboard_js(g["full"])

        c1, c2 = st.columns(2)
        c1.button("📋 Copy to Clipboard", width="stretch",
                  on_click=lambda: st.toast("Copied to clipboard!"))
        c2.button("🔄 Regenerate", width="stretch", on_click=do_generate)
    else:
        st.info("Isi brief di sidebar lalu klik **Generate** untuk membuat copy pertamamu ✨")
        if not dummy_df.empty:
            sample = dummy_df.iloc[0]
            with st.container(border=True):
                st.caption("Contoh hasil (sample)")
                st.markdown(f"**{sample['product_name']} — {sample['target_audience']}**")
                st.text_area("Sample", str(sample["ad_copy"]), height=140,
                             disabled=True, label_visibility="collapsed")
                st.markdown(f"**➡ {sample['cta']}**")

with tab_hist:
    if not hist_df.empty:
        st.dataframe(hist_df, width="stretch", hide_index=True)
    else:
        st.info("Belum ada generasi tersimpan. Buat copy pertama Anda di sidebar.")

with tab_analytics:
    if combined.empty:
        st.info("Belum ada data untuk dianalisis.")
    else:
        ac1, ac2 = st.columns(2, gap="large")
        with ac1:
            with st.container(border=True):
                st.markdown("##### 🎨 Tone Usage")
                if "tone" in combined.columns and not combined["tone"].dropna().empty:
                    tone_counts = combined["tone"].value_counts().reset_index()
                    tone_counts.columns = ["tone", "count"]
                    bar = (
                        alt.Chart(tone_counts)
                        .mark_bar(cornerRadiusEnd=6)
                        .encode(
                            x=alt.X("tone:N", title=None, sort="-y"),
                            y=alt.Y("count:Q", title="Count"),
                            color=alt.Color("tone:N", scale=alt.Scale(range=CHART_PALETTE), legend=None),
                            tooltip=["tone", "count"],
                        )
                        .properties(height=300)
                    )
                    st.altair_chart(style_chart(bar), width="stretch")
        with ac2:
            with st.container(border=True):
                st.markdown("##### 📐 Framework Usage")
                if "framework" in combined.columns and not combined["framework"].dropna().empty:
                    fw_counts = combined["framework"].value_counts().reset_index()
                    fw_counts.columns = ["framework", "count"]
                    pie = (
                        alt.Chart(fw_counts)
                        .mark_arc(innerRadius=55)
                        .encode(
                            theta=alt.Theta("count:Q"),
                            color=alt.Color("framework:N", scale=alt.Scale(range=CHART_PALETTE),
                                            legend=alt.Legend(title="Framework")),
                            tooltip=["framework", "count"],
                        )
                        .properties(height=300)
                    )
                    st.altair_chart(style_chart(pie), width="stretch")

        with st.container(border=True):
            st.markdown("##### 📈 Daily Generation Count")
            date_series = None
            if "created_at" in hist_df.columns and not hist_df.empty:
                date_series = pd.to_datetime(hist_df["created_at"], errors="coerce").dt.date
            elif "date_created" in dummy_df.columns and not dummy_df.empty:
                date_series = pd.to_datetime(dummy_df["date_created"], errors="coerce").dt.date
            if date_series is not None:
                daily = date_series.value_counts().sort_index().reset_index()
                daily.columns = ["date", "count"]
                line = (
                    alt.Chart(daily)
                    .mark_line(point=alt.OverlayMarkDef(color=CHART_PALETTE[0]), color=CHART_PALETTE[0])
                    .encode(
                        x=alt.X("date:T", title=None),
                        y=alt.Y("count:Q", title="Generations"),
                        tooltip=["date", "count"],
                    )
                    .properties(height=260)
                )
                st.altair_chart(style_chart(line), width="stretch")

responsive_css()
