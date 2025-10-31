import streamlit as st
import pandas as pd
import os
import base64
from io import BytesIO

# --- Імпорти з перевіркою ---
try:
    from calculations import calculate_weight, calculate_length, calculate_cost
    from database import init_db, add_client, add_supplier, get_clients, get_suppliers
    from logistics import calculate_logistics
    from utils.export import export_to_csv, export_to_excel
    from utils.charts import create_cost_chart, create_weight_chart
except Exception as e:
    st.error("Критична помилка імпорту модулів!")
    st.error(f"Деталі: {e}")
    st.stop()

# --- Налаштування ---
st.set_page_config(page_title="Сітка-Рябиця Калькулятор", layout="wide")
os.makedirs("data", exist_ok=True)
init_db()

# --- Заголовок ---
st.title("Сітка-Рябиця: Професійний Калькулятор")
st.caption("Розрахунок ваги, вартості, маржі, логістики та бази даних")

# --- Сайдбар ---
with st.sidebar:
    st.header("Параметри")
    material = st.selectbox("Матеріал", ["Оцинкований", "Чорний", "Мідний", "ПВХ"])
    size = st.selectbox("Вічко", ["25×25", "30×30", "35×35", "40×40", "45×45"])
    thickness = st.slider("Товщина дроту (мм)", 1.2, 2.0, 1.6, 0.1)
    height = st.slider("Висота рулону (м)", 1.25, 2.5, 1.5, 0.25)
    margin_pct = st.slider("Маржа (%)", 10, 70, 30)
    distance_km = st.number_input("Відстань логістики (км)", 0, 1000, 100)

# --- Розрахунки ---
a = int(size.split("×")[0])
area = height * 10  # стандартний рулон 10 м
weight_1m2 = calculate_weight(a, thickness, material)
length_total = calculate_length(a, area)
weight_total = round(weight_1m2 * area, 2)
purchase = calculate_cost(weight_total, material)
sale = round(purchase * (1 + margin_pct / 100), 2)
logistics = calculate_logistics(distance_km)
profit = round(sale - purchase - logistics, 2)
margin_real = round(profit / purchase * 100, 1) if purchase > 0 else 0

# --- Метрики ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Вага 1 м²", f"{weight_1m2:.2f} кг")
c2.metric("Довжина дроту", f"{length_total:,} м")
c3.metric("Загальна вага", f"{weight_total:.2f} кг")
c4.metric("Прибуток", f"{profit:,.2f} грн")

# --- Таблиця ---
df_res = pd.DataFrame({
    "Показник": ["Собівартість", "Ціна продажу", "Логістика", "Прибуток", "Маржа %"],
    "грн": [purchase, sale, logistics, profit, margin_real]
})
st.table(df_res.style.format({"грн": "{:,.2f}"}))

# --- Графіки ---
st.subheader("Графіки")
col_g1, col_g2 = st.columns(2)
with col_g1:
    fig_cost = create_cost_chart(material, size, purchase)
    if fig_cost:
        st.plotly_chart(fig_cost, use_container_width=True)
    else:
        st.warning("Графік недоступний (plotly не встановлено)")

with col_g2:
    fig_weight = create_weight_chart(height, weight_total)
    if fig_weight:
        st.plotly_chart(fig_weight, use_container_width=True)
    else:
        st.warning("Графік недоступний")

# --- Вкладки ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Клієнти", "Постачальники", "Логістика", "Експорт", "PDF"])

with tab1:
    st.subheader("Клієнти")
    df_clients = get_clients()
    if df_clients.empty:
        st.info("База порожня")
    else:
        st.dataframe(df_clients, use_container_width=True)

    with st.expander("Додати клієнта"):
        with st.form("add_client"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Ім'я")
                email = st.text_input("Email")
            with col2:
                phone = st.text_input("Телефон")
                balance = st.number_input("Баланс", value=0.0)
            logo = st.file_uploader("Логотип", type=["png", "jpg"])
            if st.form_submit_button("Зберегти"):
                logo_b64 = base64.b64encode(logo.read()).decode() if logo else None
                add_client(name, email, phone, balance, logo_b64)
                st.success("Додано!")

with tab2:
    st.subheader("Постачальники")
    df_suppliers = get_suppliers()
    if df_suppliers.empty:
        st.info("База порожня")
    else:
        st.dataframe(df_suppliers, use_container_width=True)

    with st.expander("Додати постачальника"):
        with st.form("add_supplier"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Ім'я")
                email = st.text_input("Email")
            with col2:
                phone = st.text_input("Телефон")
                balance = st.number_input("Баланс", value=0.0)
            logo = st.file_uploader("Логотип", type=["png", "jpg"])
            if st.form_submit_button("Зберегти"):
                logo_b64 = base64.b64encode(logo.read()).decode() if logo else None
                add_supplier(name, email, phone, balance, logo_b64)
                st.success("Додано!")

with tab3:
    st.write(f"**Логістика:** {logistics:,.2f} грн")

with tab4:
    st.subheader("Експорт")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("CSV Клієнти"):
            path = export_to_csv(df_clients, "clients.csv")
            with open(path, "rb") as f:
                st.download_button("Завантажити", f, "clients.csv", "text/csv")
    with col2:
        if st.button("Excel Клієнти"):
            path = export_to_excel(df_clients, "clients.xlsx")
            with open(path, "rb") as f:
                st.download_button("Завантажити", f, "clients.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

with tab5:
    if st.button("PDF Звіт"):
        buffer = BytesIO()
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet

        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        elements.append(Paragraph("Звіт по сітці-рябиці", styles["Title"]))

        data = [["Параметр", "Значення"]] + [
            ["Матеріал", material],
            ["Вічко", size],
            ["Вага 1 м²", f"{weight_1m2:.2f} кг"],
            ["Загальна вага", f"{weight_total:.2f} кг"],
            ["Собівартість", f"{purchase:,.2f} грн"],
            ["Прибуток", f"{profit:,.2f} грн"]
        ]
        table = Table(data)
        table.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.black)]))
        elements.append(table)
        doc.build(elements)
        buffer.seek(0)
        st.download_button("Завантажити PDF", buffer, "report.pdf", "application/pdf")
