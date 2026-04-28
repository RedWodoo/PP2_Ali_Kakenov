import psycopg2

conn = psycopg2.connect(host='localhost', user='postgres', password='1234', port=5432, dbname='postgres')
conn.autocommit = True
cur = conn.cursor()
cur.execute("SELECT 1 FROM pg_database WHERE datname='snake_db'")
exists = cur.fetchone()
if exists:
    print("snake_db already exists")
else:
    cur.execute("CREATE DATABASE snake_db")
    print("snake_db created")
conn.close()
