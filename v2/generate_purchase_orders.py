
"""Generate connected synthetic purchase orders for GaiAnQi."""

import csv
import random
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RNG = random.Random(43)

def read_csv(filename):
    with (DATA / filename).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def write_csv(filename, rows):
    with (DATA / filename).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def money(value):
    return Decimal(str(value)).quantize(Decimal("0.01"))

def main():
    suppliers = read_csv("suppliers.csv")
    products = read_csv("products.csv")

    assert len(suppliers) == 40
    assert len(products) == 60

    orders = []
    lines = []
    start = date(2022, 1, 1)
    end = date(2026, 10, 31)
    day_range = (end - start).days

    # Exactly 5,000 lines across 2,000 orders.
    line_counts = [2] * 1000 + [3] * 1000
    RNG.shuffle(line_counts)

    for i, count in enumerate(line_counts, start=1):
        supplier = RNG.choice(suppliers)
        order_date = start + timedelta(days=RNG.randint(0, day_range))
        po_id = f"PO-{order_date.year}-{i:05d}"
        total = Decimal("0.00")

        for line_num, product in enumerate(
            RNG.sample(products, count), start=1
        ):
            quantity = RNG.randint(10, 400)
            unit_cost = money(product["unit_cost_usd"])
            line_value = unit_cost * quantity
            total += line_value

            lines.append({
                "purchase_order_line_id": f"{po_id}-{line_num:02d}",
                "purchase_order_id": po_id,
                "product_id": product["product_id"],
                "quantity_ordered": quantity,
                "unit_cost_usd": str(unit_cost),
                "line_value_usd": str(line_value),
            })

        orders.append({
            "purchase_order_id": po_id,
            "supplier_id": supplier["supplier_id"],
            "order_date": order_date.isoformat(),
            "currency": "USD",
            "purchase_order_status": "Approved",
            "total_order_value_usd": str(total),
        })

    totals = defaultdict(lambda: Decimal("0.00"))
    for line in lines:
        totals[line["purchase_order_id"]] += money(line["line_value_usd"])

    assert len(orders) == 2000
    assert len(lines) == 5000
    assert all(
        money(order["total_order_value_usd"]) ==
        totals[order["purchase_order_id"]]
        for order in orders
    )

    write_csv("purchase_orders.csv", orders)
    write_csv("purchase_order_lines.csv", lines)
    print("Generated 2,000 purchase orders and 5,000 lines.")
    print("All purchase order totals reconciled.")

if __name__ == "__main__":
    main()
