# suppliers.py — ПОВНИЙ, ВИПРАВЛЕНИЙ, З ПОЛЯМИ order_date, delivery_date
import sqlite3
import pandas as pd
import os
import streamlit as st
from datetime import datetime

DB_PATH = "data/suppliers.db"

def init_suppliers():
    """
    Ініціалізує базу suppliers.db:
    - Таблиця suppliers
    - Таблиця purchase_orders (з order_date, delivery_date)
    - Додає приклади
    - ALTER TABLE для старих баз
    """
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    
    # === ТАБЛИЦЯ POSTACHALNIKYV ===
    conn.execute("""CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        inn TEXT,
        address TEXT,
        phone TEXT,
        email TEXT,
        contact_person TEXT,
        rating REAL DEFAULT 5.0,
        created_date TEXT NOT NULL
    )""")

    # === ТАБЛИЦЯ ZAMOVLENNYA (PURCHASE ORDERS) ===
    conn.execute("""CREATE TABLE IF NOT EXISTS purchase_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_id INTEGER NOT NULL,
        material TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price_per_unit REAL NOT NULL,
        total_cost REAL NOT NULL,
        status TEXT DEFAULT 'planned',
        order_date TEXT,           -- ДОДАНО
        delivery_date TEXT         -- ДОДАНО
    )""")

    # === ДОДАЄМО ПОЛЯ, ЯКЩО ЇХ НЕМАЄ (ДЛЯ СТАРИХ БАЗ) ===
    try:
        conn.execute("ALTER TABLE purchase_orders ADD COLUMN order_date TEXT")
        print("Додано order_date")
    except sqlite3.OperationalError:
        pass  # Вже є

    try:
        conn.execute("ALTER TABLE purchase_orders ADD COLUMN delivery_date TEXT")
        print("Додано delivery_date")
    except sqlite3.OperationalError:
        pass  # Вже є

    # === ПРИКЛАДИ ДАНИХ ===
    # Постачальники
    conn.execute("INSERT OR IGNORE INTO suppliers (name, inn, address, phone, email, contact_person, created_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
                 ("ТОВ МеталПром", "1234567890", "Київ, вул. Металургів 10", "+380671234567", "metalprom@ukr.net", "Іван Металенко", "2025-10-01"))
    conn.execute("INSERT OR IGNORE INTO suppliers (name, inn, address, phone, email, contact_person, created_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
                 ("ФОП СтальБуд", "0987654321", "Харків, вул. Сталінградська 5", "+380672345678", "stalbud@gmail.com", "Олена Сталь", "2025-10-02"))

    # Замовлення
    today = datetime.now().strftime("%Y-%m-%d")
    future = (datetime.now() + pd.Timedelta(days=7)).strftime("%Y-%m-%d")
    conn.execute("""INSERT OR IGNORE INTO purchase_orders 
                 (supplier_id, material, quantity, price_per_unit, total_cost, status, order_date, delivery_date) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                 (1, "Оцинкований", 100, 75.0, 7500.0, "planned", today, future))
    conn.execute("""INSERT OR IGNORE INTO purchase_orders 
                 (supplier_id, material, quantity, price_per_unit, total_cost, status, order_date, delivery_date) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                 (2, "Чорний", 50, 55.0, 2750.0, "ordered", today, future))

    conn.commit()
    conn.close()

# ===================================================================
# ОТРИМАННЯ ДАНИХ
# ===================================================================
@st.cache_data(ttl=300)
def get_suppliers():
    """Повертає всіх постачальників"""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM suppliers", conn)
    conn.close()
    return df

@st.cache_data(ttl=300)
def get_purchase_orders():
    """Повертає всі замовлення з назвою постачальника"""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT po.*, s.name as supplier_name 
        FROM purchase_orders po 
        JOIN suppliers s ON po.supplier_id = s.id 
        ORDER BY po.id DESC
    """, conn)
    conn.close()
    return df

@st.cache_data(ttl=300)
def get_active_orders():
    """Повертає активні замовлення (для procurement.py)"""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT po.*, s.name as supplier_name
        FROM purchase_orders po
        JOIN suppliers s ON po.supplier_id = s.id
        WHERE po.status IN ('planned', 'ordered')
        ORDER BY po.order_date DESC
    """, conn)
    conn.close()
    return df
