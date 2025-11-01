# app.py — ОПТИМІЗОВАНИЙ, БЕЗ PLOTLY
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- Імпорти модулів ---
from warehouse import init_warehouse, get_inventory
from clients import init_clients, get_clients
from suppliers import init_suppliers, get_suppliers, get_purchase_orders
from finance import init_finance, get_cash_flow_df
from accounting import calculate_profit_loss
from logistics import calculate_optimized_logistics
from utils.reports_finance import generate_pl_pdf

# --- Ініціалізація ---
st.set_page_config(
    page_title="MeshGrid WMS Pro",
    page_icon="grid",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ініціалізуємо бази один раз
for init_func in [init_warehouse, init_clients, init_suppliers, init_finance]:
    init_func()

# --- Кешування даних ---
@st.cache_data(ttl=300, show_spinner="Завантаження даних...")
def load_all_data():
    return {
        "inventory": get_inventory(),
        "clients": get_clients(),
        "orders": get_purchase_orders(),
        "cash_flow": get_cash_flow_df(),
        "pl": calculate_profit_loss()
    }

# --- Сайдбар ---
with st.sidebar:
    st.image("https://via.placeholder.com/150", width=150)
    st.title("MeshGrid Pro")
    st.caption("Система управління складом та фінансами")

    if st.button("Оновити дані", use_container_width=True):
        st.cache_data.clear()
        st.success("Кеш очищено!")
        st.rerun()

    st.divider()
    st.caption("© 2025 MeshGrid")

# --- Заголовок ---
st.title("MeshGrid WMS Pro")
st.caption("Професійний WMS без зайвих залежностей")

# --- Завантаження даних ---
data = load_all_data()

# --- Вкладки ---
tab_dashboard, tab_warehouse, tab_procurement, tab_logistics, tab_finance = st.tabs([
    "Дашборд", "Склад", "Закупівлі", "Логістика", "Фінанси"
])

# ===================================================================
# ДАШБОРД
# ===================================================================
with tab_dashboard:
    st.subheader("Фінансовий огляд")

    if not data["pl"].empty:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Загальний прибуток", f"₴{data['pl']['profit'].sum():,.0f}")
        with col2:
            st.metric("Періодів", len(data["pl"]))

        st.bar_chart(
            data["pl"].set_index("month")["profit"],
            use_container_width=True,
            height=300
        )
        st.line_chart(
            data["pl"].set_index("month")[["income", "expense"]],
            use_container_width=True,
            height=300
        )
    else:
        st.info("Фінансові дані відсутні")

# ===================================================================
# СКЛАД
# ===================================================================
with tab_warehouse:
    st.subheader("Інвентаризація")

    if not data["inventory"].empty:
        total_value = (data["inventory"]["quantity"] * data["inventory"]["price_per_unit"]).sum()
        st.metric("Вартість запасів", f"₴{total_value:,.0f}")

        st.dataframe(
            data["inventory"].style.format({
                "price_per_unit": "₴{:.2f}",
                "total_cost": "₴{:.2f}"
            }),
            use_container_width=True
        )
    else:
        st.info("Склад порожній")

# ===================================================================
# ЗАКУПІВЛІ
# ===================================================================
with tab_procurement:
    st.subheader("Замовлення постачальникам")

    if not data["orders"].empty:
        st.dataframe(data["orders"], use_container_width=True)
    else:
        st.info("Немає активних замовлень")

# ===================================================================
# ЛОГІСТИКА
# ===================================================================
with tab_logistics:
    st.subheader("Оптимізація логістики")

    with st.form("logistics_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            distance = st.number_input(
                "Відстань (км)", min_value=1, max_value=5000, value=300, step=10
            )
            weight = st.number_input(
                "Вага (кг)", min_value=0.0, max_value=50000.0, value=10000.0, step=100.0
            )
        with col2:
            rolls = st.number_input(
                "Кількість рулонів", min_value=1, max_value=1000, value=100, step=1
            )

        submitted = st.form_submit_button("Розрахувати", use_container_width=True)

        if submitted:
            result = calculate_optimized_logistics(distance, weight, rolls)

            st.success(f"**Загальна вартість: ₴{result.total_cost:,.0f}**")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Рейсів", result.trips)
            with col2:
                st.metric("Паливо + упаковка", f"₴{result.fuel_cost + result.packaging_cost:,.0f}")
            with col3:
                st.metric("CO₂", f"{result.co2:,.0f} кг")
            with col4:
                st.metric("Ефективність", f"{result.route_efficiency:.1f}%")

# ===================================================================
# ФІНАНСИ
# ===================================================================
with tab_finance:
    st.subheader("Фінансовий звіт (P&L)")

    if not data["pl"].empty:
        # PDF звіт
        pdf_buffer = generate_pl_pdf(data["pl"])
        st.download_button(
            label="Завантажити P&L (PDF)",
            data=pdf_buffer,
            file_name=f"profit_loss_{datetime.now().strftime('%Y%m')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

        st.dataframe(data["pl"], use_container_width=True)
    else:
        st.info("Немає фінансових операцій")

    st.subheader("Cash Flow")
    st.dataframe(data["cash_flow"], use_container_width=True)
