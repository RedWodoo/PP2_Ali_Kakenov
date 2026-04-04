import csv
import psycopg2
from connect import get_connection

def setup_database():
    table_sql = """
    CREATE TABLE IF NOT EXISTS phonebook (
        contact_id SERIAL PRIMARY KEY,
        first_name VARCHAR(255) NOT NULL,
        phone_number VARCHAR(20) NOT NULL UNIQUE
    )
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(table_sql)

                with open('functions.sql', 'r', encoding='utf-8') as f:
                    cur.execute(f.read())
                with open('procedures.sql', 'r', encoding='utf-8') as f:
                    cur.execute(f.read())
    except FileNotFoundError as e:
        print(f"--- [ВНИМАНИЕ] Не найден файл SQL: {e.filename}. Убедитесь, что functions.sql и procedures.sql в папке.")
    except Exception as e:
        print(f"--- [ERROR] Ошибка инициализации: {e}")

def db_search_contacts(pattern):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM search_contacts(%s)", (pattern,))
            return cur.fetchall()

def db_upsert_contact(name, phone):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL upsert_contact(%s, %s)", (name, phone))

def db_insert_many(names, phones):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL insert_many_contacts(%s::TEXT[], %s::TEXT[], NULL, NULL)", (names, phones))
            return cur.fetchone()

def db_get_paginated(limit, offset):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (limit, offset))
            return cur.fetchall()

def db_delete_contact(identifier):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL delete_contact(%s)", (identifier,))

def main():
    setup_database()
    while True:
        print("\n--- PHONEBOOK (Practice 8 - PL/pgSQL) ---")
        print("1. Upsert контакт (Добавить/Обновить)")
        print("2. Массовая вставка (Тест валидации)")
        print("3. Поиск (Функция)")
        print("4. Вывод с пагинацией (LIMIT/OFFSET)")
        print("5. Удалить")
        print("0. Выход")
        choice = input("Выберите: ").strip()
        
        if choice == '1':
            name = input("Имя: ")
            phone = input("Телефон: ")
            db_upsert_contact(name, phone)
            print("--- [OK] Процедура upsert_contact выполнена.")
            
        elif choice == '2':
            names = []
            phones = []
            try:
                with open('contacts.csv', 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    next(reader)
                    for row in reader:
                        if len(row) == 2:
                            names.append(row[0])
                            phones.append(row[1])
                
                print("Загрузка данных из CSV через процедуру...")
                bn, bp = db_insert_many(names, phones)
                print("--- [OK] Обработка завершена.")
                if bn:
                    print("--- [WARNING] Эти контакты отклонены базой (неверный формат):")
                    for name, phone in zip(bn, bp):
                        print(f"    {name}: {phone}")
            except FileNotFoundError:
                print("--- [ERROR] Файл contacts.csv не найден!")
                    
        elif choice == '3':
            term = input("Паттерн для поиска: ")
            res = db_search_contacts(term)
            if res:
                for r in res: print(f"ID: {r[0]} | {r[1]} | {r[2]}")
            else:
                print("Ничего не найдено.")
                
        elif choice == '4':
            try:
                lim = int(input("Лимит (сколько записей показать): "))
                off = int(input("Смещение (сколько записей пропустить): "))
                res = db_get_paginated(lim, off)
                for r in res: print(f"ID: {r[0]} | {r[1]} | {r[2]}")
            except ValueError:
                print("--- [ERROR] Введите числа!")
                
        elif choice == '5':
            db_delete_contact(input("Имя или телефон для удаления: "))
            print("--- [OK] Процедура delete_contact выполнена.")
            
        elif choice == '0':
            print("Выход...")
            break

if __name__ == "__main__":
    main()