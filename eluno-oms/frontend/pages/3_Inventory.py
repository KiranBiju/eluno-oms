"""Inventory management page."""

import frontend.bootstrap  # noqa: F401
import pandas as pd
import streamlit as st

from api_client import api
from frontend.constants import COATINGS, LENS_INDICES, LENS_TYPES

st.set_page_config(page_title="Inventory | Eluno OMS", layout="wide")
st.title("🔍 Inventory")

tab_list, tab_add, tab_check = st.tabs(["Inventory List", "Add Item", "Check Availability"])

with tab_add:
    st.subheader("Add Inventory Item")
    with st.form("add_inventory"):
        c1, c2, c3 = st.columns(3)
        sphere = c1.number_input("Sphere", -20.0, 20.0, 0.0, 0.25)
        cylinder = c2.number_input("Cylinder", -10.0, 10.0, 0.0, 0.25)
        axis = c3.number_input("Axis", 0, 180, 0)

        c4, c5, c6 = st.columns(3)
        lens_type = c4.selectbox("Lens Type", LENS_TYPES, key="add_lens_type")
        lens_index = c5.selectbox("Lens Index", LENS_INDICES, key="add_lens_index")
        coating = c6.selectbox("Coating", COATINGS, key="add_coating")

        c7, c8 = st.columns(2)
        stock = c7.number_input("Stock Quantity", 0, 1000, 10)
        vendor = c8.text_input("Vendor Name", "Essilor India")

        if st.form_submit_button("Add Item", type="primary"):
            try:
                api.create_inventory({
                    "sphere": sphere, "cylinder": cylinder, "axis": int(axis),
                    "lens_type": lens_type, "lens_index": lens_index,
                    "coating": coating, "stock_quantity": int(stock),
                    "vendor_name": vendor,
                })
                st.success("Inventory item added.")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

with tab_check:
    st.subheader("Lens Availability Check")
    with st.form("check_avail"):
        c1, c2, c3 = st.columns(3)
        sphere = c1.number_input("Sphere", -20.0, 20.0, -2.0, 0.25, key="chk_sph")
        cylinder = c2.number_input("Cylinder", -10.0, 10.0, 0.0, 0.25, key="chk_cyl")
        axis = c3.number_input("Axis", 0, 180, 0, key="chk_axis")
        c4, c5 = st.columns(2)
        lens_type = c4.selectbox("Lens Type", LENS_TYPES, key="chk_type")
        coating = c5.selectbox("Coating", COATINGS, key="chk_coating")

        if st.form_submit_button("Check Availability"):
            try:
                result = api.check_availability({
                    "sphere": sphere, "cylinder": cylinder,
                    "axis": int(axis), "lens_type": lens_type, "coating": coating,
                })
                if result["in_stock"]:
                    st.success(f"✅ **In House** — {result['stock_quantity']} units available. Est. TAT: {result['estimated_tat_days']} day(s)")
                else:
                    st.warning(f"⚠️ **Vendor Procurement** — Est. TAT: {result['estimated_tat_days']} days")
            except Exception as exc:
                st.error(str(exc))

with tab_list:
    try:
        items = api.get_inventory()
    except Exception as exc:
        st.error(f"Failed to load inventory: {exc}")
        st.stop()

    if not items:
        st.info("No inventory items. Add items using the 'Add Item' tab.")
    else:
        df = pd.DataFrame(items)
        display = df[["id", "sphere", "cylinder", "axis", "lens_type", "lens_index", "coating", "stock_quantity", "vendor_name"]]
        st.dataframe(display, use_container_width=True, hide_index=True)

        st.subheader("Update / Delete")
        item_id = st.selectbox("Select Item ID", [i["id"] for i in items])
        item = next(i for i in items if i["id"] == item_id)
        new_stock = st.number_input("Update Stock Quantity", 0, 1000, item["stock_quantity"])
        c1, c2 = st.columns(2)
        if c1.button("Update Stock"):
            try:
                api.update_inventory(item_id, {"stock_quantity": int(new_stock)})
                st.success("Stock updated.")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))
        if c2.button("Delete Item", type="secondary"):
            try:
                api.delete_inventory(item_id)
                st.success("Item deleted.")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))
