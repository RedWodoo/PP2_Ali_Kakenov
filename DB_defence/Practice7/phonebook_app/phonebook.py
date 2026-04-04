import csv
from connect import get_connection

def create_table():
    sql = """
    CREATE TABLE IF NOT EXISTS phonebook (
        contact_id SERIAL PRIMARY KEY,
        first_name VARCHAR(255) NOT NULL,
        phone_number VARCHAR(20) NOT NULL UNIQUE
    )
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)

def insert_from_console(name, phone):
    sql = "INSERT INTO phonebook(first_name, phone_number) VALUES(%s, %s)"
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (name, phone))
        print(f"--- [OK] {name} добавлен.")
    except Exception as e:
        print(f"--- [ERROR] {e}")

def insert_from_csv(file_path):
    sql = "INSERT INTO phonebook(first_name, phone_number) VALUES(%s, %s) ON CONFLICT DO NOTHING"
    count = 0
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    next(reader)
                    for row in reader:
                        if len(row) == 2:
                            cur.execute(sql, row)
                            count += 1
        print(f"--- [OK] Загружено строк: {count}")
    except Exception as e:
        print(f"--- [ERROR] {e}")

def update_contact(target_name, new_name=None, new_phone=None):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                if new_name:
                    cur.execute("UPDATE phonebook SET first_name=%s WHERE first_name=%s", (new_name, target_name))
                if new_phone:
                    cur.execute("UPDATE phonebook SET phone_number=%s WHERE first_name=%s", (new_phone, target_name))
        print("--- [OK] Обновлено.")
    except Exception as e:
        print(f"--- [ERROR] {e}")

def query_contacts(pattern):
    sql = "SELECT * FROM phonebook WHERE first_name ILIKE %s OR phone_number LIKE %s"
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (f'%{pattern}%', f'{pattern}%'))
                return cur.fetchall()
    except Exception as e:
        print(f"--- [ERROR] {e}")
        return []

def delete_contact(identifier):
    sql = "DELETE FROM phonebook WHERE first_name = %s OR phone_number = %s"
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (identifier, identifier))
        print("--- [OK] Удалено.")
    except Exception as e:
        print(f"--- [ERROR] {e}")

def main():
    print("Запуск программы...") 
    create_table()
    while True:
        print("\n--- PHONEBOOK ---")
        print("1. Add\n2. CSV\n3. Update\n4. Search\n5. Delete\n0. Exit")
        choice = input("Select: ").strip()
        
        if choice == '1':
            insert_from_console(input("Name: "), input("Phone: "))
        elif choice == '2':
            insert_from_csv('contacts.csv')
        elif choice == '3':
            t = input("Name: ")
            nn = input("New Name: ")
            np = input("New Phone: ")
            update_contact(t, nn or None, np or None)
        elif choice == '4':
            res = query_contacts(input("Query: "))
            for r in res: print(r)
        elif choice == '5':
            delete_contact(input("Name/Phone: "))
        elif choice == '0':
            break

if __name__ == "__main__":
    main()