import os

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

MIN_STOCK = {
    "Оцинкований": 50,
    "Чорний": 30,
    "ПВХ": 20
}

TRUCK_CAPACITY = 20000  # кг
FUEL_CONSUMPTION = 0.35  # л/км
CO2_PER_LITER = 2.3
