import sqlite3
from datetime import datetime

conn = sqlite3.connect('clients.db')
c = conn.cursor()

# Створення таблиць
c.execute('''CREATE TABLE IF NOT EXISTS clients
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              type TEXT,
              inn TEXT,
              address TEXT,
              phone TEXT,
              email TEXT,
              contact_person TEXT,
              balance REAL DEFAULT 0.0,
              created_date TEXT NOT NULL)''')

c.execute('''CREATE TABLE IF NOT EXISTS transactions
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              client_id INTEGER,
              type TEXT,
              amount REAL,
              date TEXT,
              comment TEXT)''')

# Додавання зразкових даних для clients
c.execute("INSERT OR REPLACE INTO clients VALUES (1, 'ТОВ СіткаПлюс', 'client', '1234567890', 'Київ, вул. Сіткова 1', '+380671234567', 'info@sitkaplus.ua', 'Іван Петренко', 5000.0, '2025-10-01')")
c.execute("INSERT OR REPLACE INTO clients VALUES (2, 'ФОП Іваненко', 'client', '0987654321', 'Львів, вул. Дротова 5', '+380672345678', 'ivanenko@gmail.com', 'Олена Іваненко', -2000.0, '2025-10-03')")
c.execute("INSERT OR REPLACE INTO clients VALUES (3, 'ТОВ МеталБуд', 'supplier', '1122334455', 'Харків, вул. Металургів 20', '+380673456789', 'metalbud@ukr.net', 'Олег Металенко', 0.0, '2025-10-05')")

# Додавання транзакцій
c.execute("INSERT OR REPLACE INTO transactions VALUES (1, 1, 'payment', 15000.0, '2025-10-10', 'Оплата за замовлення №123')")
c.execute("INSERT OR REPLACE INTO transactions VALUES (2, 1, 'sale', -5000.0, '2025-10-12', 'Продаж 50 рулонів')")
c.execute("INSERT OR REPLACE INTO transactions VALUES (3, 2, 'payment', 3000.0, '2025-10-15', 'Часткова оплата')")
c.execute("INSERT OR REPLACE INTO transactions VALUES (4, 3, 'purchase', -10000.0, '2025-10-20', 'Закупівля матеріалів')")
c.execute("INSERT OR REPLACE INTO transactions VALUES (5, 3, 'payment', 10000.0, '2025-10-22', 'Оплата постачальнику')")

conn.commit()
conn.close()

print("clients.db створено з 3 клієнтами та 5 транзакціями.")
