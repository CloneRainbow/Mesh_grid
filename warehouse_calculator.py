# warehouse_calculator.py — ВИПРАВЛЕНИЙ
import streamlit as st
import pandas as pd  # ДОДАНО
from typing import Dict, Tuple, Optional
import math

# Константи з формули
BASE_WEIGHT_FACTOR = 13.4
BASE_LENGTH_FACTOR = 2173
COPPER_DENSITY_RATIO = 1.141
PVC_COEFFICIENTS = {
    1.2: 0.3896,
    1.5: 0.4711,
    1.8: 0.5402,
    2.0: 0.5794
}

MATERIAL_PRICES: Dict[str, float] = {
    "Оцинкований": 75.0,
    "Чорний": 55.0,
    "Мідний": 700.0,
    "ПВХ": 110.0
}

@st.cache_data(ttl=300)
def calculate_warehouse_cost(
    cell_size_mm: float,
    wire_thickness_mm: float,
    roll_length_m: float,
    roll_height_m: float,
    material: str,
    custom_price_per_kg: Optional[float] = None
) -> Tuple[Dict[str, float], pd.DataFrame]:
    """
    Розрахунок витрат на виготовлення сітки-рябиці.
    """
    if cell_size_mm <= 0 or wire_thickness_mm <= 0:
        st.error("Розмір вічка та товщина дроту мають бути > 0")
        return {}, pd.DataFrame()

    area = roll_length_m * roll_height_m

    # Коефіцієнт для матеріалу
    if material == "Мідний":
        material_coeff = COPPER_DENSITY_RATIO
    elif material == "ПВХ":
        material_coeff = PVC_COEFFICIENTS.get(wire_thickness_mm, 0.5)
    else:
        material_coeff = 1.0

    # Вага 1 м²
    weight_per_m2 = BASE_WEIGHT_FACTOR * (wire_thickness_mm ** 2) / cell_size_mm * material_coeff
    weight_per_m2 = round(weight_per_m2, 4)

    # Довжина на 1 м²
    length_per_m2 = BASE_LENGTH_FACTOR / cell_size_mm
    length_per_m2 = round(length_per_m2, 1)

    # Загальна вага
    total_weight = round(weight_per_m2 * area, 2)

    # Ціна за кг
    price_per_kg = custom_price_per_kg or MATERIAL_PRICES.get(material, 75.0)

    # Собівартість
    total_cost = round(total_weight * price_per_kg, 2)

    results = {
        "вага_1м2": weight_per_m2,
        "довжина_1м2": length_per_m2,
        "площа": area,
        "загальна_вага": total_weight,
        "ціна_за_кг": price_per_kg,
        "собівартість": total_cost
    }

    details_df = pd.DataFrame({
        "Параметр": [
            "Розмір вічка (мм)", "Товщина дроту (мм)", "Довжина рулону (м)",
            "Висота рулону (м)", "Площа (м²)", "Вага 1 м² (кг)",
            "Довжина дроту 1 м² (м)", "Загальна вага (кг)", "Ціна за кг (грн)", "Собівартість (грн)"
        ],
        "Значення": [
            cell_size_mm, wire_thickness_mm, roll_length_m, roll_height_m,
            area, weight_per_m2, length_per_m2, total_weight, price_per_kg, total_cost
        ]
    })

    return results, details_df
