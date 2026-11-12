
# Global Trade Data Analysis & Compliance Intelligence

### GaiAnQi Global Trading | Trade Intelligence Portfolio

**Python | SQL-Ready Data Modeling | Streamlit | Pandas | GitHub Actions | Trade Compliance**

An end-to-end trade analytics project demonstrating how connected procurement, logistics, customs, and compliance data can support business intelligence, operational oversight, and risk-based decision-making.

Built using **GaiAnQi Global Trading**, a fictional international importer, and reproducible synthetic transaction data.

### [🚀 Launch the Live Trade Intelligence Dashboard](https://global-trade-data-analysis-hzk4vwoxryasepp4c58s7h.streamlit.app)

Explore interactive analytics covering import operations, supplier exposure, customs valuation, and compliance review activity.

**Status:** V2 Live | **Data:** Synthetic | **Reporting Date:** November 10, 2026

---

## Executive Snapshot

| Key Metric | V2 Results |
|---|---:|
| Purchase Order Value | $498.18M |
| Customs Entered Value | $487.31M |
| Suppliers | 40 |
| Products | 60 |
| Purchase Orders | 2,000 |
| Shipments | 3,000 |
| Customs Entries | 2,940 |
| Compliance Review Flags | 7,039 |

*Compliance flags are synthetic review indicators, not confirmed violations.*

---

## Business Problem

International trade data is often fragmented across purchasing, transportation, customs brokerage, and compliance systems.

This project demonstrates how connecting those records can improve transaction traceability, financial reconciliation, operational reporting, and compliance exception management.

### Analytical Capabilities

- **Import Operations:** Shipment volumes, transportation modes, and transaction activity.
- **Supplier Intelligence:** Supplier exposure, shipment activity, and synthetic risk segmentation.
- **Customs Valuation:** Invoice values, illustrative adjustments, and entered value reconciliation.
- **Compliance Intelligence:** Rule-based exceptions categorized by risk severity, review status, and compliance topic.
- **Data Quality:** Unique identifiers, relationship validation, and financial consistency checks.

---

## Connected Data Architecture

V2 models the import lifecycle using linked synthetic records:

```text
Suppliers + Products
        |
        v
Purchase Orders (2,000)
        |
        v
Purchase Order Lines (5,000)
        |
        v
Shipments (3,000)
        |
        v
Shipment Lines (5,000)
        |
        v
Customs Entries (2,940)
        |
        v
Customs Entry Lines (4,894)
        |
        v
Compliance Review Flags (7,039)
```

Shared identifiers connect purchasing, shipment, customs, and compliance records to support transaction-level traceability.

---

## Technology & Automation

| Technology | Application |
|---|---|
| Python | Data generation, validation, and analytics |
| Pandas | Data transformation and dashboard preparation |
| Streamlit | Interactive business intelligence dashboard |
| GitHub Actions | Automated dataset generation and reporting |
| CSV | Structured synthetic transaction datasets |
| Git & GitHub | Version control and project documentation |

The pipeline uses deterministic synthetic data generation, referential integrity checks, duplicate detection, and financial reconciliation.

### Repository Structure

```text
Global-Trade-Data-Analysis/
|
|-- .github/workflows/       # Automated pipelines
|-- archive/v1/              # Preserved original project
|-- v2/
|   |-- data/                # Connected transaction datasets
|   |-- analytics/           # Generated KPI summaries
|   |-- generate_master_data.py
|   |-- generate_purchase_orders.py
|   |-- generate_shipments.py
|   |-- generate_customs_entries.py
|   |-- generate_compliance_exceptions.py
|   |-- analyze_trade_operations.py
|   |-- dashboard.py
|   `-- README.md
|
|-- CHANGELOG.md
|-- README.md
`-- requirements.txt
```

---

## Project Evolution

**V1 | Foundational Trade Analytics**

Analyzed 500 synthetic import transactions representing approximately $74.1M in entered value, with 327 transactions flagged for preliminary review.

**V2 | Connected Trade Intelligence**

Expanded into an automated, interconnected data environment with nearly 5,000 customs entry lines, financial reconciliation, compliance exception analytics, and a live Streamlit dashboard.

See the [Development Changelog](CHANGELOG.md) for project milestones and the [V1 Archive](archive/v1/) for historical work.

---

## Skills Demonstrated

**Trade Compliance:** Customs entry analytics, classification review, valuation controls, origin documentation, and exception management.

**Data Analytics:** Relational data modeling, KPI development, data validation, reconciliation, and business intelligence.

**Technical Execution:** Python automation, Streamlit dashboards, GitHub Actions, version control, and reproducible workflows.

---

## Disclaimer

GaiAnQi Global Trading is fictional, and all project data is synthetic. Tariff classifications, valuation scenarios, and compliance flags are illustrative. Results do not represent actual regulatory determinations or confirmed violations.

**[Explore the Live Dashboard](https://global-trade-data-analysis-hzk4vwoxryasepp4c58s7h.streamlit.app)**
