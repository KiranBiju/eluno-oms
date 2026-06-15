"""Orders management page."""

import frontend.bootstrap  # noqa: F401
import pandas as pd
import streamlit as st

from api_client import api
from frontend.constants import COATINGS, LENS_INDICES, LENS_TYPES, ORDER_STATUSES, STORE_LOCATIONS, get_valid_next_statuses

st.set_page_config(page_title="Orders | Eluno OMS", layout="wide")
st.title("📦 Orders")

tab_list, tab_create = st.tabs(["Order List", "Create Order"])

with tab_create:
    st.subheader("Create New Order")
    with st.form("create_order_form"):
        c1, c2 = st.columns(2)
        customer_name = c1.text_input("Customer Name*")
        customer_phone = c2.text_input("Customer Phone*")
        store_location = c1.selectbox("Store Location", STORE_LOCATIONS)
        frame_name = c2.text_input("Frame Name*", value="Eluno Classic")

        c3, c4, c5 = st.columns(3)
        sphere = c3.number_input("Sphere (SPH)", -20.0, 20.0, 0.0, 0.25)
        cylinder = c4.number_input("Cylinder (CYL)", -10.0, 10.0, 0.0, 0.25)
        axis = c5.number_input("Axis", 0, 180, 0)

        c6, c7, c8 = st.columns(3)
        lens_type = c6.selectbox("Lens Type", LENS_TYPES)
        lens_index = c7.selectbox("Lens Index", LENS_INDICES)
        coating = c8.selectbox("Coating", COATINGS)

        submitted = st.form_submit_button("Create Order", type="primary")
        if submitted:
            if not customer_name or not customer_phone or not frame_name:
                st.error("Please fill all required fields.")
            else:
                try:
                    data = {
                        "customer_name": customer_name,
                        "customer_phone": customer_phone,
                        "store_location": store_location,
                        "sphere": sphere,
                        "cylinder": cylinder,
                        "axis": int(axis),
                        "lens_type": lens_type,
                        "lens_index": lens_index,
                        "coating": coating,
                        "frame_name": frame_name,
                    }
                    avail = api.check_availability({
                        "sphere": sphere, "cylinder": cylinder,
                        "axis": int(axis), "lens_type": lens_type, "coating": coating,
                    })
                    order = api.create_order(data)
                    st.success(
                        f"Order #{order['id']} created! "
                        f"Lens: {avail['availability']} (TAT +{avail['estimated_tat_days']} days)"
                    )
                except Exception as exc:
                    st.error(f"Failed to create order: {exc}")

with tab_list:
    st.subheader("Filter Orders")
    fc1, fc2, fc3, fc4 = st.columns(4)
    filter_status = fc1.selectbox("Status", ["All"] + ORDER_STATUSES)
    filter_store = fc2.selectbox("Store", ["All"] + STORE_LOCATIONS)
    filter_lens = fc3.selectbox("Lens Type", ["All"] + LENS_TYPES)
    search = fc4.text_input("Search (name/phone/frame)")

    filters = {}
    if filter_status != "All":
        filters["status"] = filter_status
    if filter_store != "All":
        filters["store_location"] = filter_store
    if filter_lens != "All":
        filters["lens_type"] = filter_lens
    if search:
        filters["search"] = search

    try:
        orders = api.get_orders(**filters)
    except Exception as exc:
        st.error(f"Failed to load orders: {exc}")
        st.stop()

    if not orders:
        st.info("No orders match your filters.")
    else:
        rows = []
        for o in orders:
            sla = o.get("sla_metrics", {})
            rows.append({
                "ID": o["id"],
                "Customer": o["customer_name"],
                "Store": o["store_location"],
                "Lens Type": o["lens_type"],
                "Status": o["status"],
                "Created": o["created_at"][:10],
                "Expected Delivery": o["expected_delivery"][:10],
                "SLA Remaining": f"{sla.get('time_remaining_days', 'N/A')} days",
                "SLA Health": sla.get("sla_health", "N/A"),
                "Delay Reason": sla.get("delay_reason") or "—",
                "Risk": o.get("risk_level") or "—",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Update Order Status")
    if orders:
        order_ids = [o["id"] for o in orders]
        selected_id = st.selectbox("Select Order ID", order_ids)
        selected = next(o for o in orders if o["id"] == selected_id)
        next_statuses = get_valid_next_statuses(selected["status"])

        if next_statuses:
            new_status = st.selectbox("New Status", next_statuses)
            reason = st.text_input("Reason (optional)")
            if st.button("Update Status"):
                try:
                    api.update_order_status(selected_id, new_status, reason)
                    st.success(f"Order #{selected_id} updated to '{new_status}'")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Status update failed: {exc}")
        else:
            st.info(f"Order #{selected_id} is at terminal status: {selected['status']}")

        with st.expander("View Status History"):
            try:
                history = api.get_order_history(selected_id)
                for h in history:
                    st.write(f"**{h['changed_at'][:19]}** — {h['old_status']} → **{h['new_status']}** ({h.get('reason') or 'N/A'})")
            except Exception as exc:
                st.error(str(exc))
