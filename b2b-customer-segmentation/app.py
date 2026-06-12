"""B2B Customer Segmentation with K-Means. Author: Avatar Putra Sigit"""
import os
import subprocess
import sys

import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "data", "customers.csv")

@st.cache_data
def load_data() -> pd.DataFrame:
    """Load customer data, generate if missing."""
    try:
        if not os.path.exists(CSV_PATH):
            subprocess.run([sys.executable, os.path.join(BASE_DIR, "data", "generator.py")], check=True)
        return pd.read_csv(CSV_PATH)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def elbow_method(df: pd.DataFrame, features: list) -> pd.DataFrame:
    """Calculate inertia for k=1 to 8."""
    try:
        scaler = StandardScaler()
        X = scaler.fit_transform(df[features])
        inertias = []
        for k in range(1, 9):
            km = KMeans(n_clusters=k, random_state=42, n_init=10)
            km.fit(X)
            inertias.append(km.inertia_)
        return pd.DataFrame({"k": range(1, 9), "inertia": inertias})
    except Exception as e:
        st.error(f"Error in elbow method: {e}")
        return pd.DataFrame({"k": [], "inertia": []})

def segment_customers(df: pd.DataFrame, features: list, n_clusters: int) -> pd.DataFrame:
    """Apply K-Means clustering with PCA projection for visualization."""
    try:
        scaler = StandardScaler()
        X = scaler.fit_transform(df[features])
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        df["cluster"] = kmeans.fit_predict(X)
        pca = PCA(n_components=2)
        pca_result = pca.fit_transform(X)
        df["pca_1"] = pca_result[:, 0]
        df["pca_2"] = pca_result[:, 1]
        return df
    except Exception as e:
        st.error(f"Error in clustering: {e}")
        return df

def cluster_persona(df: pd.DataFrame) -> dict:
    """Generate persona label for each cluster."""
    personas = {}
    try:
        for c in sorted(df["cluster"].unique()):
            sub = df[df["cluster"] == c]
            avg_value = sub["contract_value"].mean()
            avg_freq = sub["service_frequency"].mean()
            avg_sat = sub["satisfaction_score"].mean()
            avg_days = sub["last_order_days"].mean()
            if avg_value > 80_000_000 and avg_sat > 4.2:
                personas[c] = "🏆 High-Value Loyal"
            elif avg_value > 60_000_000 and avg_days > 180:
                personas[c] = "⚠️ At-Risk Big Client"
            elif avg_freq > 8:
                personas[c] = "🔥 Small Frequent"
            else:
                personas[c] = "💎 New Potential"
    except Exception as e:
        st.error(f"Error labeling personas: {e}")
    return personas

def main() -> None:
    """Render the Streamlit segmentation dashboard."""
    st.set_page_config(page_title="B2B Customer Segmentation", layout="wide")
    st.title("🎯 B2B Customer Segmentation")
    st.markdown("K-Means clustering untuk klien bisnis jasa B2B")

    df = load_data()
    if df.empty:
        st.stop()
    features = ["company_size", "contract_value", "service_frequency", "satisfaction_score", "last_order_days", "years_as_client"]

    with st.sidebar:
        st.header("⚙️ Settings")
        n_clusters = st.slider("Jumlah Cluster (K)", 2, 6, 4)
        st.markdown("---")
        st.markdown("**Fitur yang digunakan:**")
        for f in features:
            st.markdown(f"- {f}")

    st.subheader("1. Elbow Method — Cari K Optimal")
    elbow_df = elbow_method(df, features)
    fig = px.line(elbow_df, x="k", y="inertia", markers=True, title="Elbow Curve")
    st.plotly_chart(fig, use_container_width=True)

    df = segment_customers(df, features, n_clusters)
    personas = cluster_persona(df)

    st.subheader("2. Cluster Visualization (PCA 2D)")
    df["persona"] = df["cluster"].map(personas)
    fig2 = px.scatter(df, x="pca_1", y="pca_2", color="persona", hover_data=["company_name", "contract_value"], size="contract_value", title="Customer Clusters")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("3. Cluster Personas")
    for c in sorted(df["cluster"].unique()):
        sub = df[df["cluster"] == c]
        p = personas[c]
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Cluster", f"{c} ({p})")
        col2.metric("Count", len(sub))
        col3.metric("Avg Contract", f"Rp {sub['contract_value'].mean():,.0f}")
        col4.metric("Avg Satisfaction", f"{sub['satisfaction_score'].mean():.2f}")
        st.markdown("---")

    st.subheader("4. Recommendations per Cluster")
    recs = {
        "🏆 High-Value Loyal": "Prioritize retention. Offer loyalty discounts & premium support.",
        "⚠️ At-Risk Big Client": "Immediate outreach. Survey satisfaction & offer contract renewal incentive.",
        "🔥 Small Frequent": "Upsell to annual contract. Volume discount to increase contract value.",
        "💎 New Potential": "Nurture with education content. Free trial or demo to build trust."
    }
    for persona, rec in recs.items():
        if persona in df["persona"].values:
            st.markdown(f"**{persona}:** {rec}")

if __name__ == "__main__":
    main()
