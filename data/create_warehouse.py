import sqlite3

conn = sqlite3.connect('warehouse.db')
c = conn.cursor()

# Створення таблиці
c.execute('''CREATE TABLE IF NOT EXISTS inventory
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              batch_id TEXT UNIQUE NOT NULL,
              material TEXT NOT NULL,
              quantity INTEGER NOT NULL,
              price_per_unit REAL NOT NULL,
              total_cost REAL NOT NULL,
              arrival_date TEXT NOT NULL)''')

# Додавання зразкових даних
c.execute("INSERT OR REPLACE INTO inventory VALUES (1, 'B001', 'Оцинкований', 100, 75.0, 7500.0, '2025-10-01')")
c.execute("INSERT OR REPLACE INTO inventory VALUES (2, 'B002', 'Чорний', 60, 10.0, 600.0, '2025-10-05')")
c.execute("INSERT OR REPLACE INTO inventory VALUES (3, 'B003', 'ПВХ', 20, 110.0, 2200.0, '2025-10-07')")
c.execute("INSERT OR REPLACE INTO inventory VALUES (4, 'B004', 'Мідний', 5, 700.0, 3500.0, '2025-10-10')")
c.execute("INSERT OR REPLACE INTO inventory VALUES (5, 'B005', 'Оцинкований', 80, 8.0, 640.0, '2025-10-12')")

conn.commit()
conn.close()

print("warehouse.db створено з 5 записами.")
