"""
TSIS 1 — Расширенная телефонная книга
Расширение Practice 7-8:
  - Расширенная модель контакта (email, дата рождения, группы, несколько телефонов)
  - Продвинутый поиск и фильтрация (по группе, email, сортировка, постраничный просмотр)
  - Импорт/экспорт (JSON + расширенный CSV)
  - Новые хранимые процедуры (add_phone, move_to_group, расширенный search_contacts)
"""
import csv
import json
import os
from datetime import datetime
from connect import get_connection


# ============================================================
# ИНИЦИАЛИЗАЦИЯ БАЗЫ
# ============================================================
def setup_database():
    """Создаём таблицы и загружаем SQL-процедуры/функции."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # базовая таблица если ещё нет
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS phonebook (
                        contact_id SERIAL PRIMARY KEY,
                        first_name VARCHAR(255) NOT NULL,
                        phone_number VARCHAR(20) NOT NULL UNIQUE
                    )
                """)
                # расширения схемы (группы, телефоны, новые столбцы)
                for sql_file in ['schema.sql', 'functions.sql', 'procedures.sql']:
                    if os.path.exists(sql_file):
                        with open(sql_file, 'r', encoding='utf-8') as f:
                            cur.execute(f.read())
        print("--- [OK] Database initialized.")
    except Exception as e:
        print(f"--- [ERROR] Setup failed: {e}")


# ============================================================
# CRUD-ОПЕРАЦИИ
# ============================================================
def upsert_contact(name, phone):
    """Добавляем или обновляем контакт через процедуру upsert."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL upsert_contact(%s, %s)", (name, phone))
    print(f"--- [OK] Upsert: {name}")


def update_extra_fields(name, email=None, birthday=None):
    """Обновляем дополнительные поля контакта (email, дата рождения)."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            if email:
                cur.execute("UPDATE phonebook SET email = %s WHERE first_name = %s", (email, name))
            if birthday:
                cur.execute("UPDATE phonebook SET birthday = %s WHERE first_name = %s", (birthday, name))
    print(f"--- [OK] Updated extra fields for {name}")


def delete_contact(identifier):
    """Удаляем контакт по имени или телефону через хранимую процедуру."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL delete_contact(%s)", (identifier,))
    print(f"--- [OK] Deleted: {identifier}")


def add_phone(contact_name, phone, phone_type):
    """Добавляем дополнительный номер телефона контакту."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL add_phone(%s, %s, %s)", (contact_name, phone, phone_type))
    print(f"--- [OK] Added {phone_type} phone {phone} to {contact_name}")


def move_to_group(contact_name, group_name):
    """Перемещаем контакт в группу (создаёт группу если не существует)."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL move_to_group(%s, %s)", (contact_name, group_name))
    print(f"--- [OK] Moved {contact_name} to group '{group_name}'")


# ============================================================
# ПОИСК И ФИЛЬТРАЦИЯ
# ============================================================
def search_contacts(pattern):
    """Поиск по имени, телефону, email и дополнительным номерам."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM search_contacts(%s)", (pattern,))
            return cur.fetchall()


def filter_by_group(group_name):
    """Показать контакты из определённой группы."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.contact_id, p.first_name, p.phone_number, p.email, p.birthday, g.name
                FROM phonebook p
                LEFT JOIN groups g ON p.group_id = g.id
                WHERE g.name ILIKE %s
                ORDER BY p.first_name
            """, (group_name,))
            return cur.fetchall()


def search_by_email(pattern):
    """Ищем контакты по частичному совпадению email."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.contact_id, p.first_name, p.phone_number, p.email, p.birthday, g.name
                FROM phonebook p
                LEFT JOIN groups g ON p.group_id = g.id
                WHERE p.email ILIKE %s
                ORDER BY p.first_name
            """, (f'%{pattern}%',))
            return cur.fetchall()


