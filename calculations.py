from typing import Dict

# --- Константи ---
BASE_FORMULA_FACTOR = 13.4
LENGTH_PER_M2_FACTOR = 2173  # метрів дроту на 1 м² при a = 1 мм

# Ціни за 1 кг (грн)
PRICES_PER_KG: Dict[str, float] = {
    "Оцинкований": 75.0,
    "Чорний": 55.0,
    "Мідний": 700.0,
    "ПВХ": 110.0
}

# Коефіцієнти для ПВХ (відхилення від бази) — з таблиці
PVC_COEFFICIENTS: Dict[float, float] = {
    1.2: 0.3896,  # 0.77 / (13.4 * 1.2² / 25) ≈ 0.3896
    1.5: 0.4711,  # 1.21 / (13.4 * 1.5² / 25)
    1.8: 0.5402,
    2.0: 0.5794
}

# Коефіцієнт для міді (густина міді / густина сталі ≈ 8.96 / 7.85)
COPPER_DENSITY_RATIO = 1.141


def calculate_weight(a: int, d: float, material: str = "Оцинкований") -> float:
    """
    Розрахунок ваги 1 м² сітки (кг).

    Формула: 13.4 × d² / a
    - a: розмір вічка (мм)
    - d: товщина дроту (мм)
    - material: матеріал (коригує вагу)

    Повертає: вагу 1 м² (кг), округлену до 2 знаків.
    """
    if a <= 0:
        raise ValueError("Розмір вічка (a) має бути > 0")
    if d <= 0:
        raise ValueError("Товщина дроту (d) має бути > 0")

    base_weight = BASE_FORMULA_FACTOR * (d ** 2) / a

    if material == "Мідний":
        return round(base_weight * COPPER_DENSITY_RATIO, 2)
    elif material == "ПВХ":
        coeff = PVC_COEFFICIENTS.get(d)
        if coeff is None:
            # Інтерполяція для нестандартної товщини
            keys = sorted(PVC_COEFFICIENTS.keys())
            if d < keys[0]:
                coeff = PVC_COEFFICIENTS[keys[0]]
            elif d > keys[-1]:
                coeff = PVC_COEFFICIENTS[keys[-1]]
            else:
                for i in range(len(keys) - 1):
                    if keys[i] <= d <= keys[i + 1]:
                        # Лінійна інтерполяція
                        x1, y1 = keys[i], PVC_COEFFICIENTS[keys[i]]
                        x2, y2 = keys[i + 1], PVC_COEFFICIENTS[keys[i + 1]]
                        coeff = y1 + (y2 - y1) * (d - x1) / (x2 - x1)
                        break
        return round(base_weight * coeff, 2)
    else:
        return round(base_weight, 2)


def calculate_length(a: int, area: float) -> int:
    """
    Розрахунок загальної довжини дроту (м).

    Формула: 2173 / a × площа (м²)
    """
    if a <= 0 or area < 0:
        raise ValueError("Невірні вхідні дані для довжини")
    length = (LENGTH_PER_M2_FACTOR / a) * area
    return round(length)  # ціле число метрів


def calculate_cost(weight: float, material: str) -> float:
    """
    Розрахунок собівартості (грн).

    Формула: вага × ціна за кг
    """
    if weight < 0:
        raise ValueError("Вага не може бути від'ємною")
    price = PRICES_PER_KG.get(material, PRICES_PER_KG["Оцинкований"])
    return round(weight * price, 2)
