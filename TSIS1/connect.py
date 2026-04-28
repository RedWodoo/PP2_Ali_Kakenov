import psycopg2
from contextlib import contextmanager
from config import load_config

@contextmanager
def get_connection():
    conn = None
    try:
        params = load_config()
        conn = psycopg2.connect(**params)
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Database Error: {e}")
        raise
    finally:
        if conn:
            conn.close()
