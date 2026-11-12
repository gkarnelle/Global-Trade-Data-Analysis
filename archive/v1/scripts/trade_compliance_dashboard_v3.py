
import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import FuncFormatter

BASE = Path(__file__).resolve().parent
OUTPUT = BASE / "outputs"
OUTPUT.mkdir(exist_ok=True)


def read_csv(filename):
    with (BASE / filename).open(
        "r", newline="", encoding="utf-8-sig"
    ) as file:
        return list(csv.DictReader(
            (line for line in file if line.strip()),
            skipinitialspace=True
        ))


entries = read_csv("import_entries.csv")
summary = read_csv("outputs/annual_compliance_screening.csv")
policies = read_csv("tariff_policy_history.csv")

if not entries or not summary or not policies:
    raise ValueError("One or more input files are empty.")

required_policy_columns = {
    "policy_id", "program", "event_date",
    "effective_date", "event_type", "policy_summary",
    "source_agency", "source_url", "verification_status"
}

if not required_policy_columns.issubset(policies[0]):
    raise ValueError(
        "Policy CSV is missing required columns."
    )

years = [r["year"].strip() for r in summary]
counts = [int(r["total_entries"]) for r in summary]
flagged = [int(r["entries_flagged"]) for r in summary]
percentages = [
    float(r["flagged_entry_pct"]) for r in summary
]
values = [
    float(r["total_entered_value_usd"]) / 1e6
    for r in summary
]
flagged_values = [
    float(r["flagged_entered_value_usd"]) / 1e6
    for r in summary
]

if years != ["2022", "2023", "2024", "2025", "2026"]:
    raise ValueError("Expected 2022-2026 summary data.")

if sum(counts) != len(entries):
    raise ValueError("Transaction totals do not match.")

total_transactions = sum(counts)
total_value = sum(values)
total_flagged = sum(flagged)
total_flagged_value = sum(flagged_values)

origins = defaultdict(lambda: defaultdict(int))

for entry in entries:
    year = entry["entry_date"][:4]
    origin = entry["origin_code"].strip()
    origins[year][origin] += 1

countries = [
    ("CN", "China", "#345995"),
    ("MX", "Mexico", "#1D8A99"),
    ("CA", "Canada", "#65B891"),
    ("DE", "Germany", "#E6B566"),
    ("VN", "Vietnam", "#D67B5C"),
    ("KR", "South Korea", "#8775A7")
]

# Read timeline events from the policy reference CSV.
events = []

for policy in policies:
    event_date = datetime.strptime(
        policy["event_date"].strip(), "%Y-%m-%d"
    )

    effective_text = policy["effective_date"].strip()
    effective_date = (
        datetime.strptime(effective_text, "%Y-%m-%d")
        if effective_text else None
    )

    events.append({
        "id": policy["policy_id"].strip(),
        "program": policy["program"].strip(),
        "event_date": event_date,
        "effective_date": effective_date,
        "event_type": policy["event_type"].strip(),
        "summary": policy["policy_summary"].strip(),
        "agency": policy["source_agency"].strip(),
        "source": policy["source_url"].strip(),
        "status": policy["verification_status"].strip()
    })

events.sort(key=lambda item: item["event_date"])

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titleweight": "bold",
    "figure.facecolor": "#F7F9FC",
    "axes.facecolor": "white"
})

fig = plt.figure(figsize=(16, 17))
fig.patch.set_facecolor("#F7F9FC")

fig.text(
    0.07, 0.967, "GAIANQI GLOBAL TRADING",
    fontsize=25, weight="bold", color="#19334D"
)
fig.text(
    0.07, 0.94,
    "2022-2026 | Executive Trade Compliance Intelligence",
    fontsize=15, color="#52667B"
)
fig.text(
    0.07, 0.917,
    "Fictional importer | Synthetic data | "
    "Preliminary compliance screening",
    fontsize=10, color="#66788A"
)

# Executive KPI cards.
kpis = [
    ("TOTAL TRANSACTIONS",
     "{:,}".format(total_transactions)),
    ("TOTAL ENTERED VALUE",
     "${:.1f}M".format(total_value)),
    ("TRANSACTIONS FLAGGED",
     "{:,} ({:.1f}%)".format(
         total_flagged,
         100 * total_flagged / total_transactions
     )),
    ("FLAGGED ENTERED VALUE",
     "${:.1f}M".format(total_flagged_value))
]

for i, (label, value) in enumerate(kpis):
    x = 0.07 + i * 0.225
    y = 0.839

    card = FancyBboxPatch(
        (x, y), 0.205, 0.060,
        transform=fig.transFigure,
        boxstyle="round,pad=0.008",
        facecolor="white",
        edgecolor="#DFE7EF",
        linewidth=1
    )
    fig.add_artist(card)

    fig.text(
        x + 0.012, y + 0.039, label,
        fontsize=9, color="#65788B",
        weight="bold"
    )
    fig.text(
        x + 0.012, y + 0.012, value,
        fontsize=19, color="#19334D",
        weight="bold"
    )

# Four analytical charts.
grid = fig.add_gridspec(
    2, 2,
    left=0.07, right=0.96,
    top=0.806, bottom=0.39,
    hspace=0.43, wspace=0.25
)

ax1 = fig.add_subplot(grid[0, 0])
bars = ax1.bar(years, counts, color="#345995")
ax1.set_title("Annual Import Activity", loc="left", pad=14)
ax1.set_ylabel("Transactions")
ax1.set_ylim(0, max(counts) * 1.23)
ax1.grid(axis="y", alpha=0.15)
ax1.set_axisbelow(True)

