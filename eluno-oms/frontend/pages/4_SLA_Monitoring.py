"""SLA Monitoring page."""

import frontend.bootstrap  # noqa: F401
import pandas as pd
import streamlit as st

from api_client import api

HEALTH_COLORS = {"Green": "🟢", "Yellow": "🟡", "Red": "🔴"}

st.set_page_config(page_title="SLA Monitoring | Eluno OMS", layout="wide")
st.title("⏱️ SLA Monitoring")

col1, col2 = st.columns([3, 1])
with col2:
    if st.button("🤖 Run Predictions", type="primary"):
        try:
            result = api.run_predictions()
            st.success(
                f"Scored {result['orders_scored']} orders. "
                f"{result['high_risk_count']} high risk. "
                f"{result['alerts_triggered']} alerts sent."
            )
        except Exception as exc:
            st.error(str(exc))

try:
    orders = api.get_orders(limit=100)
except Exception as exc:
    st.error(f"Failed to load orders: {exc}")
    st.stop()

active = [o for o in orders if o["status"] != "Delivered"]

if not active:
    st.info("No active orders to monitor.")
    st.stop()

health_filter = col1.selectbox("Filter by SLA Health", ["All", "Green", "Yellow", "Red"])

rows = []
for o in active:
    sla = o.get("sla_metrics", {})
    health = sla.get("sla_health", "Green")
    if health_filter != "All" and health != health_filter:
        continue
    rows.append({
        "Order ID": o["id"],
        "Customer": o["customer_name"],
        "Status": o["status"],
        "SLA Days": sla.get("sla_days"),
        "Days Elapsed": sla.get("days_elapsed"),
        "Time Remaining": f"{sla.get('time_remaining_days', 0)} days",
        "SLA Health": f"{HEALTH_COLORS.get(health, '')} {health}",
        "Expected Delivery": o["expected_delivery"][:10],
        "Delay Reason": sla.get("delay_reason") or "—",
        "Breach %": f"{(o.get('breach_probability') or 0) * 100:.1f}%",
        "Risk Level": o.get("risk_level") or "—",
    })

if rows:
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("SLA Health Summary")
    health_counts = pd.Series([r.split()[-1] for r in df["SLA Health"]]).value_counts()
    c1, c2, c3 = st.columns(3)
    c1.metric("🟢 Green", health_counts.get("Green", 0))
    c2.metric("🟡 Yellow", health_counts.get("Yellow", 0))
    c3.metric("🔴 Red", health_counts.get("Red", 0))
else:
    st.info(f"No orders with SLA health '{health_filter}'.")
