import psycopg2
from config import load_config

def create_table():
    """ Создание таблицы phonebook """
    sql = """
    CREATE TABLE IF NOT EXISTS phonebook (
        contact_id SERIAL PRIMARY KEY,
        first_name VARCHAR(255) NOT NULL,
        phone_number VARCHAR(20) NOT NULL UNIQUE
    )
    """
    try:
        config = load_config()
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                conn.commit()
                print("Table 'phonebook' is ready.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)