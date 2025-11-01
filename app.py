# app.py — ПОВНИЙ, ОПТИМІЗОВАНИЙ, ГОТОВИЙ ДО ДЕПЛОЮ
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO

# --- ІМПОРТИ МОДУЛІВ ---
from warehouse_calculator import calculate_warehouse_cost
from warehouse import init_warehouse, get_inventory
from clients import init_clients, get_clients
from suppliers import init_suppliers, get_suppliers, get_purchase_orders
from finance import init_finance, get_cash_flow_df
from accounting import calculate_profit_loss
from logistics import calculate_optimized_logistics
from procurement import recommend_procurement, create_purchase_order, get_active_orders
from utils.reports_finance import export_pl_to_excel

# --- ІНІЦІАЛІЗАЦІЯ ---
st.set_page_config(
    page_title="MeshGrid WMS Pro",
    page_icon="grid",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ініціалізуємо бази один раз
for init_func in [init_warehouse, init_clients, init_suppliers, init_finance]:
    init_func()

# --- КЕШУВАННЯ ДАНИХ ---
@st.cache_data(ttl=300, show_spinner="Завантаження даних...")
def load_all_data():
    return {
        "inventory": get_inventory(),
        "clients": get_clients(),
        "orders": get_purchase_orders(),
        "active_orders": get_active_orders(),
        "cash_flow": get_cash_flow_df(),
        "pl": calculate_profit_loss(),
        "recommendations": recommend_procurement()
    }

# --- САЙДБАР ---
with st.sidebar:
    st.image("https://via.placeholder.com/150", width=150)
    st.title("MeshGrid Pro")
    st.caption("Система управління сіткою-рябицею")

    if st.button("Оновити дані", use_container_width=True):
        st.cache_data.clear()
        st.success("Кеш очищено!")
        st.rerun()

    st.divider()
    st.caption("© 2025 MeshGrid")

# --- ЗАГОЛОВОК ---
st.title("MeshGrid WMS Pro")
st.caption("Професійна система для виробництва та логістики сітки-рябиці")

# --- ЗАВАНТАЖЕННЯ ДАНИХ ---
data = load_all_data()

# --- ВКЛАДКИ ---
tab_calc, tab_warehouse, tab_procurement, tab_logistics, tab_finance = st.tabs([
    "Калькулятор Сітки", "Склад", "Закупівлі", "Логістика", "Фінанси"
])

# ===================================================================
# 1. КАЛЬКУЛЯТОР СІТКИ
# ===================================================================
with tab_calc:
    st.header("Калькулятор Витрат на Виготовлення Сітки-Рябиці")

    col1, col2 = st.columns(2)
    with col1:
        material = st.selectbox("Матеріал", ["Оцинкований", "Чорний", "Мідний", "ПВХ"])
        cell_size = st.number_input("Розмір вічка (мм)", 10, 100, 25, step=5)
        wire_thick = st.number_input("Товщина дроту (мм)", 1.0, 3.0, 1.2, step=0.1)
    with col2:
        roll_len = st.number_input("Довжина рулону (м)", 1.0, 100.0, 10.0, step=0.5)
        roll_height = st.number_input("Висота рулону (м)", 0.5, 3.0, 1.5, step=0.1)
        custom_price = st.number_input("Ціна за кг (0 = стандарт)", 0.0, 1000.0, 0.0, step=5.0)

    if st.button("Розрахувати", type="primary", use_container_width=True):
        results, details_df = calculate_warehouse_cost(
            cell_size, wire_thick, roll_len, roll_height, material,
            custom_price if custom_price > 0 else None
        )

        if results:
            area = roll_len * roll_height
            total_wire = results["довжина_1м2"] * area

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Площа", f"{area:.2f} м²")
            col2.metric("Вага 1 м²", f"{results['вага_1м2']:.4f} кг")
            col3.metric("Загальна вага", f"{results['загальна_вага']:.2f} кг")
            col4.metric("Собівартість", f"₴{results['собівартість']:,.2f}")

            st.subheader("Деталі")
            st.dataframe(details_df, use_container_width=True)

            # Експорт
            buffer = BytesIO()
            details_df.to_excel(buffer, index=False, engine='openpyxl')
            buffer.seek(0)
            st.download_button(
                "Експорт в Excel",
                buffer,
                f"ситка_{cell_size}x{wire_thick}_{material}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("Помилка розрахунку")

# ===================================================================
# 2. СКЛАД
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
# 3. ЗАКУПІВЛІ
# ===================================================================
with tab_procurement:
    st.subheader("Рекомендації")
    if not data["recommendations"].empty:
        st.dataframe(data["recommendations"], use_container_width=True)

        with st.expander("Створити замовлення"):
            mat = st.selectbox("Матеріал", data["recommendations"]["material"].unique())
            qty = st.number_input("Кількість", 1, 1000, int(data["recommendations"][data["recommendations"]["material"] == mat]["to_order"].iloc[0]))
            price = st.number_input("Ціна за од.", 1.0, 1000.0, 75.0)
            if st.button("Замовити"):
                # Приклад: supplier_id = 1
                create_purchase_order(1, mat, qty, price)
    else:
        st.success("Запаси в нормі")

    st.subheader("Активні замовлення")
    st.dataframe(data["active_orders"], use_container_width=True)

# ===================================================================
# 4. ЛОГІСТИКА
# ===================================================================
with tab_logistics:
    st.subheader("Оптимізація логістики")

    with st.form("log_form"):
        col1, col2 = st.columns(2)
        with col1:
            distance = st.number_input("Відстань (км)", 1, 5000, 300)
            weight = st.number_input("Вага (кг)", 0.0, 50000.0, 10000.0)
        with col2:
            rolls = st.number_input("Рулонів", 1, 1000, 100)

        if st.form_submit_button("Розрахувати"):
            result = calculate_optimized_logistics(distance, weight, rolls)

            st.success(f"**Загальна вартість: ₴{result.total_cost:,.0f}**")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Рейсів", result.trips)
            col2.metric("Паливо + упаковка", f"₴{result.fuel_cost + result.packaging_cost:,.0f}")
            col3.metric("CO₂", f"{result.co2:,.0f} кг")
            col4.metric("Ефективність", f"{result.route_efficiency:.1f}%")

# ===================================================================
# 5. ФІНАНСИ
# ===================================================================
with tab_finance:
    st.subheader("P&L Звіт")

    if not data["pl"].empty:
        excel_buffer = export_pl_to_excel(data["pl"])
        st.download_button(
            "Завантажити P&L (Excel)",
            excel_buffer,
            f"PL_{datetime.now().strftime('%Y%m')}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        st.bar_chart(data["pl"].set_index("month")["profit"])
        st.line_chart(data["pl"].set_index("month")[["income", "expense"]])
    else:
        st.info("Немає фінансових даних")

    st.subheader("Cash Flow")
    st.dataframe(data["cash_flow"], use_container_width=True)
