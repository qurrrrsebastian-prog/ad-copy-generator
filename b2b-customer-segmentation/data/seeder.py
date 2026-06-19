"""Seed 200 synthetic B2B clients and pre-label them with K-Means (4 clusters).

Columns: id, company_name, industry, revenue, employees, contract_value,
engagement_score, last_purchase, churn_risk.

Segments (Champions / Loyal / At Risk / Lost) are derived from the cluster
centroids so labels stay meaningful regardless of cluster index ordering.
Reproducible via seed=42.
"""
import os

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "clients.csv")

INDUSTRIES = ["Property", "Retail", "Manufacturing", "Hospital", "Office Building", "Hotel"]
FEATURES = ["revenue", "contract_value", "engagement_score", "last_purchase"]


def _label_clusters(df: pd.DataFrame) -> pd.Series:
    """Map raw cluster ids to business segments using a composite score.

    Higher revenue + contract + engagement and lower recency (last_purchase)
    => better segment. We rank clusters by a composite centroid score and assign
    Champions > Loyal > At Risk > Lost.
    """
    order = ["Champions", "Loyal", "At Risk", "Lost"]
    stats = df.groupby("cluster").agg(
        revenue=("revenue", "mean"),
        contract_value=("contract_value", "mean"),
        engagement_score=("engagement_score", "mean"),
        last_purchase=("last_purchase", "mean"),
    )
    # Normalise each driver 0..1 then build a score (recency inverted).
    norm = (stats - stats.min()) / (stats.max() - stats.min() + 1e-9)
    score = (
        norm["revenue"] + norm["contract_value"] + norm["engagement_score"]
        + (1 - norm["last_purchase"])
    )
    ranked = score.sort_values(ascending=False).index.tolist()
    mapping = {cluster_id: order[i] for i, cluster_id in enumerate(ranked)}
    return df["cluster"].map(mapping)


def generate_clients(n: int = 200) -> pd.DataFrame:
    """Generate, cluster, label, and persist the client dataset."""
    try:
        rng = np.random.default_rng(42)
        revenue = rng.integers(500_000_000, 50_000_000_000, n).astype(float)
        employees = rng.integers(5, 2000, n)
        contract_value = rng.integers(5_000_000, 500_000_000, n).astype(float)
        engagement_score = np.round(rng.uniform(0, 100, n), 1)
        last_purchase = rng.integers(1, 365, n)  # days since last purchase
        churn_pool = ["Low", "Medium", "High"]
        churn_risk = rng.choice(churn_pool, n, p=[0.45, 0.35, 0.20])

        df = pd.DataFrame(
            {
                "id": np.arange(1, n + 1),
                "company_name": [f"Company_{i}" for i in range(1, n + 1)],
                "industry": rng.choice(INDUSTRIES, n),
                "revenue": revenue,
                "employees": employees,
                "contract_value": contract_value,
                "engagement_score": engagement_score,
                "last_purchase": last_purchase,
                "churn_risk": churn_risk,
            }
        )

        # ---- K-Means: 4 clusters on scaled features ----
        scaler = StandardScaler()
        X = scaler.fit_transform(df[FEATURES])
        kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
        df["cluster"] = kmeans.fit_predict(X)
        df["segment"] = _label_clusters(df)

        df.to_csv(CSV_PATH, index=False)
        print(f"Seeded {n} B2B clients -> {CSV_PATH}")
        print(df["segment"].value_counts().to_string())
        return df
    except Exception as e:
        print(f"Error seeding clients: {e}")
        return pd.DataFrame()


if __name__ == "__main__":
    generate_clients()
