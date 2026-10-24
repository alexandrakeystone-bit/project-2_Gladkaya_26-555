def create_table(metadata, table_name, columns_list):
    """
    Создает таблицу в metadata.
    Возвращает (updated_metadata, error_message_or_None).
    """
    if table_name in metadata:
        return metadata, f'Ошибка: Таблица "{table_name}" уже существует.'

    # Валидация типов данных
    parsed_columns = {}
    for col in columns_list:
        if ":" not in col:
            return metadata, f"Некорректное значение: {col}. Попробуйте снова."
        
        col_name, col_type = col.split(":")
        col_type = col_type.lower()
        
        if col_type not in ["int", "str", "bool"]:
            return metadata, f"Некорректное значение: {col_type}. Попробуйте снова."
        
        parsed_columns[col_name] = col_type

    # Автоматически добавляем ID в начало
    new_columns = {"ID": "int"}
    new_columns.update(parsed_columns)

    metadata[table_name] = new_columns
    return metadata, None


def drop_table(metadata, table_name):
    """
    Удаляет таблицу из metadata.
    Возвращает (updated_metadata, error_message_or_None).
    """
    if table_name not in metadata:
        return metadata, f'Ошибка: Таблица "{table_name}" не существует.'
    
    del metadata[table_name]
    return metadata, None


def list_tables(metadata):
    """Возвращает список имен таблиц."""
    return list(metadata.keys())