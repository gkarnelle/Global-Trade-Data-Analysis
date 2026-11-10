
"""Generate connected synthetic shipments for GaiAnQi Global Trading."""

import csv
import random
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RNG = random.Random(44)

def read_csv(name):
    with (DATA / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def write_csv(name, rows):
    with (DATA / name).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def money(value):
    return Decimal(str(value)).quantize(Decimal("0.01"))

def main():
    orders = read_csv("purchase_orders.csv")
    po_lines = read_csv("purchase_order_lines.csv")
    suppliers = {
        s["supplier_id"]: s for s in read_csv("suppliers.csv")
    }

    orders_by_id = {
        o["purchase_order_id"]: o for o in orders
    }

    # Group lines by PO, keeping every line exactly once.
    grouped = defaultdict(list)
    for line in po_lines:
        grouped[line["purchase_order_id"]].append(line)

    shipments = []
    shipment_lines = []
    shipment_counter = 0

    for po_id, lines in sorted(grouped.items()):
        order = orders_by_id[po_id]
        supplier = suppliers[order["supplier_id"]]
        order_date = date.fromisoformat(order["order_date"])

        # Split each PO's lines into one or two shipments.
        if len(lines) == 3:
            groups = [lines[:2], lines[2:]]
        else:
            groups = [lines]

        for group in groups:
            shipment_counter += 1
            shipment_id = f"SHP-{shipment_counter:06d}"

            mode = RNG.choice(["Ocean", "Air", "Truck", "Rail"])
            lead_time = int(supplier["lead_time_days"])
            ship_date = order_date + timedelta(days=lead_time)
            transit_days = {
                "Ocean": 28,
                "Air": 5,
                "Truck": 8,
                "Rail": 14,
            }[mode]
            arrival_date = ship_date + timedelta(days=transit_days)

            freight = money(RNG.uniform(150, 3500))

            shipments.append({
                "shipment_id": shipment_id,
                "purchase_order_id": po_id,
                "supplier_id": order["supplier_id"],
                "origin_code": supplier["country_code"],
                "transport_mode": mode,
                "ship_date": ship_date.isoformat(),
                "estimated_arrival_date": arrival_date.isoformat(),
                "freight_cost_usd": str(freight),
                "shipment_status": "Delivered",
            })

            for line in group:
                shipment_lines.append({
                    "shipment_line_id": (
                        f"{shipment_id}-{len(shipment_lines)+1:06d}"
                    ),
                    "shipment_id": shipment_id,
                    "purchase_order_line_id": line[
                        "purchase_order_line_id"
                    ],
                    "product_id": line["product_id"],
                    "quantity_shipped": line["quantity_ordered"],
                    "shipment_line_value_usd": line["line_value_usd"],
                })

    assert len(shipments) == 3000
    assert len(shipment_lines) == 5000
    assert len({
        line["purchase_order_line_id"] for line in shipment_lines
    }) == 5000

    write_csv("shipments.csv", shipments)
    write_csv("shipment_lines.csv", shipment_lines)

    print("Generated", len(shipments), "shipments.")
    print("Generated", len(shipment_lines), "shipment lines.")
    print("All PO lines allocated exactly once.")

if __name__ == "__main__":
    main()
