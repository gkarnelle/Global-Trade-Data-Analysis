
"""Analyze synthetic import transactions using illustrative tariff scenarios."""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

# Load synthetic import transactions and scenario rules.
entries = pd.read_csv(
    ROOT / "import_entries.csv",
    parse_dates=["entry_date"],
    dtype={"hts_code": str, "origin_code": str}
)

rules = pd.read_csv(
    ROOT / "tariff_rules.csv",
    parse_dates=["effective_start", "effective_end"]
)

# Validate essential fields.
required = {
    "entry_id", "entry_date", "origin_code",
    "product_category", "entered_value_usd"
}

missing = required - set(entries.columns)
if missing:
    raise ValueError(f"Missing import columns: {missing}")

if entries["entry_id"].duplicated().any():
    raise ValueError("Duplicate import entry IDs detected")

if (
    entries["entered_value_usd"].isna().any()
    or (entries["entered_value_usd"] <= 0).any()
):
    raise ValueError("Invalid entered values detected")


# Match import entries against illustrative tariff rules.
matches = entries.merge(
    rules,
    on="product_category",
    how="left",
    suffixes=("_entry", "_rule")
)

# Filter by country of origin and effective dates.
applicable = matches[
    (
        (matches["origin_code_rule"] == "ALL")
        | (
            matches["origin_code_entry"]
            == matches["origin_code_rule"]
        )
    )
    & (matches["entry_date"] >= matches["effective_start"])
    & (matches["entry_date"] <= matches["effective_end"])
].copy()


applicable["modeled_additional_duty_usd"] = (
    applicable["entered_value_usd"]
    * applicable["illustrative_additional_rate"]
)

# --------------------------------------------------
# COMPLIANCE RISK SCREENING
# Illustrative review priorities, not legal findings
# --------------------------------------------------

def assign_risk_priority(modeled_duty):
    """Prioritize matched entries by modeled duty exposure."""
    if modeled_duty >= 25000:
        return "High"
    elif modeled_duty >= 10000:
        return "Medium"
    else:
        return "Low"


applicable["risk_priority"] = applicable[
    "modeled_additional_duty_usd"
].apply(assign_risk_priority)

applicable["hts_review_flag"] = "Review HTS and Chapter 99 applicability"

applicable["trade_remedy_review_flag"] = (
    "Verify program scope, rates, dates, and exclusions"
)

applicable["origin_review_flag"] = (
    "Verify documented country of origin"
)


# Build a complete screening report covering every import entry.
# Keep only the entry-level columns needed from matched scenarios.
matched = applicable[
    [
        "entry_id",
        "program",
        "modeled_additional_duty_usd",
        "risk_priority",
        "hts_review_flag",
        "trade_remedy_review_flag",
        "origin_review_flag",
    ]
].copy()

# Aggregate matches to one row per entry, allowing for
# multiple hypothetical tariff rules to match an entry.
matched_summary = matched.groupby("entry_id", as_index=False).agg(
    matched_programs=("program", lambda x: ", ".join(sorted(set(x)))),
    modeled_additional_duty_usd=("modeled_additional_duty_usd", "sum"),
    matched_rule_count=("program", "size"),
)

# Join screening results back to all original transactions.
compliance_report = entries.merge(
    matched_summary,
    on="entry_id",
    how="left",
    validate="one_to_one",
)

compliance_report["screening_status"] = (
    compliance_report["matched_rule_count"]
    .notna()
    .map({True: "Scenario Match", False: "No Scenario Match"})
)

compliance_report["modeled_additional_duty_usd"] = (
    compliance_report["modeled_additional_duty_usd"].fillna(0)
)

compliance_report["matched_rule_count"] = (
    compliance_report["matched_rule_count"].fillna(0).astype(int)
)

compliance_report["risk_priority"] = (
    compliance_report["modeled_additional_duty_usd"]
    .apply(assign_risk_priority)
)

compliance_report.loc[
    compliance_report["screening_status"] == "No Scenario Match",
    "risk_priority",
] = "Not Assessed"

compliance_report["hts_review_flag"] = (
    "Verify HTS classification and Chapter 99 applicability"
)
compliance_report["origin_review_flag"] = (
    "Verify documented country of origin"
)
compliance_report["trade_remedy_review_flag"] = (
    "Verify applicable remedies, scope, dates, and exclusions"
)

compliance_report.to_csv(
    OUT / "compliance_risk_report.csv",
    index=False,
)

print("\nComplete Compliance Screening Summary")
print(compliance_report["screening_status"].value_counts())
print("\nReview Priority Summary")
print(compliance_report["risk_priority"].value_counts())


