"""Dashboard Overview page."""

import frontend.bootstrap  # noqa: F401
import pandas as pd
import plotly.express as px
import streamlit as st

from frontend.api_client import api

st.set_page_config(page_title="Dashboard | Eluno OMS", layout="wide")
st.title("📊 Dashboard Overview")

try:
    stats = api.get_order_stats()
    inv_summary = api.get_inventory_summary()
    orders = api.get_orders(limit=100)
    predictions = api.get_predictions()
except Exception as exc:
    st.error(f"Failed to load dashboard data: {exc}")
    st.stop()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Orders", stats.get("total_orders", 0))
col2.metric("Active Orders", stats.get("active_orders", 0))
col3.metric("Delivered", stats.get("delivered_orders", 0))
col4.metric("At Risk / Breached", stats.get("breached_or_at_risk", 0))
high_risk = len([p for p in predictions if p.get("risk_level") == "High"])
col5.metric("High Risk Orders", high_risk)

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("Order Status Distribution")
    if orders:
        status_counts = pd.Series([o["status"] for o in orders]).value_counts()
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=350)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No orders yet. Create orders from the Orders page.")

with right:
    st.subheader("Risk Distribution")
    if predictions:
        risk_counts = pd.Series([p.get("risk_level", "Unknown") for p in predictions]).value_counts()
        colors = {"Low": "#2ecc71", "Medium": "#f39c12", "High": "#e74c3c"}
        fig = px.bar(
            x=risk_counts.index,
            y=risk_counts.values,
            color=risk_counts.index,
            color_discrete_map=colors,
            labels={"x": "Risk Level", "y": "Orders"},
        )
        fig.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20), height=350)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Run predictions from SLA Monitoring page.")

st.divider()

inv_col1, inv_col2 = st.columns(2)

with inv_col1:
    st.subheader("Inventory Availability")
    inv_data = {
        "Category": ["In Stock SKUs", "Low Stock", "Out of Stock"],
        "Count": [
            inv_summary.get("in_stock_skus", 0),
            inv_summary.get("low_stock_skus", 0),
            inv_summary.get("out_of_stock_skus", 0),
        ],
    }
    fig = px.bar(
        inv_data,
        x="Category",
        y="Count",
        color="Category",
        color_discrete_sequence=["#27ae60", "#f39c12", "#e74c3c"],
    )
    fig.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20), height=300)
    st.plotly_chart(fig, use_container_width=True)

with inv_col2:
    st.subheader("Recent High-Risk Orders")
    if predictions:
        df = pd.DataFrame(predictions[:5])
        display_cols = ["order_id", "customer_name", "status", "breach_probability", "risk_level"]
        df["breach_probability"] = (df["breach_probability"] * 100).round(1).astype(str) + "%"
        st.dataframe(df[display_cols], use_container_width=True, hide_index=True)
    else:
        st.info("No predictions available.")

if st.button("🔄 Refresh Dashboard"):
    st.rerun()
