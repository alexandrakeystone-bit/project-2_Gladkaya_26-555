import json
import os

DB_FILE = "db.json"
_table_cache = {}


def load_metadata():
    """Загружает метаданные таблиц из JSON-файла."""
    global _table_cache
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            _table_cache = json.load(f)
    else:
        _table_cache = {}


def save_metadata():
    """Сохраняет метаданные таблиц в JSON-файл."""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(_table_cache, f, indent=2)


def create_table(table_name, columns_str):
    """Создает таблицу с указанными столбцами."""
    if table_name in _table_cache:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return

    # Добавляем автоматический столбец ID
    columns = {"ID": "int"}
    
    for col in columns_str:
        if ":" not in col:
            print(f"Некорректное значение: {col}. Попробуйте снова.")
            return
        
        col_name, col_type = col.split(":")
        col_type = col_type.lower()
        
        if col_type not in ["int", "str", "bool"]:
            print(f"Некорректное значение: {col_type}. Попробуйте снова.")
            return
            
        columns[col_name] = col_type

    _table_cache[table_name] = columns
    save_metadata()
    
    # Формируем красивый вывод
    cols_display = ", ".join([f"{k}:{v}" for k, v in columns.items()])
    print(f'Таблица "{table_name}" успешно создана со столбцами: {cols_display}')


def drop_table(table_name):
    """Удаляет таблицу."""
    if table_name in _table_cache:
        del _table_cache[table_name]
        save_metadata()
        print(f'Таблица "{table_name}" успешно удалена.')
    else:
        print(f'Ошибка: Таблица "{table_name}" не существует.')


def list_tables():
    """Показывает список всех таблиц."""
    if not _table_cache:
        print("Таблиц пока нет.")
    else:
        for table in _table_cache.keys():
            print(f"- {table}")