print("\nCompliance Risk Screening Summary")
print(applicable["risk_priority"].value_counts())

# Save entry-level tariff scenario matches.
applicable.to_csv(
    OUT / "tariff_scenario_matches.csv",
    index=False
)

# Summarize modeled exposure by trade remedy program.
program_summary = (
    applicable.groupby("program", as_index=False)
    .agg(
        matched_entries=("entry_id", "nunique"),
        entered_value_usd=("entered_value_usd", "sum"),
        modeled_additional_duty_usd=(
            "modeled_additional_duty_usd", "sum"
        )
    )
    .sort_values(
        "modeled_additional_duty_usd",
        ascending=False
    )
)

program_summary.to_csv(
    OUT / "tariff_program_summary.csv",
    index=False
)

total_import_value = entries["entered_value_usd"].sum()
total_modeled_duties = applicable[
    "modeled_additional_duty_usd"
].sum()

print("\nGLOBAL TRADE | TARIFF SCENARIO INTELLIGENCE")
print("Synthetic data and illustrative tariff assumptions")
print(f"\nImport transactions: {len(entries)}")
print(f"Total entered value: ${total_import_value:,.2f}")
print(f"Scenario-matched entries: {applicable['entry_id'].nunique()}")
print(f"Modeled additional duties: ${total_modeled_duties:,.2f}")

print("\nMODELED EXPOSURE BY PROGRAM")
print(program_summary.to_string(index=False))

print("\nReports saved in outputs/")

# ==========================================================
# EXECUTIVE TARIFF INTELLIGENCE DASHBOARD
# Synthetic data and illustrative tariff assumptions only.
# ==========================================================

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

NAVY = "#17324D"
TEAL = "#197F8C"
GOLD = "#D99A36"
GRAY = "#66788A"
BG = "#F5F7FA"

# Calculate dashboard KPIs.
matched_entries = applicable["entry_id"].nunique()
match_rate = matched_entries / len(entries) * 100

# Summarize modeled duties by country of origin.
country_exposure = (
    applicable.groupby("country_of_origin", as_index=False)
    ["modeled_additional_duty_usd"]
    .sum()
    .sort_values("modeled_additional_duty_usd", ascending=False)
)

country_exposure.to_csv(
    OUT / "tariff_country_exposure.csv",
    index=False
)

# Summarize modeled duties by product category.
category_exposure = (
    applicable.groupby("product_category", as_index=False)
    ["modeled_additional_duty_usd"]
    .sum()
    .sort_values("modeled_additional_duty_usd", ascending=False)
)

category_exposure.to_csv(
    OUT / "tariff_category_exposure.csv",
    index=False
)

fig = plt.figure(figsize=(16, 11), facecolor=BG)

# Dashboard title and prominent disclosure.
fig.text(
    .06, .955,
    "GLOBAL TRADE | TARIFF & COMPLIANCE INTELLIGENCE",
    fontsize=19, fontweight="bold", color=NAVY
)
fig.text(
    .06, .924,
    "2025–2026 U.S. Import Exposure | Scenario Analysis",
    fontsize=11, color=GRAY
)
fig.text(
    .06, .895,
    "SYNTHETIC DATA  |  ILLUSTRATIVE TARIFF SCENARIOS",
    fontsize=11, color=TEAL, fontweight="bold"
)

# Executive KPI cards.
kpis = [
    ("TOTAL ENTERED VALUE", total_import_value, "money"),
    ("MODELED ADDITIONAL DUTIES", total_modeled_duties, "money"),
    ("IMPORT TRANSACTIONS", len(entries), "count"),
    ("SCENARIO MATCH RATE", match_rate, "percent"),
]

for i, (label, value, kind) in enumerate(kpis):
    x = .06 + i * .235
    ax = fig.add_axes([x, .76, .215, .105])
    ax.set_facecolor("white")
    ax.set_xticks([])
    ax.set_yticks([])

    for spine in ax.spines.values():
        spine.set_visible(False)

    if kind == "money":
        display = f"${value / 1e6:,.2f}M"
    elif kind == "percent":
        display = f"{value:.1f}%"
    else:
        display = f"{value:,}"

    ax.text(
        .05, .70, label, transform=ax.transAxes,
        fontsize=9, color=GRAY, fontweight="bold"
    )
    ax.text(
        .05, .18, display, transform=ax.transAxes,
        fontsize=23, color=TEAL, fontweight="bold"
    )

# Chart 1: Trade remedy program exposure.
ax1 = fig.add_axes([.08, .39, .39, .29])
ax1.set_facecolor("white")

bars = ax1.bar(
    program_summary["program"],
    program_summary["modeled_additional_duty_usd"],
    color=[TEAL, GOLD, "#7B8FA3"]
)

