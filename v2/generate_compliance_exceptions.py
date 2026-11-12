
"""GaiAnQi Global Trading V2 - Compliance Exception Engine.

Generates reproducible, synthetic compliance review exceptions.
Flags indicate potential risks, not confirmed legal violations.
"""

import csv
import hashlib
from collections import Counter
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"
AS_OF_DATE = date(2026, 11, 10)

OUTPUT_COLUMNS = [
    "exception_id",
    "entry_id",
    "entry_line_id",
    "shipment_id",
    "purchase_order_id",
    "supplier_id",
    "product_id",
    "exception_category",
    "exception_code",
    "severity",
    "exception_reason",
    "recommended_action",
    "review_status",
    "detected_as_of_date",
]


def read_csv(filename):
    with (DATA / filename).open(
        newline="", encoding="utf-8"
    ) as file:
        return list(csv.DictReader(file))


def stable_bucket(value, modulo=100):
    """Stable pseudo-random bucket independent of row ordering."""
    digest = hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()
    return int(digest[:12], 16) % modulo


def decimal_or_none(value):
    try:
        if value is None or str(value).strip() == "":
            return None
        number = Decimal(str(value))
        return number if number.is_finite() else None
    except (InvalidOperation, ValueError):
        return None


def main():
    entries = read_csv("customs_entries.csv")
    lines = read_csv("customs_entry_lines.csv")
    shipments = read_csv("shipments.csv")
    suppliers = read_csv("suppliers.csv")
    products = read_csv("products.csv")

    entry_by_id = {
        row["entry_id"]: row for row in entries
    }
    shipment_by_id = {
        row["shipment_id"]: row for row in shipments
    }
    supplier_by_id = {
        row["supplier_id"]: row for row in suppliers
    }
    product_by_id = {
        row["product_id"]: row for row in products
    }

    assert len(entry_by_id) == len(entries)
    assert len(shipment_by_id) == len(shipments)
    assert len(supplier_by_id) == len(suppliers)
    assert len(product_by_id) == len(products)

    exceptions = []
    seen = set()

    def add_exception(line, entry, code, category,
                      severity, reason, action):
        unique_key = (line["entry_line_id"], code)

        if unique_key in seen:
            return

        seen.add(unique_key)

        exceptions.append({
            "exception_id": "",
            "entry_id": line["entry_id"],
            "entry_line_id": line["entry_line_id"],
            "shipment_id": entry["shipment_id"],
            "purchase_order_id": (
                entry["purchase_order_id"]
            ),
            "supplier_id": entry["supplier_id"],
            "product_id": line["product_id"],
            "exception_category": category,
            "exception_code": code,
            "severity": severity,
            "exception_reason": reason,
            "recommended_action": action,
            "review_status": "Open - Pending Analyst Review",
            "detected_as_of_date": AS_OF_DATE.isoformat(),
        })

    for line in sorted(
        lines, key=lambda row: row["entry_line_id"]
    ):
        entry = entry_by_id.get(line["entry_id"])

        # Missing parent entries cannot inherit parent IDs.
        # Record the problem separately with blank references.
        if entry is None:
            exceptions.append({
                "exception_id": "",
                "entry_id": line["entry_id"],
                "entry_line_id": line["entry_line_id"],
                "shipment_id": "",
                "purchase_order_id": "",
                "supplier_id": "",
                "product_id": line["product_id"],
                "exception_category": "Data Integrity",
                "exception_code": "MISSING_ENTRY",
                "severity": "Critical",
                "exception_reason": (
                    "Customs entry line has no matching entry header."
                ),
                "recommended_action": (
                    "Reconcile the entry line to its source entry."
                ),
                "review_status": "Open - Pending Analyst Review",
                "detected_as_of_date": AS_OF_DATE.isoformat(),
            })
            continue

        product = product_by_id.get(line["product_id"])
        shipment = shipment_by_id.get(entry["shipment_id"])
        supplier = supplier_by_id.get(entry["supplier_id"])

        # 1. Classification review
        if (
            product is None
            or product["classification_review_status"]
            != "Verified"
        ):
            add_exception(
                line, entry,
                "HTS_REVIEW",
                "HTS Classification",
                "Medium",
                "Product HTS classification requires verification.",
                "Review product specifications, HTS rationale, "
                "and classification documentation."
            )

        # 2. Valuation adjustment review
        adjustment = decimal_or_none(
            line["valuation_adjustment_usd"]
        )

        if adjustment is not None and adjustment != 0:
            add_exception(
                line, entry,
                "VALUATION_ADJUSTMENT",
                "Customs Valuation",
                "High",
                "Entered value includes a synthetic adjustment.",
                "Verify the adjustment basis and supporting "
                "customs valuation documentation."
            )

        # 3. Origin documentation review
        # Synthetic selection, not an origin-based legal finding.
        if stable_bucket(
            line["entry_line_id"] + "|origin"
        ) < 12:
            add_exception(
                line, entry,
                "ORIGIN_DOCUMENT_REVIEW",
                "Country of Origin",
                "Medium",
                "Origin documentation selected for sample review.",
                "Verify origin evidence and any applicable "
                "preferential treatment claims."
            )

        # 4. Synthetic missing-document scenario
        if stable_bucket(
            line["entry_line_id"] + "|document"
        ) < 8:
            add_exception(
                line, entry,
                "DOCUMENTATION_GAP",
                "Documentation",
                "High",
                "Synthetic scenario: required supporting "
                "document is marked unavailable for review.",
                "Request supporting documentation and "
                "record the analyst's resolution."
            )

        # 5. Referential and numerical integrity
        issues = []

        if product is None:
            issues.append("Unknown product reference")

        if shipment is None:
            issues.append("Unknown shipment reference")
        else:
            if (
                shipment["purchase_order_id"]
                != entry["purchase_order_id"]
            ):
                issues.append("Purchase order reference mismatch")

            if (
                shipment["supplier_id"]
                != entry["supplier_id"]
            ):
                issues.append("Supplier reference mismatch")

            if (
                shipment["origin_code"]
                != line["origin_code"]
            ):
                issues.append("Origin mismatch")

        if supplier is None:
            issues.append("Unknown supplier reference")

        quantity = decimal_or_none(
            line["quantity_entered"]
        )
        invoice = decimal_or_none(
            line["invoice_value_usd"]
        )
        entered = decimal_or_none(
            line["entered_value_usd"]
        )

        if quantity is None or quantity <= 0:
            issues.append("Invalid entered quantity")

        if invoice is None or invoice < 0:
            issues.append("Invalid invoice value")

        if entered is None or entered < 0:
            issues.append("Invalid entered value")

        if adjustment is None:
            issues.append("Invalid valuation adjustment")

        if (
            invoice is not None
            and adjustment is not None
            and entered is not None
            and invoice + adjustment != entered
        ):
            issues.append("Entered value reconciliation mismatch")

        if issues:
            add_exception(
                line, entry,
                "DATA_INTEGRITY",
                "Data Integrity",
                "Critical",
                "; ".join(issues),
                "Investigate and correct the source data "
                "before relying on the affected record."
            )

    exceptions.sort(
        key=lambda row: (
            row["entry_line_id"],
            row["exception_code"]
        )
    )

    for index, row in enumerate(exceptions, start=1):
        row["exception_id"] = f"EXC-{index:06d}"

    assert len({
        row["exception_id"] for row in exceptions
    }) == len(exceptions)

    assert len({
        (row["entry_line_id"], row["exception_code"])
        for row in exceptions
    }) == len(exceptions)

    DATA.mkdir(parents=True, exist_ok=True)

    with (DATA / "compliance_exceptions.csv").open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file, fieldnames=OUTPUT_COLUMNS
        )
        writer.writeheader()
        writer.writerows(exceptions)

    print("GaiAnQi V2 Compliance Exception Engine")
    print("--------------------------------------")
    print("Customs entry lines analyzed:", len(lines))
    print("Exceptions generated:", len(exceptions))
    print("Reporting date:", AS_OF_DATE)

    print("\nExceptions by category:")
    for category, count in sorted(
        Counter(
            row["exception_category"]
            for row in exceptions
        ).items()
    ):
        print(f"  {category}: {count}")

    print("\nExceptions by severity:")
    for severity, count in sorted(
        Counter(
            row["severity"]
            for row in exceptions
        ).items()
    ):
        print(f"  {severity}: {count}")

    print("\nAll exception ID validations passed.")


if __name__ == "__main__":
    main()
