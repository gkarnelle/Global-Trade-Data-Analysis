# Global Trade Data Analysis & Compliance Intelligence

### GaiAnQi Global Trading | Synthetic Import Operations Analytics

A portfolio project demonstrating how connected import transaction data can support operational visibility, compliance risk identification, customs valuation review, and data-driven decision-making.

Built around **GaiAnQi Global Trading**, a fictional international importing company, this project simulates an end-to-end import data environment spanning procurement, logistics, customs entry records, and compliance exception management.

> **Project Status:** Version 2.0 under active development. The connected data generation pipeline and initial compliance exception engine are implemented. Advanced analytics and interactive dashboards are planned enhancements.

---

## Executive Overview

International trade operations generate data across multiple business functions, including sourcing, purchasing, transportation, customs brokerage, and compliance.

When these records are disconnected, organizations may struggle to reconcile transactions, identify discrepancies, prioritize compliance reviews, and understand their import exposure.

This project explores how a connected data architecture and reproducible Python workflows can help address those challenges.

### Project Objectives

- Connect supplier, product, purchase order, shipment, and customs entry records.
- Demonstrate transactional traceability across the import lifecycle.
- Generate realistic, reproducible synthetic trade datasets.
- Identify potential compliance review exceptions using documented screening rules.
- Validate financial calculations and record relationships.
- Develop a foundation for operational and compliance analytics.

---

## Version 2.0: Connected Trade Data Architecture

The V2 model introduces interconnected datasets representing major stages of the import process.

| Data Domain | Records | Purpose |
|---|---:|---|
| Suppliers | 40 | Supplier profiles and operational risk attributes |
| Products | 60 | Product master data and illustrative tariff classifications |
| Purchase Orders | 2,000 | Procurement transaction headers |
| Purchase Order Lines | 5,000 | Product-level purchasing details |
| Shipments | 3,000 | Transportation and delivery records |
| Shipment Lines | 5,000 | Product-level shipment traceability |
| Customs Entries | Variable | Synthetic entries associated with delivered shipments |
| Customs Entry Lines | Variable | Entry-level product, quantity, origin, and valuation details |
| Compliance Exceptions | Variable | Rule-based compliance review indicators |

Customs entry and exception record counts depend on the generated source data and applicable screening rules.

### Data Relationships

```text
SUPPLIERS ────────────────┐
                         │
PRODUCTS ────────────────┤
                         ▼
                  PURCHASE ORDERS
                         │
                         ▼
                 PURCHASE ORDER LINES
                         │
                         ▼
                      SHIPMENTS
                         │
                         ▼
                   SHIPMENT LINES
                         │
                         ▼
                   CUSTOMS ENTRIES
                         │
                         ▼
                 CUSTOMS ENTRY LINES
                         │
                         ▼
                COMPLIANCE EXCEPTIONS
```

Shared synthetic identifiers support traceability between purchasing, transportation, customs, and compliance records.

---

## Compliance Exception Intelligence

The V2 compliance exception engine applies documented rules to synthetic customs entry records.

### Review Categories

| Category | Analytical Focus |
|---|---|
| HTS Classification | Classification verification and supporting rationale |
| Customs Valuation | Review of illustrative valuation adjustments |
| Country of Origin | Supporting documentation and origin review scenarios |
| Documentation | Simulated missing-document scenarios |
| Data Integrity | Invalid values and inconsistent transaction references |

Each generated exception includes identifiers connecting it to the relevant customs transaction, an exception category, severity, reason, recommended action, and review status.

**Important:** Exceptions represent preliminary review indicators, not confirmed violations. Some scenarios are deliberately simulated to demonstrate analytical controls and human-review workflows.

The current engine provides a starting point for exception management rather than a production-ready compliance screening solution.

---

## Automation and Data Quality

The project uses Python scripts and GitHub Actions to generate and validate synthetic datasets.

Implemented controls include:

- Deterministic synthetic data generation.
- Unique transaction identifier checks.
- Purchase order and shipment relationship validation.
- Customs entry value reconciliation.
- Entry-to-shipment referential integrity checks.
- Duplicate compliance exception checks.
- Automated CSV generation and version-controlled outputs.

These controls help demonstrate reproducibility, traceability, and basic data governance principles.

---

## Technology Stack

| Technology | Application |
|---|---|
| Python | Synthetic data generation and rule-based analysis |
| CSV | Structured transaction datasets |
| GitHub Actions | Workflow execution and automation |
| Git / GitHub | Version control and project documentation |
| Decimal arithmetic | Financial value reconciliation |
| SHA-256 hashing | Deterministic exception sampling and archive verification |

---

## Repository Structure

```text
Global-Trade-Data-Analysis/
│
├── .github/
│   └── workflows/
│       └── Automated generation and validation
│
├── archive/
│   └── v1/
│       ├── scripts/
│       ├── data/
│       ├── dashboards/
│       ├── outputs/
│       └── README.md
│
├── v2/
│   ├── data/
│   ├── generate_master_data.py
│   ├── generate_purchase_orders.py
│   ├── generate_shipments.py
│   ├── generate_customs_entries.py
│   ├── generate_compliance_exceptions.py
│   └── README.md
│
├── CHANGELOG.md
├── README.md
└── requirements.txt
```

The original project has been preserved under `archive/v1/` for historical reference.

---

## Project Evolution

### Version 1.0: Initial Trade Analytics

The original project analyzed 500 synthetic import transactions representing approximately $74.1 million in entered value.

Its preliminary screening logic identified 327 transactions for further review.

V1 established the foundation for tariff exposure analysis, compliance screening, and trade dashboard development.

### Version 2.0: Connected Import Intelligence

V2 expands the project into a connected synthetic import operations environment, with procurement, logistics, customs, and compliance exception datasets.

The emphasis shifts from analyzing individual transaction files to understanding relationships across the import lifecycle.

For the development history, see [CHANGELOG.md](CHANGELOG.md).

For historical scripts, datasets, and dashboards, see [Version 1 Archive](archive/v1/README.md).

---

## Professional Skills Demonstrated

**Trade Compliance & Customs Analytics:** Import data analysis, classification review workflows, valuation reconciliation, origin documentation review, and exception identification.

**Data Analytics & Engineering:** Relational data modeling, Python automation, reproducible datasets, data validation, and transactional traceability.

**Business Intelligence:** Analytical problem framing, KPI development, operational reporting foundations, and risk-based decision support.

**Project Development:** Version control, automated workflows, documentation, historical archiving, and iterative improvement.

---

## Disclaimer

GaiAnQi Global Trading is a fictional company. All suppliers, transactions, products, shipment records, and compliance scenarios are synthetic.

Tariff classifications and customs valuation scenarios are illustrative and should not be interpreted as regulatory determinations, legal advice, or evidence of actual compliance violations.

This project is intended for professional portfolio and educational demonstration purposes.