ax1.set_title(
    "01 | Modeled Exposure by Trade Remedy",
    loc="left", fontweight="bold", color=NAVY, pad=15
)
ax1.yaxis.set_major_formatter(
    FuncFormatter(lambda x, pos: f"${x / 1e6:.1f}M")
)
ax1.spines[["top", "right"]].set_visible(False)

for bar in bars:
    height = bar.get_height()
    ax1.text(
        bar.get_x() + bar.get_width() / 2,
        height + 25000,
        f"${height / 1e6:.2f}M",
        ha="center", fontsize=10, fontweight="bold"
    )

ax1.set_ylim(
    0,
    program_summary["modeled_additional_duty_usd"].max() * 1.22
)

# Chart 2: Country exposure.
ax2 = fig.add_axes([.57, .39, .37, .29])
ax2.set_facecolor("white")

top_countries = country_exposure.head(6).iloc[::-1]

ax2.barh(
    top_countries["country_of_origin"],
    top_countries["modeled_additional_duty_usd"],
    color=TEAL
)

ax2.set_title(
    "02 | Modeled Duties by Country of Origin",
    loc="left", fontweight="bold", color=NAVY, pad=15
)
ax2.xaxis.set_major_formatter(
    FuncFormatter(lambda x, pos: f"${x / 1e6:.1f}M")
)
ax2.spines[["top", "right"]].set_visible(False)

for i, value in enumerate(
    top_countries["modeled_additional_duty_usd"]
):
    ax2.text(
        value + 10000, i,
        f"${value / 1000:,.0f}K",
        va="center", fontsize=9
    )

ax2.set_xlim(
    0,
    top_countries["modeled_additional_duty_usd"].max() * 1.30
)

# Executive compliance priorities.
ax3 = fig.add_axes([.06, .105, .88, .20])
ax3.set_facecolor("white")
ax3.set_xticks([])
ax3.set_yticks([])

for spine in ax3.spines.values():
    spine.set_visible(False)

ax3.text(
    .025, .80,
    "03 | EXECUTIVE COMPLIANCE PRIORITIES",
    fontsize=13, fontweight="bold", color=NAVY,
    transform=ax3.transAxes
)

priorities = [
    "PRIORITY 1  |  Validate HTS classifications and Chapter 99 applicability.",
    "PRIORITY 2  |  Review origin-specific trade remedies and exclusions.",
    "PRIORITY 3  |  Evaluate lawful mitigation and sourcing alternatives."
]

for i, priority in enumerate(priorities):
    ax3.text(
        .035, .55 - i * .22,
        priority, fontsize=11, color=NAVY,
        transform=ax3.transAxes
    )

# Explicit methodological disclaimer.
fig.text(
    .06, .062,
    "Portfolio demonstration using fictional import transactions and "
    "simplified trade remedy assumptions.",
    fontsize=9, color=GRAY
)
fig.text(
    .06, .041,
    "Not actual tariff determinations, current duty rates, "
    "or verified savings opportunities.",
    fontsize=9, color=GRAY
)

fig.savefig(
    OUT / "tariff_intelligence_dashboard.png",
    dpi=180,
    bbox_inches="tight",
    facecolor=fig.get_facecolor()
)

plt.close(fig)

print("\nExecutive tariff dashboard generated successfully.")
print("Saved to outputs/tariff_intelligence_dashboard.png")

# --------------------------------------------------
# TARIFF MITIGATION | LANDED COST SCENARIO MODEL
# Hypothetical assumptions, not verified duty savings
# --------------------------------------------------

def calculate_landed_cost(
    product_value,
    additional_duty_rate,
    freight_cost
):
    """Calculate simplified modeled landed cost."""
    additional_duty = product_value * additional_duty_rate

    landed_cost = (
        product_value
        + additional_duty
        + freight_cost
    )

    return landed_cost


# Illustrative sourcing comparison
current_cost = calculate_landed_cost(
    product_value=100000,
    additional_duty_rate=0.25,
    freight_cost=5000
)

alternative_cost = calculate_landed_cost(
    product_value=108000,
    additional_duty_rate=0.00,
    freight_cost=6000
)

potential_difference = current_cost - alternative_cost

print("\nTARIFF MITIGATION | ILLUSTRATIVE SOURCING SCENARIO")
print(f"Current modeled landed cost: ${current_cost:,.2f}")
print(f"Alternative modeled landed cost: ${alternative_cost:,.2f}")
print(f"Potential cost difference: ${potential_difference:,.2f}")
print("Scenario only; actual tariff treatment and sourcing feasibility require verification.")
