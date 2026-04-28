# PP2 Coursework — Полный гайд для защиты

**Автор:** Али Какенов  
**Предмет:** PP2 (Python Programming 2)  
**Проекты:** Practice 11 (3 игры) + TSIS 1–4

---

## Оглавление

1. [Practice 11 — Racer (Гонки)](#1-practice-11--racer-гонки)
2. [Practice 11 — Snake (Змейка)](#2-practice-11--snake-змейка)
3. [Practice 11 — Paint (Рисовалка)](#3-practice-11--paint-рисовалка)
4. [TSIS 1 — PhoneBook (Телефонная книга)](#4-tsis-1--phonebook-телефонная-книга)
5. [TSIS 2 — Paint Extended (Расширенная рисовалка)](#5-tsis-2--paint-extended-расширенная-рисовалка)
6. [TSIS 3 — Racer Advanced (Продвинутые гонки)](#6-tsis-3--racer-advanced-продвинутые-гонки)
7. [TSIS 4 — Snake + Database (Змейка с БД)](#7-tsis-4--snake--database-змейка-с-бд)
8. [Структура проекта](#8-структура-проекта)
9. [Технологии](#9-технологии)
10. [Как запустить](#10-как-запустить)

---

## 1. Practice 11 — Racer (Гонки)

**Файл:** `Practice11/racer/racer.py`  
**Расширение Practice 10**

### Что было добавлено:
- **Взвешенные монеты** — 3 типа (бронза = 1 очко, серебро = 3, золото = 5) с разной вероятностью выпадения (60/30/10%)
- **Масштабирование скорости** — скорость врага увеличивается каждые 5 собранных очков-монет
- **Безопасный спавн** — монеты и враг не появляются друг на друге и на игроке (inflate с зоной безопасности)
- **Увеличенный хитбокс** — `rect.inflate(12, 12)` для удобного подбора монет
- **Тихий звук монеты** — громкость 40% (`set_volume(0.4)`)
- **Экран Game Over** — кнопки "Restart" и "Quit" с hover-эффектом

### Ключевой код:
```python
# типы монет с весами
COIN_TYPES = [
    {"color": (205,127,50), "value": 1, "radius": 8, "label": "B"},  # бронза
    {"color": (192,192,192), "value": 3, "radius": 10, "label": "S"}, # серебро
    {"color": (255,215,0),   "value": 5, "radius": 12, "label": "G"}, # золото
]
COIN_WEIGHTS = [60, 30, 10]  # вероятности

# случайный выбор типа
self.coin_type = random.choices(COIN_TYPES, weights=COIN_WEIGHTS, k=1)[0]
```

### Классы:
| Класс | Описание |
|-------|----------|
| `Enemy` | Вражеская машина, движется вниз, респавнится с зоной безопасности |
| `Coin` | Монетка со случайным типом, рисуется кружком |
| `Player` | Машина игрока, управление стрелками |

---

## 2. Practice 11 — Snake (Змейка)

**Файл:** `Practice11/snake/snake.py`  
**Расширение Practice 10**

### Что было добавлено:
- **Взвешенная еда** — 3 типа: красная (10 очков), оранжевая (20), золотая (50)
- **Исчезающая еда** — у каждой еды таймер (8/6/4 секунды), если не успел съесть — респавнится
- **Таймер-бар** — цветная полоска под едой, показывает оставшееся время (зелёная → красная)
- **Уровни** — каждые 3 съеденных еды = +1 уровень, +1 скорость

### Ключевой код:
```python
# проверяем не истёк ли таймер еды
elapsed = current_time - food_spawn_time
if elapsed >= food_type["lifetime_ms"]:
    food_pos = generate_food(snake)
    food_type = pick_food_type()
    food_spawn_time = current_time

# рисуем полоску таймера
ratio = max(0, 1.0 - elapsed / food_type["lifetime_ms"])
bar_color = (int(255*(1-ratio)), int(255*ratio), 0)
```

---

## 3. Practice 11 — Paint (Рисовалка)

**Файл:** `Practice11/paint/paint.py`  
**Расширение Practice 10**

### Что было добавлено:
- **4 новые фигуры**: квадрат, прямоугольный треугольник, равносторонний треугольник, ромб
- **GUI-панель** — кликабельные кнопки инструментов (8 шт.) + палитра цветов (8 цветов)
- **Непрерывный карандаш** — `pygame.draw.line()` между позициями мыши
- **Предпросмотр фигур** — при перетаскивании виден контур, закрепляется при отпускании

### Архитектура фигур:
```python
def build_shape(tool, x1, y1, x2, y2):
    """Универсальная функция: принимает инструмент и 2 точки,
    возвращает данные для отрисовки."""
    if tool == "square":
        side = max(abs(x2-x1), abs(y2-y1))
        # ... вычисляем координаты
        return ("rect", pygame.Rect(...))
    elif tool == "eq_tri":
        # ... равносторонний через sqrt(3)/2
        return ("polygon", [p1, p2, apex])
```

---

## 4. TSIS 1 — PhoneBook (Телефонная книга)

**Папка:** `TSIS1/`  
**База:** PostgreSQL (`contacts_db`)

### Файлы:
| Файл | Назначение |
|------|-----------|
| `phonebook.py` | Главное консольное приложение (12 пунктов меню) |
| `schema.sql` | DDL: таблицы `groups`, `phones`, расширение `phonebook` |
| `functions.sql` | `search_contacts()`, `get_contacts_paginated()` |
| `procedures.sql` | `upsert_contact`, `delete_contact`, `add_phone`, `move_to_group` |
| `config.py` | Чтение `database.ini` |
| `connect.py` | Подключение к PostgreSQL через psycopg2 |
| `contacts.csv` | Тестовые данные для импорта |

### Возможности меню:
1. Добавить / обновить контакт (upsert)
2. Добавить телефон контакту
3. Перенести контакт в группу
4. Поиск (имя / телефон / email / все телефоны)
5. Фильтр по группе
6. Поиск по email (ILIKE)
7. Сортировка (имя / дата рождения / дата добавления)
8. Постраничный просмотр (next / prev / quit)
9. Импорт из CSV
10. Импорт из JSON (с обработкой дубликатов: пропустить/перезаписать)
11. Экспорт в JSON
12. Удаление контакта

### Расширенная схема:
```sql
-- группы контактов
CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- несколько телефонов у одного контакта
CREATE TABLE IF NOT EXISTS phones (
    id SERIAL PRIMARY KEY,
    contact_id INTEGER REFERENCES phonebook(contact_id),
    phone VARCHAR(20) NOT NULL,
    type VARCHAR(10) CHECK (type IN ('home','work','mobile'))
);
```

---

## 5. TSIS 2 — Paint Extended (Расширенная рисовалка)

**Файл:** `TSIS2/paint.py`

### Расширения поверх Practice 11:
- **Карандаш (Pencil)** — непрерывное рисование
- **Прямая линия (Line)** — клик → тащим с предпросмотром → отпускаем
- **Заливка (Flood Fill)** — BFS-алгоритм через `get_at()` / `set_at()`
- **Текстовый инструмент** — кликнуть, набрать текст, Enter для подтверждения
- **3 размера кисти** — 2px / 5px / 10px (кнопки на панели)
- **Сохранение** — `Ctrl+S` → `canvas_20260428_235900.png`
- **11 инструментов** в GUI-панели

### Алгоритм заливки (BFS):
```python
def flood_fill(surface, start_x, start_y, fill_color):
    target_color = surface.get_at((start_x, start_y))
    queue = deque([(start_x, start_y)])
    visited = {(start_x, start_y)}
    while queue:
        x, y = queue.popleft()
        if surface.get_at((x, y)) != target_color: continue
        surface.set_at((x, y), fill_color)
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < w and 0 <= ny < h and (nx,ny) not in visited:
                visited.add((nx,ny)); queue.append((nx,ny))
```

---

## 6. TSIS 3 — Racer Advanced (Продвинутые гонки)

**Папка:** `TSIS3/`  
**Модули:** `main.py`, `ui.py`, `persistence.py`

### Возможности:
- **Встречные машины (TrafficCar)** — используют `Enemy.png` с цветным тонированием (`BLEND_MULT`)
- **Дорожные препятствия (Obstacle)** — барьеры, ямы
- **Ловушки (HazardZone)** — масло (скольжение), зона замедления, нитро-полосы
- **Монеты (Coin)** — 3 типа, используют `Coin.png` с тонированием
- **Усиления (PowerUp)**: Nitro (ускорение 4с), Shield (одноразовая защита), Repair (убирает 1 препятствие)
- **Масштабирование сложности** — каждые 8 сек: +1 скорость, больше трафика и препятствий
- **Система экранов**: Меню → Ввод имени → Игра → Конец → Таблица лидеров → Настройки

### Архитектура:
```
TSIS3/
├── main.py          # точка входа, игровые классы, игровой цикл
├── ui.py            # экраны (меню, game over, лидеры, настройки)
├── persistence.py   # сохранение/загрузка JSON
├── assets/          # изображения и звуки
│   ├── Player.png, Enemy.png, Coin.png, AnimatedStreet.png
│   ├── crash.wav, bell.wav, background.wav
├── leaderboard.json # топ-10 (авто-генерируется)
└── settings.json    # звук, цвет машины, сложность
```

### Машина состояний:
```
MENU → play → USERNAME → PLAYING → GAME_OVER → retry → PLAYING
                                              → menu  → MENU
     → leaderboard → LEADERBOARD → back → MENU
     → settings    → SETTINGS    → save → MENU
     → quit        → EXIT
```

---

## 7. TSIS 4 — Snake + Database (Змейка с БД)

**Папка:** `TSIS4/`  
**Модули:** `main.py`, `db.py`, `_create_db.py`  
**База:** PostgreSQL (`snake_db`)

### Игровые расширения:
- **Ядовитая еда** — тёмно-красная с "X", укорачивает змейку на 2; если длина ≤ 1 — смерть
- **3 усиления**: Speed (ускорение 5с), Slow (замедление 5с), Shield (1 столкновение)
- **Препятствия** — с 3-го уровня появляются стены, не блокируют змейку
- **PostgreSQL лидерборд** — таблицы `players` и `game_sessions`

### Схема БД:
```sql
CREATE TABLE players (
    id       SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE game_sessions (
    id            SERIAL PRIMARY KEY,
    player_id     INTEGER REFERENCES players(id),
    score         INTEGER NOT NULL,
    level_reached INTEGER NOT NULL,
    played_at     TIMESTAMP DEFAULT NOW()
);
```

### Функции БД (`db.py`):
| Функция | Что делает |
|---------|-----------|
| `setup_database()` | Создаёт таблицы если нет |
| `get_or_create_player(name)` | Находит или создаёт игрока |
| `save_result(name, score, level)` | Сохраняет результат сессии |
| `get_top10()` | Топ-10 всех времён |
| `get_personal_best(name)` | Личный рекорд игрока |

### Graceful degradation:
```python
try:
    from db import setup_database, save_result, get_top10, get_personal_best
    DB_AVAILABLE = True
except Exception:
    DB_AVAILABLE = False  # игра работает и без PostgreSQL
```

---

## 8. Структура проекта

```
PP2_Ali_Kakenov/
├── Practice11/
│   ├── racer/          # гонки с монетами
│   │   ├── racer.py
│   │   └── *.png, *.wav
│   ├── snake/          # змейка с исчезающей едой
│   │   └── snake.py
│   └── paint/          # рисовалка с фигурами
│       └── paint.py
├── TSIS1/              # телефонная книга + PostgreSQL
│   ├── phonebook.py
│   ├── schema.sql, functions.sql, procedures.sql
│   ├── config.py, connect.py
│   └── contacts.csv
├── TSIS2/              # расширенная рисовалка
│   └── paint.py
├── TSIS3/              # продвинутые гонки
│   ├── main.py, ui.py, persistence.py
│   └── assets/
├── TSIS4/              # змейка с БД
│   ├── main.py, db.py, _create_db.py
│   └── database.ini (не в git!)
└── .gitignore          # защита конфиденциальных данных
```

---

## 9. Технологии

| Технология | Где используется |
|-----------|-----------------|
| **Python 3.14** | Все проекты |
| **Pygame-CE 2.5** | Practice 11, TSIS 2–4 |
| **PostgreSQL** | TSIS 1 (contacts_db), TSIS 4 (snake_db) |
| **psycopg2** | Подключение к PostgreSQL |
| **PL/pgSQL** | Хранимые процедуры и функции (TSIS 1) |
| **JSON** | Настройки, лидерборд (TSIS 3), импорт/экспорт (TSIS 1) |
| **CSV** | Импорт контактов (TSIS 1) |
| **Git/GitHub** | Контроль версий |

---

## 10. Как запустить

### Установка зависимостей:
```bash
pip install pygame-ce psycopg2-binary
```

### Practice 11:
```bash
cd Practice11/racer && python racer.py
cd Practice11/snake && python snake.py
cd Practice11/paint && python paint.py
```

### TSIS 1 (нужен PostgreSQL):
```bash
# 1. Создать БД contacts_db
# 2. Настроить TSIS1/database.ini
cd TSIS1 && python phonebook.py
```

### TSIS 2:
```bash
cd TSIS2 && python paint.py
```

### TSIS 3:
```bash
cd TSIS3 && python main.py
```

### TSIS 4 (нужен PostgreSQL):
```bash
# 1. Запустить _create_db.py для создания БД
cd TSIS4 && python _create_db.py
python main.py
```

---

> **Безопасность:** `database.ini` с паролями **не загружен** в Git.  
> `.gitignore` защищает: `*.ini`, `settings.json`, `leaderboard.json`, `contacts_export.json`
