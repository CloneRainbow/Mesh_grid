# database.py
import sqlite3
import pandas as pd
import os
from typing import Dict, Any

# --- Шляхи до баз ---
DB_DIR = "data"
DB_CLI = os.path.join(DB_DIR, "clients.db")
DB_SUP = os.path.join(DB_DIR, "suppliers.db")
DB_HIST = os.path.join(DB_DIR, "history.db")

# --- Ініціалізація всіх баз ---
def init_db() -> None:
    """Створює папку data/ та ініціалізує всі SQLite-бази."""
    os.makedirs(DB_DIR, exist_ok=True)

    # Клієнти
    _create_table(
        DB_CLI,
        "clients",
        """
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        balance REAL DEFAULT 0.0,
        logo TEXT
        """
    )

    # Постачальники
    _create_table(
        DB_SUP,
        "suppliers",
        """
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        balance REAL DEFAULT 0.0,
        logo TEXT
        """
    )

    # Історія розрахунків
    _create_table(
        DB_HIST,
        "history",
        """
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        material TEXT NOT NULL,
        cell_size REAL NOT NULL,
        wire_thickness REAL NOT NULL,
        roll_length REAL NOT NULL,
        roll_height REAL NOT NULL,
        price_per_kg REAL NOT NULL,
        margin_pct REAL NOT NULL,
        purchase_cost REAL NOT NULL,
        sale_price REAL NOT NULL,
        profit REAL NOT NULL,
        area REAL NOT NULL,
        total_weight REAL NOT NULL
        """
    )

# --- Універсальна функція створення таблиці ---
def _create_table(db_path: str, table_name: str, schema: str) -> None:
    """Створює таблицю, якщо її немає."""
    conn = sqlite3.connect(db_path)
    conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})")
    conn.commit()
    conn.close()

# ===================================================================
# КЛІЄНТИ
# ===================================================================
def add_client(name: str, email: str, phone: str, balance: float, logo_b64: str | None) -> None:
    """Додає клієнта в базу."""
    conn = sqlite3.connect(DB_CLI)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO clients (name, email, phone, balance, logo) VALUES (?, ?, ?, ?, ?)",
        (name, email, phone, balance, logo_b64)
    )
    conn.commit()
    conn.close()

def get_clients() -> pd.DataFrame:
    """Повертає всіх клієнтів."""
    conn = sqlite3.connect(DB_CLI)
    df = pd.read_sql_query("SELECT id, name, email, phone, balance FROM clients ORDER BY id DESC", conn)
    conn.close()
    return df

# ===================================================================
# ПОСТАЧАЛЬНИКИ
# ===================================================================
def add_supplier(name: str, email: str, phone: str, balance: float, logo_b64: str | None) -> None:
    """Додає постачальника."""
    conn = sqlite3.connect(DB_SUP)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO suppliers (name, email, phone, balance, logo) VALUES (?, ?, ?, ?, ?)",
        (name, email, phone, balance, logo_b64)
    )
    conn.commit()
    conn.close()

def get_suppliers() -> pd.DataFrame:
    """Повертає всіх постачальників."""
    conn = sqlite3.connect(DB_SUP)
    df = pd.read_sql_query("SELECT id, name, email, phone, balance FROM suppliers ORDER BY id DESC", conn)
    conn.close()
    return df

# ===================================================================
# ІСТОРІЯ РОЗРАХУНКІВ
# ===================================================================
def add_calculation(calc_dict: Dict[str, Any]) -> None:
    """Зберігає результат розрахунку в історію."""
    conn = sqlite3.connect(DB_HIST)
    df = pd.DataFrame([calc_dict])
    df.to_sql("history", conn, if_exists="append", index=False)
    conn.close()

@st.cache_data(ttl=300)  # Кеш на 5 хвилин
def get_history(limit: int = 100) -> pd.DataFrame:
    """Повертає останні N записів історії."""
    conn = sqlite3.connect(DB_HIST)
    query = f"""
        SELECT 
            timestamp, material, cell_size, wire_thickness,
            roll_length, roll_height, price_per_kg, margin_pct,
            purchase_cost, sale_price, profit, area, total_weight
        FROM history 
        ORDER BY id DESC 
        LIMIT {limit}
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def clear_history() -> None:
    """Очищає всю історію."""
    conn = sqlite3.connect(DB_HIST)
    conn.execute("DELETE FROM history")
    conn.commit()
    conn.close()
    # Скидаємо кеш
    get_history.clear()
