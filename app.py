# app.py
import streamlit as st
import pandas as pd
import os
import base64
from io import BytesIO
from datetime import datetime

# --- Імпорти з перевіркою ---
try:
    from calculations import calculate_weight_1m2, calculate_total_length, calculate_cost
    from database import (
        init_db, add_calculation, get_history, clear_history,
        get_clients, get_suppliers, add_client, add_supplier
    )
    from logistics import calculate_logistics_cost
    from utils.export import export_to_csv, export_to_excel
    from utils.charts import create_cost_chart, create_weight_chart
except Exception as e:
    st.error("Помилка імпорту модулів!")
    st.error(f"Деталі: {e}")
    st.stop()

# --- Налаштування ---
st.set_page_config(page_title="Сітка-Рябиця Pro", layout="wide", initial_sidebar_state="expanded")
os.makedirs("data", exist_ok=True)
init_db()

# --- Сесія ---
if 'calc_history' not in st.session_state:
    st.session_state.calc_history = []
if 'last_calc' not in st.session_state:
    st.session_state.last_calc = None

# --- Сайдбар: Змінні формули ---
with st.sidebar:
    st.header("Формули")
    weight_factor = st.number_input("Коефіцієнт ваги (13.4)", 10.0, 20.0, 13.4, 0.1)
    length_factor = st.number_input("Коефіцієнт довжини (2173)", 2000, 3000, 2173, 10)

# --- ВКЛАДКИ ---
tab_calc, tab_history, tab_clients, tab_suppliers, tab_logistics, tab_reports = st.tabs([
    "Калькулятор", "Історія", "Клієнти", "Постачальники", "Логістика", "Звіти"
])

# ===================================================================
# ВКЛАДКА 1: КАЛЬКУЛЯТОР
# ===================================================================
with tab_calc:
    st.header("Ручний розрахунок сітки-рябиці")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Параметри сітки")
        material = st.selectbox("Матеріал", ["Оцинкований", "Чорний", "Мідний", "ПВХ"])
        cell_size = st.number_input("Розмір вічка (мм)", 10, 100, 25, 1)
        wire_thickness = st.number_input("Тonemщина дроту (мм)", 1.0, 3.0, 1.6, 0.1)
        roll_length = st.number_input("Довжина рулону (м)", 1.0, 100.0, 10.0, 0.5)
        roll_height = st.number_input("Висота рулону (м)", 0.5, 3.0, 1.5, 0.1)

    with col2:
        st.subheader("Фінанси")
        price_per_kg = st.number_input("Ціна за 1 кг (грн)", 1.0, 1000.0, 75.0, 1.0)
        margin_pct = st.slider("Маржа (%)", 0, 100, 30)
        distance_km = st.number_input("Відстань логістики (км)", 0, 1000, 100, 10)

    if st.button("Розрахувати", type="primary", use_container_width=True):
        # --- Розрахунок ---
        area = roll_length * roll_height
        weight_1m2 = calculate_weight_1m2(cell_size, wire_thickness, material, weight_factor)
        total_length = calculate_total_length(cell_size, area, length_factor)
        total_weight = round(weight_1m2 * area, 2)
        purchase_cost = calculate_cost(total_weight, price_per_kg)
        sale_price = round(purchase_cost * (1 + margin_pct / 100), 2)
        logistics_cost = calculate_logistics_cost(distance_km)
        profit = round(sale_price - purchase_cost - logistics_cost, 2)
        real_margin = round(profit / purchase_cost * 100, 1) if purchase_cost > 0 else 0

        # --- Збереження в історію ---
        calc_record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "material": material,
            "cell_size": cell_size,
            "wire_thickness": wire_thickness,
            "roll_length": roll_length,
            "roll_height": roll_height,
            "price_per_kg": price_per_kg,
            "margin_pct": margin_pct,
            "purchase_cost": purchase_cost,
            "sale_price": sale_price,
            "profit": profit,
            "area": area,
            "total_weight": total_weight
        }
        add_calculation(calc_record)
        st.session_state.calc_history.append(calc_record)
        st.session_state.last_calc = calc_record

        # --- Вивід ---
        st.success("Розрахунок завершено!")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Площа", f"{area:.2f} м²")
        c2.metric("Вага 1 м²", f"{weight_1m2:.2f} кг")
        c3.metric("Загальна вага", f"{total_weight:.2f} кг")
        c4.metric("Прибуток", f"{profit:,.2f} грн")

        df_res = pd.DataFrame({
            "Показник": ["Собівартість", "Ціна продажу", "Логістика", "Маржа %"],
            "Значення": [f"{purchase_cost:,.2f} грн", f"{sale_price:,.2f} грн", f"{logistics_cost:,.2f} грн", f"{real_margin:.1f}%"]
        })
        st.table(df_res)

        # --- Графіки (Plotly) ---
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            fig_cost = create_cost_chart(material, f"{cell_size}×{cell_size}", purchase_cost)
            if fig_cost:
                st.plotly_chart(fig_cost, use_container_width=True)
            else:
                st.warning("Plotly недоступний")
        with col_g2:
            fig_weight = create_weight_chart(roll_height, total_weight)
            if fig_weight:
                st.plotly_chart(fig_weight, use_container_width=True)

