import csv
from collections import defaultdict
from pathlib import Path

DATA_FILE = Path(__file__).with_name("trade_data.csv")

totals = defaultdict(lambda: {"exports": 0.0, "imports": 0.0})
yearly = defaultdict(lambda: {"exports": 0.0, "imports": 0.0})

with DATA_FILE.open(newline="", encoding="utf-8") as file:
    for row in csv.DictReader(file):
        country = row["country"]
        year = int(row["year"])
        exports = float(row["exports_usd_millions"])
        imports = float(row["imports_usd_millions"])
        totals[country]["exports"] += exports
        totals[country]["imports"] += imports
        yearly[year]["exports"] += exports
        yearly[year]["imports"] += imports

print("GLOBAL TRADE ANALYSIS")
print("Synthetic sample data | USD millions")

for country, values in sorted(totals.items()):
    balance = values["exports"] - values["imports"]
    status = "Surplus" if balance >= 0 else "Deficit"
    print(f"{country}: Exports ${values['exports']:,.0f}M | "
          f"Imports ${values['imports']:,.0f}M | "
          f"{status} ${abs(balance):,.0f}M")

print("\nYEARLY TRADE TRENDS")
previous_exports = None

for year, values in sorted(yearly.items()):
    balance = values["exports"] - values["imports"]
    print(f"{year}: Exports ${values['exports']:,.0f}M | "
          f"Imports ${values['imports']:,.0f}M | "
          f"Balance ${balance:,.0f}M")
    if previous_exports is not None:
        growth = (values["exports"] / previous_exports - 1) * 100
        print(f"  Export growth: {growth:.1f}%")
    previous_exports = values["exports"]
