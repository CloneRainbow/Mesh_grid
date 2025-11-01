# logistics.py — ВИПРАВЛЕНИЙ
from dataclasses import dataclass

@dataclass
class LogisticsResult:
    trips: int
    fuel_cost: float
    packaging_cost: float
    driver_cost: float
    total_cost: float
    co2: float
    route_efficiency: float  # % використання вантажопідйомності

def calculate_optimized_logistics(distance_km, weight_kg, roll_count):
    from config.settings import TRUCK_CAPACITY, FUEL_CONSUMPTION, CO2_PER_LITER
    import math

    # Розрахунок
    trips = math.ceil(weight_kg / TRUCK_CAPACITY)
    fuel_liters = distance_km * FUEL_CONSUMPTION * trips
    fuel_cost = fuel_liters * 55.0  # ₴/л
    packaging_cost = roll_count * 5.0
    driver_cost = trips * 500.0
    total_cost = fuel_cost + packaging_cost + driver_cost
    co2 = fuel_liters * CO2_PER_LITER

    # Ефективність (скільки % вантажопідйомності використано)
    used_capacity = weight_kg / (TRUCK_CAPACITY * trips)
    route_efficiency = round(used_capacity * 100, 1)

    # ПОВЕРТАЄМО ВСІ АТРИБУТИ
    return LogisticsResult(
        trips=trips,
        fuel_cost=fuel_cost,
        packaging_cost=packaging_cost,
        driver_cost=driver_cost,
        total_cost=total_cost,
        co2=co2,
        route_efficiency=route_efficiency
    )
