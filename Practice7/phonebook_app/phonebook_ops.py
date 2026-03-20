import psycopg2
import csv
from config import load_config


def insert_contact(name, phone):
    sql = "INSERT INTO phonebook(first_name, phone_number) VALUES(%s, %s)"
    config = load_config()
    with psycopg2.connect(**config) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (name, phone))
            conn.commit()


def upload_csv(file_path):
    config = load_config()
    with psycopg2.connect(**config) as conn:
        with conn.cursor() as cur:
            with open(file_path, 'r') as f:
                reader = csv.reader(f)
                next(reader)  
                for row in reader:
                    cur.execute("INSERT INTO phonebook(first_name, phone_number) VALUES(%s, %s) ON CONFLICT DO NOTHING", row)
            conn.commit()

def update_contact(target_name, new_name=None, new_phone=None):
    config = load_config()
    with psycopg2.connect(**config) as conn:
        with conn.cursor() as cur:
            if new_name:
                cur.execute("UPDATE phonebook SET first_name=%s WHERE first_name=%s", (new_name, target_name))
            if new_phone:
                cur.execute("UPDATE phonebook SET phone_number=%s WHERE first_name=%s", (new_phone, target_name))
            conn.commit()

def query_contacts(search_term):
    sql = "SELECT * FROM phonebook WHERE first_name ILIKE %s OR phone_number ILIKE %s"
    config = load_config()
    with psycopg2.connect(**config) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (f'%{search_term}%', f'%{search_term}%'))
            return cur.fetchall()

def delete_contact(identifier):
    sql = "DELETE FROM phonebook WHERE first_name = %s OR phone_number = %s"
    config = load_config()
    with psycopg2.connect(**config) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (identifier, identifier))
            conn.commit()