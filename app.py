# app.py
import streamlit as st
import pandas as pd
import base64
from io import BytesIO
import os

from calculations import calculate_weight, calculate_length, calculate_cost
from database import init_db, add_client, add_supplier, get_clients, get_suppliers
from logistics import calculate_logistics
from utils.export import export_to_csv, export_to_excel
from utils.charts import create_cost_chart, create_weight_chart
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# --- Налаштування ---
st.set_page_config(page_title="Сітка-Рябиця Калькулятор", layout="wide", initial_sidebar_state="expanded")

# --- Ініціалізація ---
os.makedirs("data", exist_ok=True)
init_db()

# --- Заголовок ---
st.title("Сітка-Рябиця: Професійний Калькулятор")
st.markdown("**Розрахунок матеріалів, собівартості, маржі, логістики та баз клієнтів/постачальників**")

# --- Сайдбар ---
with st.sidebar:
    st.header("Параметри розрахунку")
    material = st.selectbox("Матеріал", ["Оцинкований", "Чорний", "Мідний", "ПВХ"])
    size = st.selectbox("Розмір вічка", ["25×25", "30×30", "35×35", "40×40", "45×45"])
    thickness = st.slider("Товщина дроту (мм)", 1.2, 2.0, 1.2, 0.1)
    height = st.slider("Висота рулону (м)", 1.25, 2.5, 1.5, 0.25)
    margin_pct = st.slider("Маржа (%)", 10, 70, 30)
    distance_km = st.number_input("Відстань логістики (км)", 0, 1000, 100, 10)

# --- Розрахунки ---
a = int(size.split("×")[0])
weight_1m2 = calculate_weight(a, thickness, material)
area = height * 10  # 10 м довжини (стандартний рулон)
length_total = calculate_length(a, area)
weight_total = weight_1m2 * area
purchase = calculate_cost(weight_total, material)
sale = purchase * (1 + margin_pct / 100)
logistics = calculate_logistics(distance_km)
profit = sale - purchase - logistics
margin_real = profit / purchase * 100 if purchase else 0

# --- Метрики ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Вага 1 м²", f"{weight_1m2:.2f} кг")
col2.metric("Довжина дроту", f"{length_total:,.0f} м")
col3.metric("Загальна вага", f"{weight_total:.2f} кг")
col4.metric("Чистий прибуток", f"{profit:,.2f} грн")

# --- Таблиця результатів ---
df_res = pd.DataFrame({
    "Показник": ["Собівартість", "Ціна продажу", "Логістика", "Прибуток", "Маржа реальна"],
    "Значення (грн)": [purchase, sale, logistics, profit, margin_real]
})
st.table(df_res.style.format({"Значення (грн)": "{:,.2f}"}))

# --- Графіки ---
st.subheader("Графіки")
col_g1, col_g2 = st.columns(2)
with col_g1:
    st.plotly_chart(create_cost_chart(material, size, purchase), use_container_width=True)
with col_g2:
    st.plotly_chart(create_weight_chart(height, weight_total), use_container_width=True)

# --- Вкладки ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Клієнти", "Постачальники", "Логістика", "Експорт", "PDF Звіт"])

# --- Клієнти ---
with tab1:
    st.subheader("База клієнтів")
    df_clients = get_clients()
    if df_clients.empty:
        st.info("База порожня. Додайте першого клієнта.")
    else:
        st.dataframe(df_clients, use_container_width=True)

    with st.expander("Додати клієнта"):
        with st.form("add_client"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Ім'я")
                email = st.text_input("Email")
            with c2:
                phone = st.text_input("Телефон")
                balance = st.number_input("Баланс (грн)", value=0.0)
            logo = st.file_uploader("Логотип (опціонально)", type=["png", "jpg", "jpeg"])
            if st.form_submit_button("Зберегти"):
                logo_b64 = base64.b64encode(logo.read()).decode() if logo else None
                add_client(name, email, phone, balance, logo_b64)
                st.success("Клієнт додано!")

# --- Постачальники ---
with tab2:
    st.subheader("База постачальників")
    df_suppliers = get_suppliers()
    if df_suppliers.empty:
        st.info("База порожня.")
    else:
        st.dataframe(df_suppliers, use_container_width=True)

    with st.expander("Додати постачальника"):
        with st.form("add_supplier"):
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

# --- Логістика ---
with tab3:
    st.write(f"**Витрати на логістику:** `{logistics:,.2f} грн` (відстань {distance_km} км)")

# --- Експорт ---
with tab4:
    st.subheader("Експорт даних")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("CSV — Клієнти"):
            csv_path = export_to_csv(df_clients, "clients.csv")
            with open(csv_path, "rb") as f:
                st.download_button("Завантажити CSV", f, file_name="clients.csv", mime="text/csv")
    with col2:
        if st.button("Excel — Клієнти"):
            xlsx_path = export_to_excel(df_clients, "clients.xlsx")
            with open(xlsx_path, "rb") as f:
                st.download_button("Завантажити Excel", f, file_name="clients.xlsx",
                                 mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# --- PDF Звіт ---
with tab5:
    if st.button("Створити PDF-звіт"):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph("Звіт по сітці-рябиці", styles["Title"]))
        elements.append(Paragraph(f"Дата: {pd.Timestamp.now().strftime('%d.%m.%Y')}", styles["Normal"]))

        data = [
            ["Параметр", "Значення"],
            ["Матеріал", material],
            ["Вічко", size],
            ["Товщина", f"{thickness} мм"],
            ["Висота", f"{height} м"],
            ["Вага 1 м²", f"{weight_1m2:.2f} кг"],
            ["Загальна вага", f"{weight_total:.2f} кг"],
            ["Довжина дроту", f"{length_total:,.0f} м"],
            ["Собівартість", f"{purchase:,.2f} грн"],
            ["Ціна продажу", f"{sale:,.2f} грн"],
            ["Логістика", f"{logistics:,.2f} грн"],
            ["Прибуток", f"{profit:,.2f} грн"],
            ["Маржа", f"{margin_real:.1f} %"]
        ]

        table = Table(data, colWidths=[200, 120])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]))
        elements.append(table)
        doc.build(elements)
        buffer.seek(0)
        st.download_button("Завантажити PDF", buffer, file_name="sitka_report.pdf", mime="application/pdf")
