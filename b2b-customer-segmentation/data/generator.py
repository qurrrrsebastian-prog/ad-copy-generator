"""Generate synthetic B2B customer data for segmentation. Author: Avatar Putra Sigit"""
import os
import random

import pandas as pd

def generate_customers(n: int = 200) -> pd.DataFrame:
    """Generate B2B customer records for RKARI-like service business."""
    try:
        random.seed(42)
        industries = ["Property", "Retail", "Manufacturing", "Hospital", "Office Building", "Hotel"]
        data = []
        for i in range(n):
            company_size = random.randint(10, 500)
            contract_value = random.randint(5_000_000, 150_000_000)
            service_frequency = random.randint(1, 12)
            satisfaction = round(random.uniform(3.0, 5.0), 1)
            last_order_days = random.randint(7, 365)
            years_client = random.randint(0, 5)
            data.append({
                "id": i + 1,
                "company_name": f"Company_{i+1}",
                "industry": random.choice(industries),
                "company_size": company_size,
                "contract_value": contract_value,
                "service_frequency": service_frequency,
                "satisfaction_score": satisfaction,
                "last_order_days": last_order_days,
                "years_as_client": years_client
            })
        df = pd.DataFrame(data)
        out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "customers.csv")
        df.to_csv(out_path, index=False)
        print(f"Generated {n} B2B customers to {out_path}")
        return df
    except Exception as e:
        print(f"Error generating customers: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    generate_customers()