# ===================================================================
# ВКЛАДКА 2: ІСТОРІЯ
# ===================================================================
with tab_history:
    st.header("Історія розрахунків")
    history_df = get_history(100)
    if not history_df.empty:
        st.dataframe(history_df.drop(columns=["id"]), use_container_width=True)
        if st.button("Очистити історію"):
            clear_history()
            st.success("Історія очищена!")
            st.rerun()
    else:
        st.info("Історія порожня")

# ===================================================================
# ВКЛАДКА 3: КЛІЄНТИ
# ===================================================================
with tab_clients:
    st.header("База клієнтів")
    df_clients = get_clients()
    if not df_clients.empty:
        st.dataframe(df_clients.drop(columns=["logo"], errors="ignore"), use_container_width=True)
    else:
        st.info("Немає клієнтів")

    with st.expander("Додати клієнта"):
        with st.form("add_client_form"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Ім'я")
                email = st.text_input("Email")
            with c2:
                phone = st.text_input("Телефон")
                balance = st.number_input("Баланс (грн)", value=0.0)
            logo = st.file_uploader("Логотип", type=["png", "jpg", "jpeg"])
            if st.form_submit_button("Зберегти"):
                logo_b64 = base64.b64encode(logo.read()).decode() if logo else None
                add_client(name, email, phone, balance, logo_b64)
                st.success("Клієнт додано!")
                st.rerun()

# ===================================================================
# ВКЛАДКА 4: ПОСТАЧАЛЬНИКИ
# ===================================================================
with tab_suppliers:
    st.header("База постачальників")
    df_suppliers = get_suppliers()
    if not df_suppliers.empty:
        st.dataframe(df_suppliers.drop(columns=["logo"], errors="ignore"), use_container_width=True)
    else:
        st.info("Немає постачальників")

    with st.expander("Додати постачальника"):
        with st.form("add_supplier_form"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Ім'я")
                email = st.text_input("Email")
            with c2:
                phone = st.text_input("Телефон")
                balance = st.number_input("Баланс (грн)", value=0.0)
            logo = st.file_uploader("Логотип", type=["png", "jpg", "jpeg"])
            if st.form_submit_button("Зберегти"):
                logo_b64 = base64.b64encode(logo.read()).decode() if logo else None
                add_supplier(name, email, phone, balance, logo_b64)
                st.success("Постачальник додано!")
                st.rerun()

# ===================================================================
# ВКЛАДКА 5: ЛОГІСТИКА
# ===================================================================
with tab_logistics:
    st.header("Розрахунок логістики")
    dist = st.number_input("Відстань (км)", 0, 1000, 100)
    tariff = st.number_input("Тариф (грн/км)", 0.1, 10.0, 1.0, 0.1)
    fixed = st.number_input("Фіксована плата (грн)", 0, 1000, 100)
    total = calculate_logistics_cost(dist, tariff, fixed)
    st.metric("Вартість логістики", f"{total:,.2f} грн")

# ===================================================================
# ВКЛАДКА 6: ЗВІТИ
# ===================================================================
with tab_reports:
    st.header("Експорт та PDF")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Експорт бази")
        if st.button("CSV — Клієнти"):
            path = export_to_csv(get_clients(), "clients.csv")
            with open(path, "rb") as f:
                st.download_button("Завантажити", f, "clients.csv", "text/csv")
        if st.button("Excel — Клієнти"):
            path = export_to_excel(get_clients(), "clients.xlsx")
            with open(path, "rb") as f:
                st.download_button("Завантажити", f, "clients.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    with col2:
        st.subheader("PDF-звіт")
        if st.session_state.last_calc and st.button("PDF останнього розрахунку"):
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Table, Paragraph
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet

            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()
            calc = st.session_state.last_calc

            elements.append(Paragraph("Звіт по сітці-рябиці", styles["Title"]))
            elements.append(Paragraph(f"Дата: {calc['timestamp']}", styles["Normal"]))

            data = [["Параметр", "Значення"]] + [
                ["Матеріал", calc["material"]],
                ["Вічко", f"{calc['cell_size']}×{calc['cell_size']} мм"],
                ["Площа", f"{calc['area']:.2f} м²"],
                ["Вага", f"{calc['total_weight']:.2f} кг"],
                ["Собівартість", f"{calc['purchase_cost']:,.2f} грн"],
                ["Продаж", f"{calc['sale_price']:,.2f} грн"],
                ["Прибуток", f"{calc['profit']:,.2f} грн"]
            ]
            table = Table(data, colWidths=[200, 150])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('GRID', (0,0), (-1,-1), 0.5, colors.black),
                ('ALIGN', (1,1), (-1,-1), 'RIGHT')
            ]))
            elements.append(table)
            doc.build(elements)
            buffer.seek(0)
            st.download_button("Завантажити PDF", buffer, "sitka_report.pdf", "application/pdf")