for bar in bars:
    ax1.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 2,
        str(int(bar.get_height())),
        ha="center"
    )

ax2 = fig.add_subplot(grid[0, 1])
ax2.plot(
    years, percentages,
    marker="o", linewidth=2.7,
    markersize=8, color="#D67B5C"
)
ax2.set_title(
    "Transactions Flagged for Potential Review",
    loc="left", pad=14
)
ax2.set_ylabel("Share of transactions (%)")
ax2.set_ylim(0, 100)
ax2.grid(axis="y", alpha=0.15)

for year, pct in zip(years, percentages):
    ax2.annotate(
        "{:.1f}%".format(pct),
        (year, pct),
        xytext=(0, 11),
        textcoords="offset points",
        ha="center"
    )

ax3 = fig.add_subplot(grid[1, 0])
positions = list(range(len(years)))
width = 0.36

ax3.bar(
    [p - width / 2 for p in positions],
    values, width,
    color="#345995",
    label="Total entered value"
)
ax3.bar(
    [p + width / 2 for p in positions],
    flagged_values, width,
    color="#E6B566",
    label="Flagged entered value"
)
ax3.set_xticks(positions)
ax3.set_xticklabels(years)
ax3.set_title("Entered Value Screening", loc="left", pad=14)
ax3.set_ylabel("USD millions")
ax3.yaxis.set_major_formatter(
    FuncFormatter(
        lambda value, pos: "${:.0f}M".format(value)
    )
)
ax3.legend(frameon=False, fontsize=9)
ax3.grid(axis="y", alpha=0.15)
ax3.set_axisbelow(True)

ax4 = fig.add_subplot(grid[1, 1])
bottom = [0.0] * len(years)

for code, label, color in countries:
    shares = [
        100 * origins[year][code] / counts[i]
        for i, year in enumerate(years)
    ]
    ax4.bar(
        years, shares, bottom=bottom,
        color=color, label=label
    )
    bottom = [
        bottom[i] + shares[i]
        for i in range(len(years))
    ]

ax4.set_title(
    "Country-of-Origin Sourcing Mix",
    loc="left", pad=14
)
ax4.set_ylabel("Share of transaction count (%)")
ax4.set_ylim(0, 100)
ax4.legend(
    ncol=3, fontsize=8, frameon=False,
    loc="upper center",
    bbox_to_anchor=(0.5, -0.12)
)

# Data-driven policy timeline.
fig.text(
    0.07, 0.346,
    "U.S. TRADE POLICY | SELECTED HISTORICAL MILESTONES",
    fontsize=14, weight="bold", color="#19334D"
)

timeline = fig.add_axes([0.09, 0.275, 0.85, 0.055])
timeline.set_xlim(
    datetime(2022, 1, 1),
    datetime(2026, 12, 31)
)
timeline.set_ylim(-0.5, 0.5)
timeline.axhline(0, color="#9EB0C2", linewidth=2)

timeline.xaxis.set_major_locator(
    mdates.YearLocator()
)
timeline.xaxis.set_major_formatter(
    mdates.DateFormatter("%Y")
)

for spine in timeline.spines.values():
    spine.set_visible(False)

timeline.set_yticks([])
timeline.tick_params(axis="x", length=0, pad=8)

program_colors = {
    "Section 301": "#345995",
    "Section 232": "#D67B5C",
    "Section 201": "#65B891"
}

for event in events:
    color = program_colors.get(
        event["program"], "#8775A7"
    )

    timeline.scatter(
        event["event_date"], 0,
        s=115, color=color,
        edgecolor="white",
        linewidth=1.5,
        zorder=5
    )

# Event details: one record per row, avoiding overlaps.
fig.text(
    0.07, 0.247,
    "POLICY EVENT REGISTER",
    fontsize=10, weight="bold", color="#52667B"
)

row_y = 0.226
row_step = 0.026

for i, event in enumerate(events):
    date_label = event["event_date"].strftime("%b %d, %Y")
    effective_label = (
        event["effective_date"].strftime("%b %d, %Y")
        if event["effective_date"] else "Not a new effective date"
    )

    line = (
        event["id"] + " | " +
        date_label + " | " +
        event["program"] + " | " +
        event["event_type"] +
        " | Effective: " + effective_label
    )

    fig.text(
        0.08, row_y - i * row_step,
        line, fontsize=9, color="#344C63"
    )

fig.text(
    0.07, 0.075,
    "SOURCE REGISTER: Event IDs and official URLs are "
    "maintained in tariff_policy_history.csv.",
    fontsize=9, color="#52667B"
)
fig.text(
    0.07, 0.056,
    "METHOD: Screening by product category and origin. "
    "Effective-date, HTS, Chapter 99 and exclusion tests "
    "are not applied.",
    fontsize=9, color="#52667B"
)
fig.text(
    0.07, 0.037,
    "Synthetic data. Flagged entered value is not "
    "assessed duties, confirmed liability, or a "
    "compliance violation.",
    fontsize=9, color="#52667B"
)

path = OUTPUT / "trade_compliance_dashboard_v3.png"

fig.savefig(
    path, dpi=180,
    bbox_inches="tight",
    facecolor=fig.get_facecolor()
)
plt.close(fig)

print("Version 3 dashboard created successfully!")
print("Transactions:", total_transactions)
print("Flagged transactions:", total_flagged)
print("Policy milestones loaded:", len(events))
print("Saved to:", path)
