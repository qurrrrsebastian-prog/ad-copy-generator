"""Seed 30 dummy ad-copy records to data/ad_copies.csv. Author: Avatar Putra Sigit

Deterministic (seed=42) so analytics and the empty-state preview are stable.
Run directly (`python data/seeder.py`) or via core.database.get_dummy_data.
"""
import os
import random
from datetime import datetime, timedelta

import pandas as pd

_DATA_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(_DATA_DIR, "ad_copies.csv")

FRAMEWORKS = ["AIDA", "PAS", "4U", "Storytelling"]
TONES = ["Professional", "Casual", "Urgent", "Friendly", "Luxury"]

_PRODUCTS = [
    ("RKARI Glass Cleaning", "Property", "Kaca gedung tinggi kusam & sulit dibersihkan"),
    ("KopiKita Roastery", "F&B", "Margin tipis karena bahan baku kopi naik terus"),
    ("MediTrack Pro", "Health", "Antrian pasien berantakan tanpa sistem terpusat"),
    ("CloudLedger", "Tech", "Tim finance kewalahan tutup buku tiap bulan"),
    ("UrbanThread", "Fashion", "Stok lambat terjual karena promosi kurang menarik"),
    ("SafeBuild AMC", "B2B", "Maintenance gedung reaktif & biaya darurat membengkak"),
    ("FreshMart Daily", "B2C", "Pelanggan ragu belanja online karena takut tak segar"),
    ("DataPulse Analytics", "Tech", "Keputusan bisnis lambat tanpa dashboard real-time"),
    ("Villa Serenity", "Property", "Okupansi rendah di musim sepi"),
    ("GlowDerma Clinic", "Health", "Pasien skincare bingung memilih treatment yang tepat"),
]

_CTAS = ["Hubungi Kami", "Dapatkan Penawaran", "Pesan Sekarang", "Download Gratis", "Daftar Trial"]


def _make_copy(product: str, audience: str, pain: str, framework: str, tone: str) -> str:
    """Build a short ready-made ad copy string for the seed dataset."""
    if framework == "AIDA":
        return (f"{product}: solusi {audience} yang terukur. {pain}? "
                f"Kami hadir dengan pendekatan {tone.lower()} untuk hasil nyata. Action sekarang.")
    if framework == "PAS":
        return (f"Masih terganggu: {pain}? Dibiarkan, masalah ini menggerus biaya & reputasi. "
                f"{product} menyelesaikannya secara {tone.lower()}.")
    if framework == "4U":
        return (f"{product} — berguna, mendesak, unik untuk {audience}. {pain} teratasi "
                f"dengan hasil terukur dalam 30 hari. Gaya {tone.lower()}.")
    return (f"Dulu mereka berhadapan dengan {pain}. Sampai menemukan {product}. "
            f"Pendekatan {tone.lower()} mengubah segalanya — kini giliran Anda.")


def seed(n: int = 30) -> pd.DataFrame:
    """Generate and persist `n` dummy records (default 30). Returns the DataFrame."""
    random.seed(42)
    rows = []
    base_date = datetime(2026, 6, 16)
    for i in range(1, n + 1):
        product, audience, pain = _PRODUCTS[(i - 1) % len(_PRODUCTS)]
        framework = random.choice(FRAMEWORKS)
        tone = random.choice(TONES)
        cta = random.choice(_CTAS)
        date_created = (base_date - timedelta(days=random.randint(0, 29))).strftime("%Y-%m-%d")
        rows.append({
            "id": i,
            "product_name": product,
            "target_audience": audience,
            "pain_point": pain,
            "ad_copy": _make_copy(product, audience, pain, framework, tone),
            "cta": cta,
            "framework": framework,
            "tone": tone,
            "date_created": date_created,
        })
    df = pd.DataFrame(rows)
    os.makedirs(_DATA_DIR, exist_ok=True)
    df.to_csv(CSV_PATH, index=False)
    return df


if __name__ == "__main__":
    out = seed()
    print(f"Seeded {len(out)} records -> {CSV_PATH}")
