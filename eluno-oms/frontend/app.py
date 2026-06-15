"""Eluno OMS — Streamlit application entry point."""

import bootstrap  # noqa: F401
import streamlit as st

st.set_page_config(
    page_title="Eluno OMS",
    page_icon="👓",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown("""
<style>
    .main-header { font-size: 3rem; font-weight: 800; color: #1a1a2e; }
    .sub-header { color: #666; font-size: 1.3rem; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header" style="color: #4A90E2;">👓 Eluno OMS</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="header"></p>',
    unsafe_allow_html=True,
)

st.info(
    "AI-Powered Order Management System for Eyewear Operations"
)

try:
    from api_client import api
    health = api.health()
    #st.success(f"Backend connected — {health.get('service', 'API')} is running.")
except Exception as exc:
    st.error(f"Backend not reachable at http://127.0.0.1:8000. Start with: `uvicorn backend.main:app --reload`")
    st.code(str(exc))

st.markdown("---")

st.subheader("🎯Features")

col1, col2 = st.columns(2)

with col1:
    if st.button(
        "📦 Inventory Management\n\nCheck stock, procurement and availability",
        use_container_width=True,
        key="inventory"
    ):
        st.switch_page("pages/3_Inventory.py")

    if st.button(
        "⚠ SLA Monitoring\n\nPredict delayed orders before SLA breach.",
        use_container_width=True,
        key="⚠ SLA Prediction"
    ):
        st.switch_page("pages/4_SLA_Monitoring.py")    

with col2:
    if st.button(
        "🚚 Order Lifecycle\n\nTrack orders through every manufacturing stage.",
        use_container_width=True,
        key="Orders"
    ):
        st.switch_page("pages/2_Orders.py")
        
    if st.button(
        "🤖 AI Copilot\n\nAsk questions about operations and orders",
        use_container_width=True,
        key="chatbot"
    ):
        st.switch_page("pages/6_AI_Copilot.py")
