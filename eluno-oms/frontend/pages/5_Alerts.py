"""Alerts page."""

import frontend.bootstrap  # noqa: F401
import pandas as pd
import streamlit as st

from api_client import api

st.set_page_config(page_title="Alerts | Eluno OMS", layout="wide")
st.title("🚨 Alerts")

if st.button("🔄 Refresh Alerts"):
    st.rerun()

try:
    alerts = api.get_alerts()
except Exception as exc:
    st.error(f"Failed to load alerts: {exc}")
    st.stop()

if not alerts:
    st.info("No alerts yet. Run predictions from SLA Monitoring to generate breach alerts.")
else:
    st.metric("Total Alerts", len(alerts))
    rows = []
    for a in alerts:
        rows.append({
            "ID": a["id"],
            "Order ID": a["order_id"],
            "Customer": a.get("customer_name", "—"),
            "Order Status": a.get("order_status", "—"),
            "Type": a["alert_type"],
            "Message": a["message"],
            "Created": a["created_at"][:19],
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

st.divider()
st.caption(
    "Alerts are triggered when breach probability exceeds 70%. "
    "Email notifications will be sent"
)
