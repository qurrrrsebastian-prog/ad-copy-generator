"""Seed 500 rows of Jakarta-area water quality data -> data/water_quality.csv

Author: Avatar Putra Sigit
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

LOCATIONS = [
    "Jakarta Selatan",
    "Jakarta Utara",
    "Jakarta Timur",
    "Jakarta Barat",
    "Jakarta Pusat",
    "Bekasi",
    "Tangerang",
    "Depok",
    "Bogor",
]

# Approximate centre coordinates for map markers.
LOCATION_COORDS = {
    "Jakarta Selatan": (-6.2615, 106.8106),
    "Jakarta Utara": (-6.1214, 106.8740),
    "Jakarta Timur": (-6.2250, 106.9004),
    "Jakarta Barat": (-6.1683, 106.7588),
    "Jakarta Pusat": (-6.1865, 106.8343),
    "Bekasi": (-6.2383, 106.9756),
    "Tangerang": (-6.1783, 106.6319),
    "Depok": (-6.4025, 106.7942),
    "Bogor": (-6.5950, 106.8166),
}

OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "water_quality.csv")


def classify(ph: float, tds: float, turbidity: float) -> str:
    """Derive status from parameters (Critical wins over Alert over Safe)."""
    if ph < 6.0 or ph > 9.0 or tds > 1000 or turbidity > 50:
        return "Critical"
    if (6.0 <= ph < 6.5) or (8.5 < ph <= 9.0) or (500 < tds <= 1000) or (25 < turbidity <= 50):
        return "Alert"
    if 6.5 <= ph <= 8.5 and tds <= 500 and turbidity <= 25:
        return "Safe"
    return "Alert"


def seed(n: int = 500, seed_value: int = 42) -> pd.DataFrame:
    """Generate ``n`` rows and write them to ``water_quality.csv``."""
    rng = np.random.default_rng(seed_value)
    rows = []
    dates = pd.date_range("2026-01-01", "2026-06-16", freq="D")

    for i in range(n):
        location = LOCATIONS[rng.integers(0, len(LOCATIONS))]
        lat, lon = LOCATION_COORDS[location]

        # Bias a portion of readings toward unsafe values for visual variety.
        roll = rng.random()
        if roll < 0.6:                       # mostly-safe band
            ph = round(rng.uniform(6.6, 8.4), 2)
            tds = round(rng.uniform(80, 480), 0)
            turbidity = round(rng.uniform(1, 24), 1)
        elif roll < 0.85:                    # alert band
            ph = round(rng.choice([rng.uniform(6.0, 6.49), rng.uniform(8.51, 9.0)]), 2)
            tds = round(rng.uniform(500, 1000), 0)
            turbidity = round(rng.uniform(25, 50), 1)
        else:                                # critical band
            ph = round(rng.choice([rng.uniform(4.5, 5.99), rng.uniform(9.01, 10.5)]), 2)
            tds = round(rng.uniform(1001, 1900), 0)
            turbidity = round(rng.uniform(51, 120), 1)

        temperature = round(rng.uniform(26.0, 32.0), 1)
        date = dates[rng.integers(0, len(dates))]
        status = classify(ph, tds, turbidity)

        rows.append(
            {
                "id": i + 1,
                "station_name": f"WQ-{location.split()[-1][:3].upper()}-{i + 1:03d}",
                "location": location,
                "pH": ph,
                "turbidity": turbidity,
                "TDS": tds,
                "temperature": temperature,
                "lat": round(lat + rng.uniform(-0.02, 0.02), 5),
                "lon": round(lon + rng.uniform(-0.02, 0.02), 5),
                "date": date.strftime("%Y-%m-%d"),
                "status": status,
            }
        )

    df = pd.DataFrame(rows)
    df.to_csv(OUT_PATH, index=False)
    print(f"Seeded {len(df)} rows -> {OUT_PATH}")
    return df


if __name__ == "__main__":
    seed()
