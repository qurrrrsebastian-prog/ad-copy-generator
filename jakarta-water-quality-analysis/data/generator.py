"""Generate synthetic Jakarta water quality data. Author: Avatar Putra Sigit"""
import os
import random
from datetime import datetime, timedelta

import pandas as pd

def generate_water_data(n: int = 500) -> pd.DataFrame:
    """Generate realistic water quality data for Jakarta districts."""
    try:
        random.seed(42)
        districts = ["Jakarta Selatan", "Jakarta Barat", "Jakarta Pusat", "Jakarta Timur", "Jakarta Utara"]
        data = []
        for i in range(n):
            district = random.choice(districts)
            base_ph = 7.0
            if district in ["Jakarta Utara", "Jakarta Timur"]:
                base_ph = 6.5
            ph = round(random.uniform(base_ph - 0.8, base_ph + 0.8), 2)
            turbidity = round(random.uniform(2, 45), 1)
            tds = random.randint(50, 350)
            dissolved_oxygen = round(random.uniform(3.0, 8.5), 1)
            temperature = round(random.uniform(26.0, 32.0), 1)
            days_ago = random.randint(0, 365)
            date = datetime.now() - timedelta(days=days_ago)
            data.append({
                "id": i + 1,
                "date": date.strftime("%Y-%m-%d"),
                "district": district,
                "ph": ph,
                "turbidity_ntu": turbidity,
                "tds_mg_l": tds,
                "dissolved_oxygen_mg_l": dissolved_oxygen,
                "temperature_c": temperature
            })
        df = pd.DataFrame(data)
        out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jakarta_water_quality.csv")
        df.to_csv(out_path, index=False)
        print(f"Generated {n} records to {out_path}")
        return df
    except Exception as e:
        print(f"Error generating data: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    generate_water_data()
