import sqlite3
from datetime import datetime

conn = sqlite3.connect('suppliers.db')
c = conn.cursor()

# Створення таблиць
c.execute('''CREATE TABLE IF NOT EXISTS suppliers
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              inn TEXT,
              address TEXT,
              phone TEXT,
              email TEXT,
              contact_person TEXT,
              rating REAL DEFAULT 5.0,
              created_date TEXT NOT NULL)''')

c.execute('''CREATE TABLE IF NOT EXISTS purchase_orders
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              supplier_id INTEGER NOT NULL,
              material TEXT NOT NULL,
              quantity INTEGER NOT NULL,
              price_per_unit REAL NOT NULL,
              total_cost REAL NOT NULL,
              status TEXT DEFAULT 'planned',
              order_date TEXT NOT NULL,
              delivery_date TEXT)''')

# Додавання постачальників
c.execute("INSERT OR REPLACE INTO suppliers VALUES (1, 'ТОВ МеталПром', '1234567890', 'Київ, вул. Металургів 10', '+380671234567', 'metalprom@ukr.net', 'Іван Металенко', 4.8, '2025-10-01')")
c.execute("INSERT OR REPLACE INTO suppliers VALUES (2, 'ФОП СтальБуд', '0987654321', 'Харків, вул. Сталінградська 5', '+380672345678', 'stalbud@gmail.com', 'Олена Сталь', 4.2, '2025-10-02')")
c.execute("INSERT OR REPLACE INTO suppliers VALUES (3, 'ТОВ ПВХПро', '1122334455', 'Львів, вул. Пластикова 15', '+380673456789', 'pvhpro@ua.com', 'Петро ПВХ', 5.0, '2025-10-03')")

# Додавання замовлень
c.execute("INSERT OR REPLACE INTO purchase_orders VALUES (1, 1, 'Оцинкований', 100, 75.0, 7500.0, 'planned', '2025-10-15', '2025-10-20')")
c.execute("INSERT OR REPLACE INTO purchase_orders VALUES (2, 2, 'Чорний', 50, 55.0, 2750.0, 'ordered', '2025-10-18', '2025-10-25')")
c.execute("INSERT OR REPLACE INTO purchase_orders VALUES (3, 3, 'ПВХ', 20, 110.0, 2200.0, 'received', '2025-10-20', '2025-10-22')")
c.execute("INSERT OR REPLACE INTO purchase_orders VALUES (4, 1, 'Мідний', 5, 700.0, 3500.0, 'cancelled', '2025-10-25', '2025-10-30')")
c.execute("INSERT OR REPLACE INTO purchase_orders VALUES (5, 2, 'Оцинкований', 80, 8.0, 640.0, 'planned', '2025-10-28', '2025-11-05')")

conn.commit()
conn.close()

print("suppliers.db створено з 3 постачальниками та 5 замовленнями.")
