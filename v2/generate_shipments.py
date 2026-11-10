
"""Generate realistic synthetic shipments for GaiAnQi Global Trading V2."""

import csv
import random
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RNG = random.Random(44)

AS_OF_DATE = date(2026, 11, 10)

TRANSPORT_OPTIONS = {
    "CN": [("Ocean", 28), ("Air", 5)],
    "VN": [("Ocean", 30), ("Air", 6)],
    "KR": [("Ocean", 24), ("Air", 5)],
    "DE": [("Ocean", 21), ("Air", 5)],
    "MX": [("Truck", 5), ("Rail", 9)],
    "CA": [("Truck", 4), ("Rail", 7)],
}


def read_csv(name):
    with (DATA / name).open(
        newline="", encoding="utf-8"
    ) as f:
        return list(csv.DictReader(f))


def write_csv(name, rows):
    with (DATA / name).open(
        "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(
            f, fieldnames=list(rows[0])
        )
        writer.writeheader()
        writer.writerows(rows)


def money(value):
    return Decimal(str(value)).quantize(
        Decimal("0.01")
    )


def shipment_status(ship_date, arrival_date):
    if ship_date > AS_OF_DATE:
        return "Planned"
    if arrival_date > AS_OF_DATE:
        return "In Transit"
    return "Delivered"


def main():
    orders = read_csv("purchase_orders.csv")
    po_lines = read_csv("purchase_order_lines.csv")

    suppliers = {
        s["supplier_id"]: s
        for s in read_csv("suppliers.csv")
    }

    orders_by_id = {
        o["purchase_order_id"]: o
        for o in orders
    }

    grouped = defaultdict(list)

    for line in po_lines:
        grouped[line["purchase_order_id"]].append(
            line
        )

    shipments = []
    shipment_lines = []
    shipment_counter = 0

    for po_id, lines in sorted(grouped.items()):
        order = orders_by_id[po_id]
        supplier = suppliers[
            order["supplier_id"]
        ]

        order_date = date.fromisoformat(
            order["order_date"]
        )

        if len(lines) == 3:
            groups = [lines[:2], lines[2:]]
        else:
            groups = [lines]

        for group in groups:
            shipment_counter += 1

            shipment_id = (
                f"SHP-{shipment_counter:06d}"
            )

            origin = supplier["country_code"]

            mode, transit_days = RNG.choice(
                TRANSPORT_OPTIONS[origin]
            )

            lead_time = int(
                supplier["lead_time_days"]
            )

            ship_date = order_date + timedelta(
                days=lead_time
            )

            arrival_date = ship_date + timedelta(
                days=transit_days
            )

            freight = money(
                RNG.uniform(150, 3500)
            )

            status = shipment_status(
                ship_date, arrival_date
            )

            shipments.append({
                "shipment_id": shipment_id,
                "purchase_order_id": po_id,
                "supplier_id": order["supplier_id"],
                "origin_code": origin,
                "transport_mode": mode,
                "ship_date": ship_date.isoformat(),
                "estimated_arrival_date": (
                    arrival_date.isoformat()
                ),
                "freight_cost_usd": str(freight),
                "shipment_status": status,
            })

            for line in group:
                shipment_lines.append({
                    "shipment_line_id": (
                        f"{shipment_id}-"
                        f"{len(shipment_lines)+1:06d}"
                    ),
                    "shipment_id": shipment_id,
                    "purchase_order_line_id": (
                        line["purchase_order_line_id"]
                    ),
                    "product_id": line["product_id"],
                    "quantity_shipped": (
                        line["quantity_ordered"]
                    ),
                    "shipment_line_value_usd": (
                        line["line_value_usd"]
                    ),
                })

    assert len(shipments) == 3000
    assert len(shipment_lines) == 5000

    assert len({
        line["purchase_order_line_id"]
        for line in shipment_lines
    }) == 5000

    # Check that each shipment uses an allowed
    # transportation mode for its origin.
    for shipment in shipments:
        allowed_modes = [
            mode
            for mode, _ in TRANSPORT_OPTIONS[
                shipment["origin_code"]
            ]
        ]

        assert (
            shipment["transport_mode"]
            in allowed_modes
        )

        ship_date = date.fromisoformat(
            shipment["ship_date"]
        )

        arrival_date = date.fromisoformat(
            shipment["estimated_arrival_date"]
        )

        assert shipment["shipment_status"] == (
            shipment_status(
                ship_date, arrival_date
            )
        )

    write_csv("shipments.csv", shipments)
    write_csv(
        "shipment_lines.csv",
        shipment_lines
    )

    status_counts = defaultdict(int)

    for shipment in shipments:
        status_counts[
            shipment["shipment_status"]
        ] += 1

    print("GaiAnQi V2 Shipment Generation")
    print("------------------------------")
    print("Shipments:", len(shipments))
    print("Shipment lines:", len(shipment_lines))
    print("Reporting date:", AS_OF_DATE)

    for status, count in sorted(
        status_counts.items()
    ):
        print(f"{status}: {count}")

    print("All shipment validations passed.")


if __name__ == "__main__":
    main()