def get_sorted(sort_by='name'):
    """Получаем все контакты с сортировкой по имени, дню рождения или дате добавления."""
    order_map = {
        'name': 'p.first_name',
        'birthday': 'p.birthday NULLS LAST',
        'date': 'p.contact_id',
    }
    order = order_map.get(sort_by, 'p.first_name')
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT p.contact_id, p.first_name, p.phone_number, p.email, p.birthday, g.name
                FROM phonebook p
                LEFT JOIN groups g ON p.group_id = g.id
                ORDER BY {order}
            """)
            return cur.fetchall()


def paginated_browse(page_size=5):
    """Постраничный просмотр контактов через функцию БД."""
    offset = 0
    while True:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (page_size, offset))
                rows = cur.fetchall()

        if not rows:
            print("--- No more records.")
            break

        print(f"\n--- Page (offset={offset}, limit={page_size}) ---")
        for r in rows:
            print(f"  ID:{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | Group:{r[5]}")

        cmd = input("[n]ext / [p]rev / [q]uit: ").strip().lower()
        if cmd == 'n':
            offset += page_size
        elif cmd == 'p':
            offset = max(0, offset - page_size)
        elif cmd == 'q':
            break


# ============================================================
# ИМПОРТ / ЭКСПОРТ
# ============================================================
def export_to_json(filename='contacts_export.json'):
    """Экспортируем все контакты (с телефонами и группой) в JSON."""
    data = []
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.contact_id, p.first_name, p.phone_number, p.email,
                       p.birthday, g.name as group_name
                FROM phonebook p
                LEFT JOIN groups g ON p.group_id = g.id
                ORDER BY p.contact_id
            """)
            contacts = cur.fetchall()

            for c in contacts:
                cur.execute("SELECT phone, type FROM phones WHERE contact_id = %s", (c[0],))
                extra_phones = [{"phone": ph[0], "type": ph[1]} for ph in cur.fetchall()]

                data.append({
                    "first_name": c[1],
                    "phone_number": c[2],
                    "email": c[3],
                    "birthday": str(c[4]) if c[4] else None,
                    "group": c[5],
                    "extra_phones": extra_phones,
                })

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"--- [OK] Exported {len(data)} contacts to {filename}")


def import_from_json(filename='contacts_export.json'):
    """Импортируем контакты из JSON. При дубликате спрашиваем: пропустить или перезаписать."""
    if not os.path.exists(filename):
        print(f"--- [ERROR] File {filename} not found!")
        return

    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    with get_connection() as conn:
        with conn.cursor() as cur:
            for item in data:
                name = item.get('first_name', '')
                phone = item.get('phone_number', '')

                # проверяем есть ли уже такой контакт
                cur.execute("SELECT contact_id FROM phonebook WHERE first_name = %s", (name,))
                existing = cur.fetchone()

                if existing:
                    choice = input(f"  '{name}' already exists. [s]kip / [o]verwrite? ").strip().lower()
                    if choice != 'o':
                        continue
                    # перезаписываем все поля
                    cur.execute("""
                        UPDATE phonebook SET phone_number=%s, email=%s, birthday=%s
                        WHERE first_name=%s
                    """, (phone, item.get('email'), item.get('birthday'), name))
                    cid = existing[0]
                else:
                    cur.execute("""
                        INSERT INTO phonebook(first_name, phone_number, email, birthday)
                        VALUES (%s, %s, %s, %s) RETURNING contact_id
                    """, (name, phone, item.get('email'), item.get('birthday')))
                    cid = cur.fetchone()[0]

                # устанавливаем группу
                group_name = item.get('group')
                if group_name:
                    cur.execute("INSERT INTO groups(name) VALUES(%s) ON CONFLICT DO NOTHING", (group_name,))
                    cur.execute("SELECT id FROM groups WHERE name=%s", (group_name,))
                    gid = cur.fetchone()[0]
                    cur.execute("UPDATE phonebook SET group_id=%s WHERE contact_id=%s", (gid, cid))

                # добавляем доп. телефоны
                for ph in item.get('extra_phones', []):
                    cur.execute("""
                        INSERT INTO phones(contact_id, phone, type) VALUES(%s, %s, %s)
                        ON CONFLICT DO NOTHING
                    """, (cid, ph['phone'], ph['type']))

    print(f"--- [OK] Import from {filename} complete.")


