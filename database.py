# database.py
import sqlite3
import pandas as pd
import os

DB_CLI = "data/clients.db"
DB_SUP = "data/suppliers.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_CLI)
    conn.execute("""CREATE TABLE IF NOT EXISTS clients
                    (id INTEGER PRIMARY KEY, name TEXT, email TEXT,
                     phone TEXT, balance REAL, logo TEXT)""")
    conn.commit()
    conn.close()

    conn = sqlite3.connect(DB_SUP)
    conn.execute("""CREATE TABLE IF NOT EXISTS suppliers
                    (id INTEGER PRIMARY KEY, name TEXT, email TEXT,
                     phone TEXT, balance REAL, logo TEXT)""")
    conn.commit()
    conn.close()

def add_client(name, email, phone, balance, logo_b64):
    conn = sqlite3.connect(DB_CLI)
    cur = conn.cursor()
    cur.execute("INSERT INTO clients (name,email,phone,balance,logo) VALUES (?,?,?,?,?)",
                (name, email, phone, balance, logo_b64))
    conn.commit()
    conn.close()

def add_supplier(name, email, phone, balance, logo_b64):
    conn = sqlite3.connect(DB_SUP)
    cur = conn.cursor()
    cur.execute("INSERT INTO suppliers (name,email,phone,balance,logo) VALUES (?,?,?,?,?)",
                (name, email, phone, balance, logo_b64))
    conn.commit()
    conn.close()

def get_clients():
    conn = sqlite3.connect(DB_CLI)
    df = pd.read_sql_query("SELECT id, name, email, phone, balance FROM clients", conn)
    conn.close()
    return df

def get_suppliers():
    conn = sqlite3.connect(DB_SUP)
    df = pd.read_sql_query("SELECT id, name, email, phone, balance FROM suppliers", conn)
    conn.close()
    return df
