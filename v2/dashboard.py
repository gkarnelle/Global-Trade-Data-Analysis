
"""GaiAnQi Global Trading - V2 Intelligence Dashboard."""

from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
ANALYTICS = ROOT / "analytics"

st.set_page_config(
    page_title="GaiAnQi | Trade Intelligence",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def load_data(filename):
    path = ANALYTICS / filename
    if not path.exists():
        st.error(f"Missing analytics file: {filename}")
        st.stop()
    return pd.read_csv(path)


def money(value):
    return f"${float(value):,.2f}"


def compact_money(value):
    value = float(value)
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:,.2f}M"
    if abs(value) >= 1_000:
        return f"${value / 1_000:,.1f}K"
    return money(value)


kpi_df = load_data("executive_kpis.csv")
kpis = dict(zip(kpi_df["metric"], kpi_df["value"]))

shipment_status = load_data("shipment_status_summary.csv")
transport_modes = load_data("transport_mode_summary.csv")
suppliers = load_data("supplier_summary.csv")
exception_categories = load_data(
    "exception_category_summary.csv"
)
exception_severity = load_data(
    "exception_severity_summary.csv"
)
exception_status = load_data(
    "exception_status_summary.csv"
)

st.sidebar.title("🌐 GaiAnQi")
st.sidebar.caption("Global Trading | Version 2.0")

page = st.sidebar.radio(
    "Explore intelligence",
    [
        "Executive Overview",
        "Import Operations",
        "Supplier Intelligence",
        "Compliance Intelligence",
        "Customs Valuation",
    ],
)

st.sidebar.divider()
st.sidebar.info(
    "Synthetic portfolio data. Compliance flags are "
    "preliminary review indicators, not confirmed violations."
)
st.sidebar.caption(
    f"Reporting as of {kpis['reporting_as_of_date']}"
)

st.title("GaiAnQi Global Trading")
st.caption(
    "Global Trade Data Analysis & Compliance Intelligence | V2"
)

if page == "Executive Overview":
    st.subheader("Executive Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Total Entered Value",
        compact_money(kpis["total_entered_value_usd"]),
    )
    c2.metric(
        "Purchase Order Value",
        compact_money(kpis["purchase_order_value_usd"]),
    )
    c3.metric(
        "Customs Entries",
        f"{int(kpis['customs_entries']):,}",
    )
    c4.metric(
        "Compliance Review Flags",
        f"{int(kpis['compliance_exceptions']):,}",
    )

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Transaction Volumes")
        volumes = pd.DataFrame(
            {
                "Stage": [
                    "Purchase Order Lines",
                    "Shipment Lines",
                    "Customs Entry Lines",
                ],
                "Records": [
                    int(kpis["purchase_order_lines"]),
                    int(kpis["shipment_lines"]),
                    int(kpis["customs_entry_lines"]),
                ],
            }
        ).set_index("Stage")
        st.bar_chart(volumes)

    with right:
        st.subheader("Compliance Review Categories")
        chart = exception_categories.set_index(
            "exception_category"
        )
        st.bar_chart(chart["exception_count"])

    st.info(
        "Review flags are synthetic, rule-generated scenarios. "
        "They should not be interpreted as confirmed violations "
        "or an observed regulatory noncompliance rate."
    )

elif page == "Import Operations":
    st.subheader("Import Operations")

    c1, c2, c3 = st.columns(3)
    c1.metric(
        "Total Shipments",
        f"{int(kpis['shipments']):,}",
    )
    c2.metric(
        "Customs Entries",
        f"{int(kpis['customs_entries']):,}",
    )
    c3.metric(
        "Shipment Lines",
        f"{int(kpis['shipment_lines']):,}",
    )

    left, right = st.columns(2)

    with left:
        st.subheader("Shipment Status")
        st.bar_chart(
            shipment_status.set_index("shipment_status")[
                "shipment_count"
            ]
        )

    with right:
        st.subheader("Transportation Modes")
        st.bar_chart(
            transport_modes.set_index("transport_mode")[
                "shipment_count"
            ]
        )

    st.caption(
        "Shipment statuses are derived from synthetic dates "
        "and are not independently verified carrier events."
    )