def import_from_csv(filepath='contacts.csv'):
    """Расширенный CSV-импорт с поддержкой новых полей: email, birthday, group, phone_type."""
    if not os.path.exists(filepath):
        print(f"--- [ERROR] File {filepath} not found!")
        return

    count = 0
    with get_connection() as conn:
        with conn.cursor() as cur:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    name = row.get('first_name', '').strip()
                    phone = row.get('phone_number', '').strip()
                    email = row.get('email', '').strip() or None
                    birthday = row.get('birthday', '').strip() or None
                    group = row.get('group', '').strip() or None
                    phone_type = row.get('phone_type', '').strip() or 'mobile'

                    if not name or not phone:
                        continue

                    # вставляем или обновляем контакт
                    cur.execute("""
                        INSERT INTO phonebook(first_name, phone_number, email, birthday)
                        VALUES(%s, %s, %s, %s)
                        ON CONFLICT (phone_number) DO UPDATE
                        SET email = EXCLUDED.email, birthday = EXCLUDED.birthday
                        RETURNING contact_id
                    """, (name, phone, email, birthday))
                    result = cur.fetchone()
                    if result:
                        cid = result[0]
                    else:
                        cur.execute("SELECT contact_id FROM phonebook WHERE first_name=%s", (name,))
                        cid = cur.fetchone()[0]

                    # устанавливаем группу
                    if group:
                        cur.execute("INSERT INTO groups(name) VALUES(%s) ON CONFLICT DO NOTHING", (group,))
                        cur.execute("SELECT id FROM groups WHERE name=%s", (group,))
                        gid = cur.fetchone()[0]
                        cur.execute("UPDATE phonebook SET group_id=%s WHERE contact_id=%s", (gid, cid))

                    # добавляем телефон в таблицу phones
                    cur.execute("""
                        INSERT INTO phones(contact_id, phone, type)
                        VALUES(%s, %s, %s)
                    """, (cid, phone, phone_type))

                    count += 1

    print(f"--- [OK] Imported {count} contacts from CSV.")


# ============================================================
# ВЫВОД КОНТАКТОВ
# ============================================================
def print_contacts(rows):
    """Красиво выводим список контактов."""
    if not rows:
        print("  (no results)")
        return
    for r in rows:
        bday = str(r[4]) if r[4] else '-'
        print(f"  ID:{r[0]} | {r[1]} | Phone:{r[2]} | Email:{r[3] or '-'} | "
              f"Birthday:{bday} | Group:{r[5] or '-'}")


# ============================================================
# ГЛАВНОЕ МЕНЮ
# ============================================================
def main():
    setup_database()

    while True:
        print("\n" + "=" * 50)
        print("  PHONEBOOK — TSIS 1 (Extended)")
        print("=" * 50)
        print("  1. Add / Update contact (upsert)")
        print("  2. Add phone number to contact")
        print("  3. Move contact to group")
        print("  4. Search (name/phone/email/all phones)")
        print("  5. Filter by group")
        print("  6. Search by email")
        print("  7. Sort contacts (name/birthday/date)")
        print("  8. Browse (paginated)")
        print("  9. Import from CSV")
        print(" 10. Import from JSON")
        print(" 11. Export to JSON")
        print(" 12. Delete contact")
        print("  0. Exit")
        print("-" * 50)

        choice = input("Select: ").strip()

        if choice == '1':
            name = input("Name: ").strip()
            phone = input("Phone: ").strip()
            upsert_contact(name, phone)
            email = input("Email (or Enter to skip): ").strip()
            bday = input("Birthday YYYY-MM-DD (or Enter to skip): ").strip()
            if email or bday:
                update_extra_fields(name, email or None, bday or None)
            group = input("Group (Family/Work/Friend/Other or Enter to skip): ").strip()
            if group:
                move_to_group(name, group)

        elif choice == '2':
            name = input("Contact name: ").strip()
            phone = input("Phone number: ").strip()
            ptype = input("Type (home/work/mobile): ").strip()
            add_phone(name, phone, ptype)

        elif choice == '3':
            name = input("Contact name: ").strip()
            group = input("Group name: ").strip()
            move_to_group(name, group)

        elif choice == '4':
            pattern = input("Search query: ").strip()
            results = search_contacts(pattern)
            print_contacts(results)

        elif choice == '5':
            group = input("Group name: ").strip()
            results = filter_by_group(group)
            print_contacts(results)

        elif choice == '6':
            pattern = input("Email pattern: ").strip()
            results = search_by_email(pattern)
            print_contacts(results)

        elif choice == '7':
            sort = input("Sort by (name/birthday/date): ").strip().lower()
            results = get_sorted(sort)
            print_contacts(results)

        elif choice == '8':
            try:
                size = int(input("Page size (default 5): ").strip() or "5")
            except ValueError:
                size = 5
            paginated_browse(size)

        elif choice == '9':
            filepath = input("CSV file (default contacts.csv): ").strip() or 'contacts.csv'
            import_from_csv(filepath)

        elif choice == '10':
            filepath = input("JSON file (default contacts_export.json): ").strip() or 'contacts_export.json'
            import_from_json(filepath)

        elif choice == '11':
            filepath = input("Output file (default contacts_export.json): ").strip() or 'contacts_export.json'
            export_to_json(filepath)

        elif choice == '12':
            ident = input("Name or phone to delete: ").strip()
            delete_contact(ident)

        elif choice == '0':
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()
