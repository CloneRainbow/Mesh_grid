import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

DB_PATH = "data/finance.db"

def init_finance():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS cash_flow (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT, category TEXT, amount REAL, date TEXT
    )""")
    # Приклади
    conn.execute("INSERT OR IGNORE INTO cash_flow (type, category, amount, date) VALUES (?, ?, ?, ?)",
                 ("income", "Продажі", 45000.0, "2025-10-15"))
    conn.execute("INSERT OR IGNORE INTO cash_flow (type, category, amount, date) VALUES (?, ?, ?, ?)",
                 ("expense", "Закупівлі", 30000.0, "2025-10-16"))
    conn.commit()
    conn.close()

@st.cache_data(ttl=300)
def get_cash_flow_df():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM cash_flow ORDER BY date DESC", conn)
    conn.close()
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
    return df
