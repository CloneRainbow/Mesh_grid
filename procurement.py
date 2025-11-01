# procurement.py — ОПТИМІЗОВАНИЙ МОДУЛЬ ЗАКУПІВЕЛЬ
import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

# --- Шляхи до баз ---
WAREHOUSE_DB = "data/warehouse.db"
SUPPLIERS_DB = "data/suppliers.db"

# --- Налаштування мінімальних запасів ---
MIN_STOCK = {
    "Оцинкований": 50,
    "Чорний": 30,
    "ПВХ": 20,
    "Мідний": 10
}

# ===================================================================
# 1. ОТРИМАННЯ ДАНИХ З СКЛАДУ
# ===================================================================
@st.cache_data(ttl=300)
def get_current_stock():
    """Поверта
