import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

DB_PATH = "data/clients.db"

def init_clients():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, type TEXT, balance REAL DEFAULT 0.0
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER, type TEXT, amount REAL, date TEXT
    )""")
    # Приклади
    conn.execute("INSERT OR IGNORE INTO clients (name, type) VALUES (?, ?)", ("ТОВ СіткаПлюс", "client"))
    conn.execute("INSERT OR IGNORE INTO transactions (client_id, type, amount, date) VALUES (?, ?, ?, ?)",
                 (1, "payment", 15000.0, "2025-10-10"))
    conn.commit()
    conn.close()

@st.cache_data(ttl=300)
def get_clients():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM clients", conn)
    conn.close()
    return df
