import sqlite3
from datetime import datetime

conn = sqlite3.connect('finance.db')
c = conn.cursor()

# Створення таблиці
c.execute('''CREATE TABLE IF NOT EXISTS cash_flow
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              type TEXT NOT NULL,
              category TEXT NOT NULL,
              amount REAL NOT NULL,
              date TEXT NOT NULL,
              comment TEXT)''')

# Додавання зразкових даних
c.execute("INSERT OR REPLACE INTO cash_flow VALUES (1, 'income', 'Продажі', 45000.0, '2025-10-15', 'Продаж 100 рулонів Оцинкований')")
c.execute("INSERT OR REPLACE INTO cash_flow VALUES (2, 'expense', 'Закупівлі', 30000.0, '2025-10-16', 'Закупівля у МеталПром')")
c.execute("INSERT OR REPLACE INTO cash_flow VALUES (3, 'income', 'Рахунки', 25000.0, '2025-10-20', 'Оплата від ТОВ СіткаПлюс')")
c.execute("INSERT OR REPLACE INTO cash_flow VALUES (4, 'expense', 'Логістика', 5000.0, '2025-10-21', 'Доставка по Україні')")
c.execute("INSERT OR REPLACE INTO cash_flow VALUES (5, 'income', 'Прибуток', 15000.0, '2025-10-25', 'Фінансовий результат місяця')")
c.execute("INSERT OR REPLACE INTO cash_flow VALUES (6, 'expense', 'Зарплати', 20000.0, '2025-10-30', 'Зарплата персоналу')")

conn.commit()
conn.close()

print("finance.db створено з 6 фінансовими операціями.")
