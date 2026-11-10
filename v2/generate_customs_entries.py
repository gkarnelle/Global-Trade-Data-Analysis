
"""Generate synthetic customs entries for GaiAnQi Global Trading V2.

Model assumption: one entry per delivered shipment.
This is not a simulation of actual CBP filing requirements.
"""

import csv
import random
from collections import defaultdict
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"
RNG = random.Random(45)
AS_OF_DATE = date(2026, 11, 10)


def read_csv(filename):
    with (DATA / filename).open(
        newline="", encoding="utf-8"
    ) as f:
        return list(csv.DictReader(f))


def write_csv(filename, rows, columns):
    with (DATA / filename).open(
        "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def money(value):
    return Decimal(str(value)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


def main():
    shipments = read_csv("shipments.csv")
    shipment_lines = read_csv("shipment_lines.csv")
    products = {
        row["product_id"]: row
        for row in read_csv("products.csv")
    }

    po_lines = {
        row["purchase_order_line_id"]: row
        for row in read_csv("purchase_order_lines.csv")
    }

    lines_by_shipment = defaultdict(list)
    for line in shipment_lines:
        lines_by_shipment[line["shipment_id"]].append(line)

    entries = []
    entry_lines = []

    delivered = sorted(
        (
            s for s in shipments
            if s["shipment_status"] == "Delivered"
            and date.fromisoformat(
                s["estimated_arrival_date"]
            ) <= AS_OF_DATE
        ),
        key=lambda s: s["shipment_id"]
    )

    for index, shipment in enumerate(delivered, start=1):
        shipment_id = shipment["shipment_id"]
        entry_id = f"ENT-{index:06d}"
        entry_date = shipment["estimated_arrival_date"]

        shipment_value = Decimal("0.00")
        current_lines = lines_by_shipment[shipment_id]

        for line_number, shipment_line in enumerate(
            current_lines, start=1
        ):
            product_id = shipment_line["product_id"]
            product = products[product_id]

            po_line = po_lines[
                shipment_line["purchase_order_line_id"]
            ]

            invoice_value = money(
                shipment_line["shipment_line_value_usd"]
            )

            # Controlled synthetic valuation variation.
            adjustment = money(
                RNG.choice(["0.00", "0.00", "0.00", "25.00"])
            )

            declared_value = invoice_value + adjustment
            shipment_value += declared_value

            entry_lines.append({
                "entry_line_id": (
                    f"{entry_id}-{line_number:02d}"
                ),
                "entry_id": entry_id,
                "shipment_line_id": (
                    shipment_line["shipment_line_id"]
                ),
                "purchase_order_line_id": (
                    shipment_line["purchase_order_line_id"]
                ),
                "product_id": product_id,
                "entry_date": entry_date,
                "origin_code": shipment["origin_code"],
                "illustrative_hts_code": (
                    product["illustrative_hts_code"]
                ),
                "quantity_entered": (
                    shipment_line["quantity_shipped"]
                ),
                "invoice_value_usd": str(invoice_value),
                "valuation_adjustment_usd": str(adjustment),
                "entered_value_usd": str(declared_value),
                "classification_review_status": (
                    "Pending Verification"
                ),
                "valuation_review_status": (
                    "Review Required"
                    if adjustment > 0
                    else "Not Flagged"
                ),
            })

            assert int(
                shipment_line["quantity_shipped"]
            ) == int(po_line["quantity_ordered"])

        entries.append({
            "entry_id": entry_id,
            "shipment_id": shipment_id,
            "purchase_order_id": (
                shipment["purchase_order_id"]
            ),
            "supplier_id": shipment["supplier_id"],
            "entry_date": entry_date,
            "origin_code": shipment["origin_code"],
            "transport_mode": shipment["transport_mode"],
            "total_entered_value_usd": str(shipment_value),
            "entry_status": "Synthetic Historical Entry",
        })

    entry_totals = defaultdict(
        lambda: Decimal("0.00")
    )

    for line in entry_lines:
        entry_totals[line["entry_id"]] += money(
            line["entered_value_usd"]
        )

    assert len(entries) == len(delivered)

    assert len({
        row["shipment_id"] for row in entries
    }) == len(entries)

    assert all(
        money(entry["total_entered_value_usd"])
        == entry_totals[entry["entry_id"]]
        for entry in entries
    )

    assert all(
        date.fromisoformat(entry["entry_date"])
        <= AS_OF_DATE
        for entry in entries
    )

    entry_columns = [
        "entry_id", "shipment_id", "purchase_order_id",
        "supplier_id", "entry_date", "origin_code",
        "transport_mode", "total_entered_value_usd",
        "entry_status"
    ]

    line_columns = [
        "entry_line_id", "entry_id", "shipment_line_id",
        "purchase_order_line_id", "product_id",
        "entry_date", "origin_code",
        "illustrative_hts_code", "quantity_entered",
        "invoice_value_usd", "valuation_adjustment_usd",
        "entered_value_usd",
        "classification_review_status",
        "valuation_review_status"
    ]

    write_csv(
        "customs_entries.csv", entries, entry_columns
    )

    write_csv(
        "customs_entry_lines.csv",
        entry_lines, line_columns
    )

    print("GaiAnQi V2 Customs Entry Generation")
    print("-----------------------------------")
    print("Delivered shipments:", len(delivered))
    print("Customs entries:", len(entries))
    print("Customs entry lines:", len(entry_lines))
    print("All financial reconciliations passed.")
    print("All entry dates are within reporting period.")


if __name__ == "__main__":
    main()
