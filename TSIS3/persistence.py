"""
TSIS 3 — persistence.py
Сохранение и загрузка таблицы лидеров и настроек в/из JSON файлов.
"""
import json
import os

LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "sound": True,
    "car_color": "blue",
    "difficulty": "normal",
}


def load_leaderboard():
    """Загружаем топ-результаты из leaderboard.json."""
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    try:
        with open(LEADERBOARD_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_leaderboard(entries):
    """Сохраняем результаты (отсортированные, топ-10) в leaderboard.json."""
    entries = sorted(entries, key=lambda e: e.get("score", 0), reverse=True)[:10]
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(entries, f, indent=2)


def add_leaderboard_entry(name, score, distance):
    """Добавляем новую запись и сохраняем."""
    entries = load_leaderboard()
    entries.append({"name": name, "score": score, "distance": distance})
    save_leaderboard(entries)


def load_settings():
    """Загружаем настройки из settings.json, подставляя дефолты для отсутствующих."""
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
        return dict(DEFAULT_SETTINGS)
    try:
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
        # дополняем недостающие ключи дефолтами
        for k, v in DEFAULT_SETTINGS.items():
            if k not in settings:
                settings[k] = v
        return settings
    except (json.JSONDecodeError, IOError):
        return dict(DEFAULT_SETTINGS)


def save_settings(settings):
    """Сохраняем настройки в settings.json."""
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)
