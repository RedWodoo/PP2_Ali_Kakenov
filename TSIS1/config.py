"""
config.py — чтение параметров подключения к PostgreSQL из database.ini.
Ищет файл относительно папки этого скрипта, а не рабочей директории.
"""
import os
from configparser import ConfigParser

# папка, в которой лежит этот файл (TSIS1/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_config(filename='database.ini', section='postgresql'):
    """Загружаем параметры из .ini файла рядом с этим скриптом."""
    filepath = os.path.join(BASE_DIR, filename)
    parser = ConfigParser()
    found = parser.read(filepath, encoding='utf-8')
    if not found:
        raise Exception(f'Файл {filepath} не найден или пустой')
    if parser.has_section(section):
        return dict(parser.items(section))
    else:
        raise Exception(f'Секция [{section}] не найдена в {filepath}')
