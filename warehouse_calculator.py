# warehouse_calculator.py
import streamlit as st
from typing import Dict, Tuple, Optional
import math

# Константи з формули (з вашого запиту + підтверджено пошуком)
BASE_WEIGHT_FACTOR = 13.4  # Константа для ваги 1 м² (кг)
BASE_LENGTH_FACTOR = 2173  # Константа для довжини дроту на 1 м² (м при a=1 мм)
COPPER_DENSITY_RATIO = 1.141  # Коефіцієнт для міді (густина 8960 / 7850)
PVC_COEFFICIENTS = {  # Коефіцієнти для ПВХ (відхилення від бази; з ваших таблиць)
    1.2: 0.3896,  # 0.77 / (13.4 * 1.2² / 25) ≈ 0.3896
    1.5: 0.4711,
    1.8: 0.5402,
    2.0: 0.5794
}

# Ціни за кг (грн; з вашого запиту)
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
    
    Формули:
    - Вага 1 м² = BASE_WEIGHT_FACTOR × (d² / a)
    - Довжина на 1 м² = BASE_LENGTH_FACTOR / a
    - Загальна вага = вага 1 м² × площа
    - Собівартість = загальна вага × ціна/кг
    
    Параметри:
    - cell_size_mm: розмір вічка (мм, a)
    - wire_thickness_mm: товщина дроту (мм, d)
    - roll_length_m: довжина рулону (м)
    - roll_height_m: висота рулону (м)
    - material: матеріал ("Оцинкований", "Чорний", "Мідний", "ПВХ")
    - custom_price_per_kg: кастомна ціна (грн/кг; якщо None — стандартна)
    
    Повертає: (результати dict, df з деталями)
    """
    if cell_size_mm <= 0 or wire_thickness_mm <= 0:
        st.error("Розмір вічка та товщина дроту мають бути > 0")
        return {}, pd.DataFrame()

    area = roll_length_m * roll_height_m  # Площа рулону (м²)

    # Коефіцієнт для матеріалу
    if material == "Мідний":
        material_coeff = COPPER_DENSITY_RATIO
    elif material == "ПВХ":
        material_coeff = PVC_COEFFICIENTS.get(wire_thickness_mm, 0.5)
    else:
        material_coeff = 1.0

    # Вага 1 м² (кг/м²)
    weight_per_m2 = BASE_WEIGHT_FACTOR * (wire_thickness_mm ** 2) / cell_size_mm * material_coeff
    weight_per_m2 = round(weight_per_m2, 4)

    # Довжина дроту на 1 м² (м/м²)
    length_per_m2 = BASE_LENGTH_FACTOR / cell_size_mm
    length_per_m2 = round(length_per_m2, 1)

    # Загальна вага (кг)
    total_weight = round(weight_per_m2 * area, 2)

    # Ціна за кг
    price_per_kg = custom_price_per_kg or MATERIAL_PRICES.get(material, 75.0)

    # Собівартість (грн)
    total_cost = round(total_weight * price_per_kg, 2)

    # Результати
    results = {
        "вага_1м2": weight_per_m2,
        "довжина_1м2": length_per_m2,
        "площа": area,
        "загальна_вага": total_weight,
        "ціна_за_кг": price_per_kg,
        "собівартість": total_cost
    }

    # Таблиця деталей
    details_df = pd.DataFrame({
        "Параметр": ["Розмір вічка (мм)", "Товщина дроту (мм)", "Довжина рулону (м)", "Висота рулону (м)", "Площа (м²)", "Вага 1 м² (кг)", "Довжина дроту 1 м² (м)", "Загальна вага (кг)", "Ціна за кг (грн)", "Собівартість (грн)"],
        "Значення": [cell_size_mm, wire_thickness_mm, roll_length_m, roll_height_m, area, weight_per_m2, length_per_m2, total_weight, price_per_kg, total_cost]
    })

    return results, details_df
