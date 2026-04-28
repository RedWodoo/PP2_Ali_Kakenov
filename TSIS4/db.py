"""
TSIS 4 — db.py
Работа с PostgreSQL для змейки.
Таблицы: players, game_sessions.
Подключение через psycopg2 + configparser.
"""
import psycopg2
from contextlib import contextmanager
from configparser import ConfigParser


def load_config(filename='database.ini', section='postgresql'):
    """Загружаем параметры подключения к БД из .ini файла."""
    parser = ConfigParser()
    parser.read(filename, encoding='utf-8')
    config = {}
    if parser.has_section(section):
        for param in parser.items(section):
            config[param[0]] = param[1]
    else:
        raise Exception(f'Секция {section} не найдена в {filename}')
    return config


@contextmanager
def get_connection():
    """Контекстный менеджер для подключения к БД с авто-коммитом."""
    conn = None
    try:
        params = load_config()
        conn = psycopg2.connect(**params)
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Ошибка базы данных: {e}")
        raise
    finally:
        if conn:
            conn.close()


def setup_database():
    """Создаём таблицы players и game_sessions, если их ещё нет."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS players (
                        id       SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL
                    )
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS game_sessions (
                        id            SERIAL PRIMARY KEY,
                        player_id     INTEGER REFERENCES players(id),
                        score         INTEGER NOT NULL,
                        level_reached INTEGER NOT NULL,
                        played_at     TIMESTAMP DEFAULT NOW()
                    )
                """)
        print("[DB] Таблицы готовы.")
    except Exception as e:
        print(f"[DB] Ошибка инициализации (продолжаем без БД): {e}")


def get_or_create_player(username):
    """Получаем ID игрока по имени, создаём если нет."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM players WHERE username = %s", (username,))
                row = cur.fetchone()
                if row:
                    return row[0]
                cur.execute("INSERT INTO players(username) VALUES(%s) RETURNING id", (username,))
                return cur.fetchone()[0]
    except Exception:
        return None


def save_result(username, score, level):
    """Сохраняем результат игровой сессии в базу."""
    try:
        pid = get_or_create_player(username)
        if pid is None:
            return
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO game_sessions(player_id, score, level_reached)
                    VALUES(%s, %s, %s)
                """, (pid, score, level))
        print(f"[DB] Результат сохранён для {username}.")
    except Exception as e:
        print(f"[DB] Ошибка сохранения: {e}")


def get_top10():
    """Получаем топ-10 результатов за всё время."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT p.username, gs.score, gs.level_reached, gs.played_at
                    FROM game_sessions gs
                    JOIN players p ON gs.player_id = p.id
                    ORDER BY gs.score DESC
                    LIMIT 10
                """)
                return cur.fetchall()
    except Exception:
        return []


def get_personal_best(username):
    """Получаем личный рекорд игрока."""
    try:
        pid = get_or_create_player(username)
        if pid is None:
            return 0
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT COALESCE(MAX(score), 0) FROM game_sessions WHERE player_id = %s
                """, (pid,))
                return cur.fetchone()[0]
    except Exception:
        return 0
