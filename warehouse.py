import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

DB_PATH = "data/warehouse.db"

def init_warehouse():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_id TEXT,
        material TEXT,
        quantity INTEGER,
        price_per_unit REAL,
        total_cost REAL,
        arrival_date TEXT
    )""")
    # Додамо приклади
    conn.execute("INSERT OR IGNORE INTO inventory (batch_id, material, quantity, price_per_unit, total_cost, arrival_date) VALUES (?, ?, ?, ?, ?, ?)",
                 ("B001", "Оцинкований", 100, 75.0, 7500.0, "2025-10-01"))
    conn.execute("INSERT OR IGNORE INTO inventory (batch_id, material, quantity, price_per_unit, total_cost, arrival_date) VALUES (?, ?, ?, ?, ?, ?)",
                 ("B002", "Чорний", 60, 60.0, 3600.0, "2025-10-05"))
    conn.commit()
    conn.close()

@st.cache_data(ttl=300)
def get_inventory():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM inventory WHERE quantity > 0", conn)
    conn.close()
    return df
