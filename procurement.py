# procurement.py — ГОТОВИЙ ДО ІМПОРТУ В app.py
import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

# --- Шляхи до баз ---
WAREHOUSE_DB = "data/warehouse.db"
SUPPLIERS_DB = "data/suppliers.db"

# --- Мінімальні запаси ---
MIN_STOCK = {
    "Оцинкований": 50,
    "Чорний": 30,
    "ПВХ": 20,
    "Мідний": 10
}

# ===================================================================
# 1. ПОТОЧНИЙ ЗАПАС
# ===================================================================
@st.cache_data(ttl=300)
def get_current_stock():
    """Повертає поточний запас: матеріал → кількість"""
    try:
        conn = sqlite3.connect(WAREHOUSE_DB)
        df = pd.read_sql_query("""
            SELECT material, SUM(quantity) as total_quantity
            FROM inventory
            WHERE quantity > 0
            GROUP BY material
        """, conn)
        conn.close()
        return dict(zip(df["material"], df["total_quantity"]))
    except Exception as e:
        st.error(f"Помилка читання складу: {e}")
        return {}

# ===================================================================
# 2. РЕКОМЕНДАЦІЇ ПО ЗАКУПІВЛЯХ
# ===================================================================
@st.cache_data(ttl=300)
def recommend_procurement():
    """
    Повертає DataFrame з рекомендаціями:
    - Матеріал
    - Поточний запас
    - Мін. запас
    - Треба замовити
    - Пріоритет
    """
    current = get_current_stock()
    recommendations = []

    for material, min_qty in MIN_STOCK.items():
        current_qty = current.get(material, 0)
        to_order = max(0, min_qty - current_qty)
        recommendations.append({
            "material": material,
            "current_stock": current_qty,
            "min_stock": min_qty,
            "to_order": to_order,
            "priority": "Високий" if to_order > 0 else "OK"
        })

    df = pd.DataFrame(recommendations)
    df = df[df["to_order"] > 0]  # Тільки те, що треба замовити
    df = df.sort_values("to_order", ascending=False)
    return df

# ===================================================================
# 3. СТВОРЕННЯ ЗАМОВЛЕННЯ
# ===================================================================
def create_purchase_order(supplier_id: int, material: str, quantity: int, price_per_unit: float):
    """
    Додає нове замовлення в таблицю purchase_orders
    """
    total_cost = quantity * price_per_unit
    order_date = datetime.now().strftime("%Y-%m-%d")
    delivery_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

    try:
        conn = sqlite3.connect(SUPPLIERS_DB)
        conn.execute("""
            INSERT INTO purchase_orders 
            (supplier_id, material, quantity, price_per_unit, total_cost, status, order_date, delivery_date)
            VALUES (?, ?, ?, ?, ?, 'planned', ?, ?)
        """, (supplier_id, material, quantity, price_per_unit, total_cost, order_date, delivery_date))
        conn.commit()
        conn.close()
        st.success(f"Замовлення на {quantity} од. {material} створено!")
        st.cache_data.clear()  # Оновлюємо кеш
    except Exception as e:
        st.error(f"Помилка створення замовлення: {e}")

# ===================================================================
# 4. АКТИВНІ ЗАМОВЛЕННЯ
# ===================================================================
@st.cache_data(ttl=300)
def get_active_orders():
    """Повертає активні замовлення (planned, ordered) з назвою постачальника"""
    try:
        conn = sqlite3.connect(SUPPLIERS_DB)
        df = pd.read_sql_query("""
            SELECT po.*, s.name as supplier_name
            FROM purchase_orders po
            JOIN suppliers s ON po.supplier_id = s.id
            WHERE po.status IN ('planned', 'ordered')
            ORDER BY po.order_date DESC
        """, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Помилка читання замовлень: {e}")
        return pd.DataFrame()
