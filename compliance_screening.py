
import csv
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUTPUT = BASE / "outputs"
OUTPUT.mkdir(exist_ok=True)

def read_csv(filename):
    with (BASE / filename).open(
        "r", newline="", encoding="utf-8-sig"
    ) as file:
        return list(csv.DictReader(file, skipinitialspace=True))

entries = read_csv("import_entries.csv")
policy_map = read_csv("product_policy_map.csv")

if not entries or not policy_map:
    raise ValueError("Input files must contain data.")

required_entries = {
    "entry_id", "entry_date", "product_category",
    "origin_code", "entered_value_usd"
}
required_map = {
    "map_id", "product_category", "program",
    "origin_scope", "review_requirement"
}

if not required_entries.issubset(entries[0]):
    raise ValueError("Missing required import entry columns.")

if not required_map.issubset(policy_map[0]):
    raise ValueError("Missing required policy mapping columns.")

matches = []
annual = defaultdict(lambda: {
    "entry_ids": set(),
    "flagged_ids": set(),
    "total_value": 0.0,
    "flagged_value": 0.0,
    "review_matches": 0
})

for entry in entries:
    entry_id = entry["entry_id"]
    year = entry["entry_date"][:4]
    value = float(entry["entered_value_usd"])

    if value < 0:
        raise ValueError("Negative entered value: " + entry_id)

    annual[year]["entry_ids"].add(entry_id)
    annual[year]["total_value"] += value

    entry_matches = [
        rule for rule in policy_map
        if rule["product_category"] == entry["product_category"]
        and (
            rule["origin_scope"] == "ALL"
            or rule["origin_scope"] == entry["origin_code"]
        )
    ]

    if entry_matches:
        annual[year]["flagged_ids"].add(entry_id)
        annual[year]["flagged_value"] += value

    for rule in entry_matches:
        annual[year]["review_matches"] += 1
        matches.append({
            "entry_id": entry_id,
            "entry_date": entry["entry_date"],
            "year": year,
            "origin_code": entry["origin_code"],
            "product_category": entry["product_category"],
            "entered_value_usd": round(value, 2),
            "map_id": rule["map_id"],
            "program": rule["program"],
            "review_requirement": rule["review_requirement"],
            "screening_result": "Potential Review",
            "duty_determination": "Not Determined"
        })

match_columns = [
    "entry_id", "entry_date", "year", "origin_code",
    "product_category", "entered_value_usd", "map_id",
    "program", "review_requirement", "screening_result",
    "duty_determination"
]

with (OUTPUT / "compliance_screening_matches.csv").open(
    "w", newline="", encoding="utf-8"
) as file:
    writer = csv.DictWriter(file, fieldnames=match_columns)
    writer.writeheader()
    writer.writerows(matches)

summary_columns = [
    "year", "total_entries", "entries_flagged",
    "review_matches", "total_entered_value_usd",
    "flagged_entered_value_usd", "flagged_entry_pct"
]

summary_rows = []

for year, data in sorted(annual.items()):
    total_count = len(data["entry_ids"])
    flagged_count = len(data["flagged_ids"])

    summary_rows.append({
        "year": year,
        "total_entries": total_count,
        "entries_flagged": flagged_count,
        "review_matches": data["review_matches"],
        "total_entered_value_usd": round(
            data["total_value"], 2
        ),
        "flagged_entered_value_usd": round(
            data["flagged_value"], 2
        ),
        "flagged_entry_pct": round(
            flagged_count / total_count * 100, 1
        ) if total_count else 0
    })

with (OUTPUT / "annual_compliance_screening.csv").open(
    "w", newline="", encoding="utf-8"
) as file:
    writer = csv.DictWriter(file, fieldnames=summary_columns)
    writer.writeheader()
    writer.writerows(summary_rows)

print("Compliance screening complete!")
print("Transactions analyzed:", len(entries))
print("Potential policy matches:", len(matches))
print()
print("Year | Entries | Flagged | Review Matches")

for row in summary_rows:
    print(
        row["year"],
        "|", row["total_entries"],
        "|", row["entries_flagged"],
        "|", row["review_matches"]
    )

print()
print("Reports saved in outputs/")
print("NOTE: Screening only. No duties determined.")
