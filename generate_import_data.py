
"""Generate reproducible synthetic GaiAnQi import transactions, 2022–2026.

All transactions, sourcing decisions, and financial values are fictional.
HTS codes are illustrative and require independent classification review.
This script does not determine actual tariff applicability or duty rates.
"""

import csv
import random
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "import_entries.csv"

SEED = 42
rng = random.Random(SEED)

IMPORTER_NAME = "GaiAnQi Global Trading"
TOTAL_TRANSACTIONS = 500

START_DATE = date(2022, 1, 1)
CUTOFF_DATE = date(2026, 10, 29)

# Annual transaction counts are illustrative business-volume assumptions.
# They total 500 and represent growth followed by a partial-year 2026.
ANNUAL_COUNTS = {
    2022: 80,
    2023: 90,
    2024: 100,
    2025: 120,
    2026: 110,
}

# Annual entered-value multipliers relative to the 2022 baseline.
# These are fictional purchasing assumptions, NOT inflation statistics.
VALUE_MULTIPLIERS = {
    2022: 1.00,
    2023: 1.04,
    2024: 1.08,
    2025: 1.14,
    2026: 1.19,
}

# Country order must match each row of annual sourcing percentages.
ORIGINS = [
    ("China", "CN"),
    ("Mexico", "MX"),
    ("Canada", "CA"),
    ("Germany", "DE"),
    ("Vietnam", "VN"),
    ("South Korea", "KR"),
]

# Approved annual transaction-count shares, in percentages.
# These do NOT represent import-dollar shares.
SOURCING_MIX = {
    2022: [40, 20, 18, 10, 7, 5],
    2023: [37, 22, 19, 10, 7, 5],
    2024: [33, 24, 20, 10, 8, 5],
    2025: [25, 27, 21, 10, 10, 7],
    2026: [22, 28, 22, 10, 11, 7],
}

# Existing illustrative product catalog and HTS values.
PRODUCTS = [
    ("Steel fasteners", "7318.15.0000", "Steel"),
    ("Aluminum components", "7616.99.5190", "Aluminum"),
    ("Electronic control units", "8537.10.9170", "Electronics"),
    ("Industrial pumps", "8413.70.2004", "Machinery"),
    ("Solar panels", "8541.43.0010", "Solar"),
    ("Industrial batteries", "8507.60.0020", "Batteries"),
]

FIELDNAMES = [
    "entry_id",
    "importer_name",
    "entry_date",
    "country_of_origin",
    "origin_code",
    "supplier",
    "product_description",
    "product_category",
    "hts_code",
    "entered_value_usd",
    "quantity",
    "entry_type",
    "review_status",
]


def validate_configuration():
    """Reject inconsistent or invalid simulation assumptions."""
    years = set(range(2022, 2027))

    if set(ANNUAL_COUNTS) != years:
        raise ValueError("Annual counts must cover 2022–2026.")

    if set(VALUE_MULTIPLIERS) != years:
        raise ValueError("Value multipliers must cover 2022–2026.")

    if set(SOURCING_MIX) != years:
        raise ValueError("Sourcing mix must cover 2022–2026.")

    if sum(ANNUAL_COUNTS.values()) != TOTAL_TRANSACTIONS:
        raise ValueError("Annual transaction counts must total 500.")

    if any(count <= 0 for count in ANNUAL_COUNTS.values()):
        raise ValueError("Annual transaction counts must be positive.")

    if any(value <= 0 for value in VALUE_MULTIPLIERS.values()):
        raise ValueError("Annual value multipliers must be positive.")

    if len(ORIGINS) != 6:
        raise ValueError("Expected six countries of origin.")

    if len({code for _, code in ORIGINS}) != len(ORIGINS):
        raise ValueError("Duplicate country codes detected.")

    if START_DATE > CUTOFF_DATE:
        raise ValueError("Start date must precede cutoff date.")

    for year, weights in SOURCING_MIX.items():
        if len(weights) != len(ORIGINS):
            raise ValueError(f"Incorrect origin count for {year}.")

        if any(
            not isinstance(weight, int) or weight < 0
            for weight in weights
        ):
            raise ValueError(f"Invalid sourcing percentage in {year}.")

        if sum(weights) != 100:
            raise ValueError(
                f"Sourcing percentages for {year} must total 100."
            )


def allocate_origin_counts(year):
    """Convert approved percentages into exact integer row counts.

    Largest-remainder allocation avoids losing or creating rows
    through independent rounding. Ties follow ORIGINS order.
    """
    count = ANNUAL_COUNTS[year]
    percentages = SOURCING_MIX[year]

    quotas = [count * pct / 100 for pct in percentages]
    allocations = [int(quota) for quota in quotas]

    remaining = count - sum(allocations)

    ranked = sorted(
        range(len(ORIGINS)),
        key=lambda i: (-(quotas[i] - allocations[i]), i),
    )

    for i in ranked[:remaining]:
        allocations[i] += 1

    if sum(allocations) != count:
        raise ValueError(f"Origin allocation failed for {year}.")

    return allocations


def random_entry_date(year):
    """Choose a date inside the year and permitted data window."""
    first = max(date(year, 1, 1), START_DATE)
    last = min(date(year, 12, 31), CUTOFF_DATE)

    if first > last:
        raise ValueError(f"No permitted entry dates for {year}.")

    day_offset = rng.randint(0, (last - first).days)
    return first + timedelta(days=day_offset)


