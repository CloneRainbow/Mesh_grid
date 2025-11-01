import sqlite3
import pandas as pd
import os
from datetime import datetime

DB_PATH = "data/suppliers.db"

def init_suppliers():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, rating REAL DEFAULT 5.0
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS purchase_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_id INTEGER, material TEXT, quantity INTEGER,
        price_per_unit REAL, total_cost REAL, status TEXT, delivery_date TEXT
    )""")
    # Приклади
    conn.execute("INSERT OR IGNORE INTO suppliers (name) VALUES (?)", ("МеталПром",))
    conn.execute("INSERT OR IGNORE INTO purchase_orders (supplier_id, material, quantity, price_per_unit, total_cost, status, delivery_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
                 (1, "Оцинкований", 50, 70.0, 3500.0, "planned", "2025-11-10"))
    conn.commit()
    conn.close()

@st.cache_data(ttl=300)
def get_suppliers():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM suppliers", conn)
    conn.close()
    return df

@st.cache_data(ttl=300)
def get_purchase_orders():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT po.*, s.name as supplier_name FROM purchase_orders po JOIN suppliers s ON po.supplier_id = s.id", conn)
    conn.close()
    return df
