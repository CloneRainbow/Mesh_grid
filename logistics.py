from dataclasses import dataclass

@dataclass
class LogisticsResult:
    trips: int
    total_cost: float
    co2: float

def calculate_optimized_logistics(distance_km, weight_kg, roll_count):
    from config.settings import TRUCK_CAPACITY, FUEL_CONSUMPTION, CO2_PER_LITER
    import math
    trips = math.ceil(weight_kg / TRUCK_CAPACITY)
    fuel_liters = distance_km * FUEL_CONSUMPTION * trips
    fuel_cost = fuel_liters * 55.0
    packaging = roll_count * 5.0
    driver = trips * 500.0
    total = fuel_cost + packaging + driver
    co2 = fuel_liters * CO2_PER_LITER
    return LogisticsResult(trips, total, co2)
