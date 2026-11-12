
"""GaiAnQi Global Trading V2 - Trade Operations Analytics.

Calculates reproducible KPIs from connected synthetic
procurement, logistics, customs, and compliance datasets.

No external Python packages required.
"""

import csv
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUTPUT = ROOT / "analytics"
AS_OF_DATE = "2026-11-10"

ZERO = Decimal("0.00")


def read_csv(filename):
    path = DATA / filename

    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(filename, columns, rows):
    OUTPUT.mkdir(parents=True, exist_ok=True)

    with (OUTPUT / filename).open(
        "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def amount(value):
    return Decimal(str(value))


def money(value):
    return str(value.quantize(Decimal("0.01")))


def unique_index(rows, key):
    result = {row[key]: row for row in rows}
    if len(result) != len(rows):
        raise ValueError(f"Duplicate IDs found: {key}")
    return result


def main():
    suppliers = read_csv("suppliers.csv")
    products = read_csv("products.csv")
    orders = read_csv("purchase_orders.csv")
    po_lines = read_csv("purchase_order_lines.csv")
    shipments = read_csv("shipments.csv")
    shipment_lines = read_csv("shipment_lines.csv")
    entries = read_csv("customs_entries.csv")
    entry_lines = read_csv("customs_entry_lines.csv")
    exceptions = read_csv("compliance_exceptions.csv")

    supplier_by_id = unique_index(
        suppliers, "supplier_id"
    )
    product_by_id = unique_index(
        products, "product_id"
    )
    order_by_id = unique_index(
        orders, "purchase_order_id"
    )
    po_line_by_id = unique_index(
        po_lines, "purchase_order_line_id"
    )
    shipment_by_id = unique_index(
        shipments, "shipment_id"
    )
    shipment_line_by_id = unique_index(
        shipment_lines, "shipment_line_id"
    )
    entry_by_id = unique_index(
        entries, "entry_id"
    )
    entry_line_by_id = unique_index(
        entry_lines, "entry_line_id"
    )
    unique_index(exceptions, "exception_id")

    # 1. Validate purchasing relationships.
    po_totals = defaultdict(lambda: ZERO)

    for line in po_lines:
        assert line["purchase_order_id"] in order_by_id
        assert line["product_id"] in product_by_id

        expected = (
            amount(line["quantity_ordered"])
            * amount(line["unit_cost_usd"])
        )

        assert expected == amount(
            line["line_value_usd"]
        )

        po_totals[line["purchase_order_id"]] += expected

    for order in orders:
        assert order["supplier_id"] in supplier_by_id
        assert po_totals[order["purchase_order_id"]] == (
            amount(order["total_order_value_usd"])
        )

    # 2. Validate shipment relationships.
    shipped_po_lines = set()

    for shipment in shipments:
        order = order_by_id[shipment["purchase_order_id"]]

        assert shipment["supplier_id"] == (
            order["supplier_id"]
        )

    for line in shipment_lines:
        shipment = shipment_by_id[line["shipment_id"]]
        po_line = po_line_by_id[
            line["purchase_order_line_id"]
        ]

        assert shipment["purchase_order_id"] == (
            po_line["purchase_order_id"]
        )
        assert line["product_id"] == po_line["product_id"]
        assert amount(line["quantity_shipped"]) == (
            amount(po_line["quantity_ordered"])
        )
        assert amount(
            line["shipment_line_value_usd"]
        ) == amount(po_line["line_value_usd"])

        shipped_po_lines.add(
            line["purchase_order_line_id"]
        )

    assert len(shipment_lines) == len(po_lines)
    assert shipped_po_lines == set(po_line_by_id)

    # 3. Reconcile customs entry values.
    entry_totals = defaultdict(lambda: ZERO)
    total_invoice = ZERO
    total_adjustments = ZERO
    total_entered = ZERO

    for line in entry_lines:
        entry = entry_by_id[line["entry_id"]]
        shipment_line = shipment_line_by_id[
            line["shipment_line_id"]
        ]
        shipment = shipment_by_id[entry["shipment_id"]]

        assert shipment["shipment_status"] == "Delivered"
        assert shipment_line["shipment_id"] == (
            entry["shipment_id"]
        )
        assert line["product_id"] == (
            shipment_line["product_id"]
        )
        assert line["purchase_order_line_id"] == (
            shipment_line["purchase_order_line_id"]
        )
        assert amount(line["quantity_entered"]) == (
            amount(shipment_line["quantity_shipped"])
        )

        invoice = amount(line["invoice_value_usd"])
        adjustment = amount(
            line["valuation_adjustment_usd"]
        )
        entered = amount(line["entered_value_usd"])

        assert invoice + adjustment == entered

        entry_totals[line["entry_id"]] += entered
        total_invoice += invoice
        total_adjustments += adjustment
        total_entered += entered

    for entry in entries:
        shipment = shipment_by_id[entry["shipment_id"]]

        assert shipment["shipment_status"] == "Delivered"
        assert entry["purchase_order_id"] == (
            shipment["purchase_order_id"]
        )
        assert entry["supplier_id"] == (
            shipment["supplier_id"]
        )
        assert entry["entry_date"] <= AS_OF_DATE

        assert entry_totals[entry["entry_id"]] == (
            amount(entry["total_entered_value_usd"])
        )

    assert total_invoice + total_adjustments == (
        total_entered
    )

    assert total_entered == sum(
        (
            amount(e["total_entered_value_usd"])
            for e in entries
        ),
        ZERO
    )

    # 4. Validate compliance exception references.
    for exception in exceptions:
        line = entry_line_by_id[
            exception["entry_line_id"]
        ]

        assert exception["entry_id"] == line["entry_id"]

        if exception["exception_code"] != "MISSING_ENTRY":
            assert exception["entry_id"] in entry_by_id

    # 5. Executive KPIs.
    delivered_ids = {
        s["shipment_id"]
        for s in shipments
        if s["shipment_status"] == "Delivered"
    }

    entry_shipment_ids = {
        e["shipment_id"] for e in entries
    }

    assert entry_shipment_ids == delivered_ids
    assert len(entries) == len(delivered_ids)

    kpis = {
        "suppliers": len(suppliers),
        "products": len(products),
        "purchase_orders": len(orders),
        "purchase_order_lines": len(po_lines),
        "shipments": len(shipments),
        "shipment_lines": len(shipment_lines),
        "customs_entries": len(entries),
        "customs_entry_lines": len(entry_lines),
        "compliance_exceptions": len(exceptions),
        "purchase_order_value_usd": money(
            sum(
                (
                    amount(o["total_order_value_usd"])
                    for o in orders
                ),
                ZERO
            )
        ),
        "customs_invoice_value_usd": money(
            total_invoice
        ),
        "valuation_adjustments_usd": money(
            total_adjustments
        ),
        "total_entered_value_usd": money(
            total_entered
        ),
        "entries_with_exceptions": len({
            e["entry_id"] for e in exceptions
        }),
        "reporting_as_of_date": AS_OF_DATE,
    }

    write_csv(
        "executive_kpis.csv",
        ["metric", "value"],
        [
            {"metric": key, "value": value}
            for key, value in kpis.items()
        ]
    )

    # 6. Shipment status summary.
    status_counts = Counter(
        s["shipment_status"] for s in shipments
    )

    write_csv(
        "shipment_status_summary.csv",
        ["shipment_status", "shipment_count"],
        [
            {
                "shipment_status": status,
                "shipment_count": count
            }
            for status, count in sorted(
                status_counts.items()
            )
        ]
    )

    # 7. Transportation mode summary.
    mode_counts = Counter(
        s["transport_mode"] for s in shipments
    )

    write_csv(
        "transport_mode_summary.csv",
        ["transport_mode", "shipment_count"],
        [
            {
                "transport_mode": mode,
                "shipment_count": count
            }
            for mode, count in sorted(
                mode_counts.items()
            )
        ]
    )

    # 8. Supplier activity and exposure.
    supplier_shipments = Counter(
        s["supplier_id"] for s in shipments
    )

    supplier_entries = Counter(
        e["supplier_id"] for e in entries
    )

    supplier_values = defaultdict(lambda: ZERO)

    for entry in entries:
        supplier_values[entry["supplier_id"]] += (
            amount(entry["total_entered_value_usd"])
        )

    supplier_summary = []

    for supplier in suppliers:
        supplier_id = supplier["supplier_id"]

        supplier_summary.append({
            "supplier_id": supplier_id,
            "supplier_name": supplier["supplier_name"],
            "country": supplier["country"],
            "supplier_risk_tier": (
                supplier["supplier_risk_tier"]
            ),
            "master_on_time_delivery_pct": (
                supplier["on_time_delivery_pct"]
            ),
            "shipment_count": (
                supplier_shipments[supplier_id]
            ),
            "customs_entry_count": (
                supplier_entries[supplier_id]
            ),
            "total_entered_value_usd": money(
                supplier_values[supplier_id]
            ),
        })

    write_csv(
        "supplier_summary.csv",
        [
            "supplier_id",
            "supplier_name",
            "country",
            "supplier_risk_tier",
            "master_on_time_delivery_pct",
            "shipment_count",
            "customs_entry_count",
            "total_entered_value_usd",
        ],
        supplier_summary
    )

    # 9. Compliance exception summaries.
    category_counts = Counter(
        e["exception_category"] for e in exceptions
    )

    severity_counts = Counter(
        e["severity"] for e in exceptions
    )

    review_counts = Counter(
        e["review_status"] for e in exceptions
    )

    for filename, field, counts in [
        (
            "exception_category_summary.csv",
            "exception_category",
            category_counts
        ),
        (
            "exception_severity_summary.csv",
            "severity",
            severity_counts
        ),
        (
            "exception_status_summary.csv",
            "review_status",
            review_counts
        ),
    ]:
        write_csv(
            filename,
            [field, "exception_count"],
            [
                {
                    field: name,
                    "exception_count": count
                }
                for name, count in sorted(
                    counts.items()
                )
            ]
        )

    # 10. Final output.
    print("GAIANQI GLOBAL TRADING - V2 ANALYTICS")
    print("------------------------------------")

    for metric, value in kpis.items():
        print(f"{metric}: {value}")

    print("\nAnalytics files generated:")
    for path in sorted(OUTPUT.glob("*.csv")):
        print(f"  {path.name}")

    print("\nAll analytics validations passed.")


if __name__ == "__main__":
    main()
