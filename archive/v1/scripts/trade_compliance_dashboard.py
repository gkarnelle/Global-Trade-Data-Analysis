
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

BASE = Path(__file__).resolve().parent
OUTPUT = BASE / "outputs"
OUTPUT.mkdir(exist_ok=True)


def read_csv(filename):
    with (BASE / filename).open(
        "r", newline="", encoding="utf-8-sig"
    ) as file:
        return list(csv.DictReader(file, skipinitialspace=True))


# Load synthetic transaction data and screening results.
entries = read_csv("import_entries.csv")
summary = read_csv("outputs/annual_compliance_screening.csv")

if not entries or not summary:
    raise ValueError("Missing transaction or screening data.")

years = [row["year"].strip() for row in summary]

total_entries = [
    int(row["total_entries"]) for row in summary
]
flagged_entries = [
    int(row["entries_flagged"]) for row in summary
]
flagged_pct = [
    float(row["flagged_entry_pct"]) for row in summary
]
total_value = [
    float(row["total_entered_value_usd"]) / 1_000_000
    for row in summary
]
flagged_value = [
    float(row["flagged_entered_value_usd"]) / 1_000_000
    for row in summary
]

if len(years) != 5 or years != [
    "2022", "2023", "2024", "2025", "2026"
]:
    raise ValueError("Expected annual data for 2022 through 2026.")

if sum(total_entries) != len(entries):
    raise ValueError("Annual counts do not match import entries.")

# Calculate sourcing shares by transaction count.
origin_counts = defaultdict(lambda: defaultdict(int))

for entry in entries:
    year = entry["entry_date"][:4]
    origin = entry["origin_code"].strip()
    origin_counts[year][origin] += 1

countries = ["CN", "MX", "CA", "DE", "VN", "KR"]
country_labels = {
    "CN": "China",
    "MX": "Mexico",
    "CA": "Canada",
    "DE": "Germany",
    "VN": "Vietnam",
    "KR": "South Korea"
}

country_colors = {
    "CN": "#345995",
    "MX": "#1D8A99",
    "CA": "#65B891",
    "DE": "#E6B566",
    "VN": "#D67B5C",
    "KR": "#8775A7"
}

# Dashboard styling.
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titleweight": "bold",
    "figure.facecolor": "#F7F9FC",
    "axes.facecolor": "#FFFFFF",
    "savefig.facecolor": "#F7F9FC"
})

fig, axes = plt.subplots(2, 2, figsize=(16, 11))
fig.subplots_adjust(
    top=0.83,
    bottom=0.13,
    left=0.08,
    right=0.96,
    hspace=0.43,
    wspace=0.26
)

fig.suptitle(
    "GAIANQI GLOBAL TRADING",
    fontsize=24,
    fontweight="bold",
    x=0.08,
    y=0.97,
    ha="left",
    color="#19334D"
)

fig.text(
    0.08, 0.925,
    "2022–2026 | Trade Compliance Intelligence Dashboard",
    fontsize=15,
    color="#52667B"
)

fig.text(
    0.08, 0.885,
    "Synthetic importer transactions | Potential policy screening only",
    fontsize=10,
    color="#66788A"
)

# 1. Annual import activity.
ax = axes[0, 0]
bars = ax.bar(
    years, total_entries,
    color="#345995", width=0.6
)
ax.set_title("Annual Import Activity", loc="left", pad=15)
ax.set_ylabel("Number of transactions")
ax.set_ylim(0, max(total_entries) * 1.22)
ax.grid(axis="y", alpha=0.15)
ax.set_axisbelow(True)

for bar in bars:
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 2,
        str(int(bar.get_height())),
        ha="center", fontsize=9
    )

# 2. Percentage flagged for compliance review.
ax = axes[0, 1]
ax.plot(
    years, flagged_pct,
    marker="o", linewidth=2.8,
    markersize=8, color="#D67B5C"
)
ax.set_title(
    "Transactions Flagged for Potential Review",
    loc="left", pad=15
)
ax.set_ylabel("Percentage of transactions")
ax.set_ylim(0, 100)
ax.grid(axis="y", alpha=0.15)
ax.set_axisbelow(True)

for year, pct in zip(years, flagged_pct):
    ax.annotate(
        "{:.1f}%".format(pct),
        (year, pct),
        textcoords="offset points",
        xytext=(0, 11),
        ha="center", fontsize=9
    )

# 3. Total versus flagged entered value.
ax = axes[1, 0]
positions = list(range(len(years)))
width = 0.36

ax.bar(
    [p - width / 2 for p in positions],
    total_value, width,
    label="Total entered value",
    color="#345995"
)
ax.bar(
    [p + width / 2 for p in positions],
    flagged_value, width,
    label="Flagged entered value",
    color="#E6B566"
)

ax.set_xticks(positions)
ax.set_xticklabels(years)
ax.set_title(
    "Entered Value Requiring Potential Review",
    loc="left", pad=15
)
ax.set_ylabel("USD millions")
ax.yaxis.set_major_formatter(
    FuncFormatter(lambda value, pos: "${:.0f}M".format(value))
)
ax.legend(frameon=False, fontsize=9)
ax.grid(axis="y", alpha=0.15)
ax.set_axisbelow(True)

# 4. Country-of-origin sourcing mix.
ax = axes[1, 1]
bottom = [0.0] * len(years)

for country in countries:
    shares = [
        100 * origin_counts[year][country] /
        total_entries[i]
        for i, year in enumerate(years)
    ]

    ax.bar(
        years, shares, bottom=bottom,
        label=country_labels[country],
        color=country_colors[country],
        width=0.65
    )

    bottom = [
        bottom[i] + shares[i]
        for i in range(len(years))
    ]

ax.set_title(
    "Country-of-Origin Mix",
    loc="left", pad=15
)
ax.set_ylabel("Share of transaction count")
ax.set_ylim(0, 100)
ax.legend(
    ncol=3, fontsize=8,
    frameon=False,
    loc="upper center",
    bbox_to_anchor=(0.5, -0.12)
)

# Dashboard methodology and limitations.
fig.text(
    0.08, 0.065,
    "METHOD: Screening by product category and origin; "
    "no effective-date or HTS-level determination.",
    fontsize=9,
    color="#52667B"
)

fig.text(
    0.08, 0.040,
    "All GaiAnQi transactions are fictional. "
    "Flagged value is not assessed duties, "
    "confirmed liability, or a compliance violation.",
    fontsize=9,
    color="#52667B"
)

dashboard_path = (
    OUTPUT / "trade_compliance_intelligence_dashboard.png"
)

fig.savefig(
    dashboard_path,
    dpi=180,
    bbox_inches="tight"
)
plt.close(fig)

print("Dashboard created successfully!")
print("Transactions analyzed:", len(entries))
print("Years:", ", ".join(years))
print("Saved to:", dashboard_path)
