# calculations.py
from functools import lru_cache

# --- Змінні коефіцієнти (налаштовуються в UI) ---
DEFAULT_WEIGHT_FACTOR = 13.4
DEFAULT_LENGTH_FACTOR = 2173
COPPER_RATIO = 1.141
PVC_COEFFS = {1.2: 0.3896, 1.5: 0.4711, 1.8: 0.5402, 2.0: 0.5794}

@lru_cache(maxsize=128)
def calculate_weight_1m2(
    cell_size: float, wire_thickness: float, material: str,
    weight_factor: float = DEFAULT_WEIGHT_FACTOR
) -> float:
    base = weight_factor * (wire_thickness ** 2) / cell_size
    if material == "Мідний":
        return round(base * COPPER_RATIO, 2)
    if material == "ПВХ":
        coef = PVC_COEFFS.get(wire_thickness, 0.5)
        return round(base * coef, 2)
    return round(base, 2)

@lru_cache(maxsize=128)
def calculate_total_length(
    cell_size: float, area: float,
    length_factor: float = DEFAULT_LENGTH_FACTOR
) -> int:
    return round(length_factor / cell_size * area)

def calculate_cost(weight: float, price_per_kg: float) -> float:
    return round(weight * price_per_kg, 2)
