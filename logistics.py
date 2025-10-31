def calculate_logistics(distance_km: int, tariff: float = 1.0, fixed: float = 100.0) -> float:
    return distance_km * tariff + fixed