elif page == "Supplier Intelligence":
    st.subheader("Supplier Intelligence")

    c1, c2, c3 = st.columns(3)
    c1.metric("Suppliers", f"{len(suppliers):,}")
    c2.metric(
        "Supplier Countries",
        f"{suppliers['country'].nunique():,}",
    )
    c3.metric(
        "Total Supplier Entered Value",
        compact_money(
            suppliers["total_entered_value_usd"].sum()
        ),
    )

    risk_options = ["All"] + sorted(
        suppliers["supplier_risk_tier"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_risk = st.selectbox(
        "Filter by synthetic supplier risk tier",
        risk_options,
    )

    filtered = suppliers.copy()

    if selected_risk != "All":
        filtered = filtered[
            filtered["supplier_risk_tier"] == selected_risk
        ]

    st.subheader("Top Suppliers by Entered Value")
    top = filtered.nlargest(
        10, "total_entered_value_usd"
    )

    st.bar_chart(
        top.set_index("supplier_name")[
            "total_entered_value_usd"
        ]
    )

    st.subheader("Supplier Activity")
    st.dataframe(
        filtered.sort_values(
            "total_entered_value_usd",
            ascending=False,
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Supplier risk tiers and master on-time delivery "
        "percentages are generated attributes, not measured "
        "performance or independent risk assessments."
    )

elif page == "Compliance Intelligence":
    st.subheader("Compliance Intelligence")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Total Review Flags",
        f"{int(kpis['compliance_exceptions']):,}",
    )
    c2.metric(
        "Entries with Flags",
        f"{int(kpis['entries_with_exceptions']):,}",
    )
    c3.metric(
        "Flags per Entry",
        f"{int(kpis['compliance_exceptions']) / int(kpis['customs_entries']):.2f}",
    )

    left, right = st.columns(2)

    with left:
        st.subheader("Exception Categories")
        st.bar_chart(
            exception_categories.set_index(
                "exception_category"
            )["exception_count"]
        )

        st.subheader("Review Status")
        st.bar_chart(
            exception_status.set_index("review_status")[
                "exception_count"
            ]
        )

    with right:
        st.subheader("Severity Distribution")
        st.bar_chart(
            exception_severity.set_index("severity")[
                "exception_count"
            ]
        )

    st.warning(
        "All compliance exceptions are synthetic review "
        "indicators. Severity and review status are workflow "
        "attributes, not findings of legal violations."
    )

elif page == "Customs Valuation":
    st.subheader("Customs Valuation")

    invoice = float(kpis["customs_invoice_value_usd"])
    adjustments = float(
        kpis["valuation_adjustments_usd"]
    )
    entered = float(kpis["total_entered_value_usd"])

    c1, c2, c3 = st.columns(3)

    c1.metric("Invoice Value", compact_money(invoice))
    c2.metric(
        "Illustrative Adjustments",
        money(adjustments),
    )
    c3.metric("Total Entered Value", compact_money(entered))

    st.divider()
    st.subheader("Entered Value Reconciliation")

    reconciliation = pd.DataFrame(
        {
            "Component": [
                "Invoice Value",
                "Illustrative Adjustments",
                "Total Entered Value",
            ],
            "Amount (USD)": [
                invoice,
                adjustments,
                entered,
            ],
        }
    )

    st.dataframe(
        reconciliation,
        use_container_width=True,
        hide_index=True,
    )

    difference = round(
        invoice + adjustments - entered, 2
    )

    if difference == 0:
        st.success(
            "Reconciliation passed: Invoice value plus "
            "adjustments equals total entered value."
        )
    else:
        st.error(
            f"Reconciliation difference: ${difference:,.2f}"
        )

    st.caption(
        "Valuation adjustments are illustrative synthetic "
        "scenarios. Actual U.S. customs valuation requires "
        "fact-specific regulatory analysis."
    )

st.divider()
st.caption(
    "GaiAnQi Global Trading | Fictional company | "
    "Synthetic portfolio data | Human compliance review required"
)