def generate_transactions():
    """Generate all five years while preserving the existing schema."""
    rows = []
    next_entry_id = 1

    for year in sorted(ANNUAL_COUNTS):
        allocations = allocate_origin_counts(year)

        # Allocate exact origin counts, then randomize their order.
        year_origins = []
        for origin, count in zip(ORIGINS, allocations):
            year_origins.extend([origin] * count)

        rng.shuffle(year_origins)

        for country, origin_code in year_origins:
            product, hts, category = rng.choice(PRODUCTS)

            # Baseline values follow the existing $15K–$250K range.
            # Multipliers introduce illustrative year-over-year growth.
            base_value = rng.uniform(15000, 250000)
            entered_value = round(
                base_value * VALUE_MULTIPLIERS[year], 2
            )

            rows.append({
                "entry_id": f"ENT-{next_entry_id:04d}",
                "importer_name": IMPORTER_NAME,
                "entry_date": random_entry_date(year).isoformat(),
                "country_of_origin": country,
                "origin_code": origin_code,
                "supplier": f"Supplier-{rng.randint(1, 25):02d}",
                "product_description": product,
                "product_category": category,
                "hts_code": hts,
                "entered_value_usd": entered_value,
                "quantity": rng.randint(100, 5000),
                "entry_type": "Consumption",
                "review_status": "Pending Review",
            })

            next_entry_id += 1

    # Chronological ordering supports a continuous five-year narrative.
    # IDs remain unique but need not be sequential by entry date.
    rows.sort(key=lambda row: (row["entry_date"], row["entry_id"]))

    return rows


def validate_transactions(rows):
    """Validate schema, identities, dates, values, and sourcing mix."""
    if len(rows) != TOTAL_TRANSACTIONS:
        raise ValueError("Incorrect total transaction count.")

    if any(list(row.keys()) != FIELDNAMES for row in rows):
        raise ValueError("Transaction schema mismatch.")

    ids = [row["entry_id"] for row in rows]

    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate entry IDs detected.")

    expected_ids = {
        f"ENT-{i:04d}"
        for i in range(1, TOTAL_TRANSACTIONS + 1)
    }

    if set(ids) != expected_ids:
        raise ValueError("Missing or unexpected entry IDs.")

    origin_lookup = dict(ORIGINS)
    year_counts = Counter()
    year_origin_counts = Counter()

    for row in rows:
        entry_date = date.fromisoformat(row["entry_date"])
        year = entry_date.year

        if not START_DATE <= entry_date <= CUTOFF_DATE:
            raise ValueError(
                f"Entry date outside permitted range: {entry_date}"
            )

        if row["importer_name"] != IMPORTER_NAME:
            raise ValueError("Unexpected importer name.")

        if origin_lookup.get(row["country_of_origin"]) != row["origin_code"]:
            raise ValueError("Country and origin code mismatch.")

        if row["entered_value_usd"] <= 0:
            raise ValueError("Entered value must be positive.")

        if row["quantity"] <= 0:
            raise ValueError("Quantity must be positive.")

        if row["entry_type"] != "Consumption":
            raise ValueError("Unexpected entry type.")

        if row["review_status"] != "Pending Review":
            raise ValueError("Unexpected review status.")

        if not row["hts_code"]:
            raise ValueError("Missing illustrative HTS code.")

        year_counts[year] += 1
        year_origin_counts[(year, row["origin_code"])] += 1

    for year, expected_count in ANNUAL_COUNTS.items():
        if year_counts[year] != expected_count:
            raise ValueError(
                f"{year}: expected {expected_count} transactions, "
                f"found {year_counts[year]}."
            )

        allocations = allocate_origin_counts(year)

        for (_, code), expected in zip(ORIGINS, allocations):
            actual = year_origin_counts[(year, code)]

            if actual != expected:
                raise ValueError(
                    f"{year} {code}: expected {expected}, "
                    f"found {actual}."
                )

    if rows != sorted(
        rows, key=lambda row: (row["entry_date"], row["entry_id"])
    ):
        raise ValueError("Transactions are not chronologically sorted.")


def write_csv(rows):
    """Write the validated dataset to the existing CSV filename."""
    with OUTPUT.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def print_summary(rows):
    """Display annual counts and entered values for verification."""
    annual_values = Counter()

    for row in rows:
        year = int(row["entry_date"][:4])
        annual_values[year] += row["entered_value_usd"]

    print("\nGAIANQI GLOBAL TRADING | SYNTHETIC IMPORT HISTORY")
    print("Period: 2022-01-01 through 2026-10-29")
    print("Data: Fictional transactions and growth assumptions\n")

    print(f"{'Year':<8}{'Entries':>10}{'Entered Value':>22}")
    print("-" * 40)

    for year in sorted(ANNUAL_COUNTS):
        print(
            f"{year:<8}"
            f"{ANNUAL_COUNTS[year]:>10,}"
            f"${annual_values[year]:>21,.2f}"
        )

    print("-" * 40)
    print(f"Total transactions: {len(rows):,}")
    print(f"Total entered value: ${sum(annual_values.values()):,.2f}")
    print(f"Saved to: {OUTPUT}")
    print("Validation: PASSED")
    print("\nHTS codes are illustrative; no tariff determinations made.")


def main():
    validate_configuration()
    rows = generate_transactions()
    validate_transactions(rows)
    write_csv(rows)
    print_summary(rows)


if __name__ == "__main__":
    main()
