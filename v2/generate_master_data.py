
"""Generate synthetic supplier and product master data for GaiAnQi."""

import csv
import random
from pathlib import Path

RNG = random.Random(42)
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

COUNTRIES = [
    ("China", "CN"),
    ("Mexico", "MX"),
    ("Canada", "CA"),
    ("Germany", "DE"),
    ("Vietnam", "VN"),
    ("South Korea", "KR"),
]

PRODUCTS = [
    ("Steel fasteners", "Steel", "7318.15.0000"),
    ("Aluminum components", "Aluminum", "7616.99.5190"),
    ("Electronic control units", "Electronics", "8537.10.9170"),
    ("Industrial pumps", "Machinery", "8413.70.2004"),
    ("Solar panels", "Solar", "8541.43.0010"),
    ("Industrial batteries", "Batteries", "8507.60.0020"),
]

def save_csv(filename, rows):
    path = DATA_DIR / filename
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Created {path.name}: {len(rows)} records")

def generate_suppliers():
    suppliers = []
    for i in range(1, 41):
        country, code = COUNTRIES[(i - 1) % len(COUNTRIES)]
        suppliers.append({
            "supplier_id": f"SUP-{i:03d}",
            "supplier_name": f"GaiAnQi Partner {i:03d}",
            "country": country,
            "country_code": code,
            "lead_time_days": RNG.randint(12, 65),
            "on_time_delivery_pct": round(RNG.uniform(78, 99), 1),
            "supplier_risk_tier": RNG.choice(["Low", "Medium", "High"]),
            "supplier_status": "Active",
        })
    return suppliers

def generate_products():
    products = []
    for i in range(1, 61):
        description, category, hts = PRODUCTS[(i - 1) % len(PRODUCTS)]
        products.append({
            "product_id": f"PRD-{i:03d}",
            "product_description": f"{description} - Model {i:03d}",
            "product_category": category,
            "illustrative_hts_code": hts,
            "unit_cost_usd": round(RNG.uniform(15, 850), 2),
            "classification_review_status": "Pending Verification",
        })
    return products

def main():
    suppliers = generate_suppliers()
    products = generate_products()

    assert len(suppliers) == 40
    assert len(products) == 60
    assert len({s["supplier_id"] for s in suppliers}) == 40
    assert len({p["product_id"] for p in products}) == 60

    save_csv("suppliers.csv", suppliers)
    save_csv("products.csv", products)
    print("GaiAnQi master data generated successfully.")

if __name__ == "__main__":
    main()
