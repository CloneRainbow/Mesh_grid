# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from st_aggrid import AgGrid, GridOptionsBuilder

# --- Імпорти ---
from warehouse import init_warehouse, get_inventory
from clients import init_clients, get_clients
from suppliers import init_suppliers, get_suppliers, get_purchase_orders
from finance import init_finance, get_cash_flow_df
from accounting import calculate_profit_loss
from utils.reports_finance import generate_pl_pdf, export_cash_flow_excel
from logistics import calculate_optimized_logistics
from config.settings import MIN_STOCK

# --- Ініціалізація ---
st.set_page_config(page_title="MeshGrid WMS Pro", layout="wide")
for init in [init_warehouse, init_clients, init_suppliers, init_finance]:
    init()

# --- Завантаження даних ---
@st.cache_data(ttl=300)
def load_all_data():
    return {
        "inventory": get_inventory(),
        "clients": get_clients(),
        "suppliers": get_suppliers(),
        "orders": get_purchase_orders(),
        "cash_flow": get_cash_flow_df(),
        "pl": calculate_profit_loss()
    }

data = load_all_data()

# --- UI ---
st.title("MeshGrid WMS Pro")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Дашборд", "Склад", "Закупівлі", "Логістика", "Фінанси"])

with tab1:
    st.plotly_chart(px.bar(data["pl"], x="period", y="profit", title="Прибуток"), use_container_width=True)

with tab2:
    st.dataframe(data["inventory"])
    rec = pd.DataFrame([{"material": k, "to_order": max(0, v - data["inventory"][data["inventory"]["material"] == k]["quantity"].sum())} for k, v in MIN_STOCK.items()])
    st.dataframe(rec[rec["to_order"] > 0])

with tab3:
    st.dataframe(data["orders"])

with tab4:
    with st.form("logistics"):
        distance = st.number_input("Відстань", 300)
        weight = st.number_input("Вага", 10000.0)
        rolls = st.number_input("Рулонів", 100)
        if st.form_submit_button("Розрахувати"):
            res = calculate_optimized_logistics(distance, weight, rolls)
            st.metric("Витрати", f"₴{res.total_cost:,.0f}")

with tab5:
    st.download_button("PDF P&L", generate_pl_pdf(data["pl"]), "pl.pdf")
    st.download_button("Excel Cash Flow", export_cash_flow_excel(data["cash_flow"]), "cash.xlsx")
