from prettytable import PrettyTable

from primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)

# Глобальный кэш для select
_cacher = create_cacher()


@handle_db_errors
def create_table(metadata, table_name, columns_list):
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata, None

    parsed_columns = {}
    for col in columns_list:
        if ":" not in col:
            print(f"Некорректное значение: {col}. Попробуйте снова.")
            return metadata, None
        col_name, col_type = col.split(":")
        col_type = col_type.lower()
        if col_type not in ["int", "str", "bool"]:
            print(f"Некорректное значение: {col_type}. Попробуйте снова.")
            return metadata, None
        parsed_columns[col_name] = col_type

    new_columns = {"ID": "int"}
    new_columns.update(parsed_columns)
    metadata[table_name] = new_columns
    return metadata, None


@confirm_action("удаление таблицы")
@handle_db_errors
def drop_table(metadata, table_name):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata, None
    del metadata[table_name]
    return metadata, None


@handle_db_errors
def list_tables(metadata):
    return list(metadata.keys())


@log_time
@handle_db_errors
def insert(metadata, table_data, table_name, values):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return table_data, None, None

    schema = metadata[table_name]
    col_names = list(schema.keys())[1:]

    if len(values) != len(col_names):
        print(
            f"Ошибка: неверное количество значений. "
            f"Ожидается {len(col_names)}, получено {len(values)}."
        )
        return table_data, None, None

    parsed_values = []
    for val_str, col_name in zip(values, col_names):
        expected_type = schema[col_name]
        if expected_type == "int":
            try:
                parsed_values.append(int(val_str))
            except ValueError:
                print(f"Неверный тип для {col_name}: ожидается int.")
                return table_data, None, None
        elif expected_type == "bool":
            if val_str.lower() not in ["true", "false"]:
                print(f"Неверный тип для {col_name}: ожидается bool.")
                return table_data, None, None
            parsed_values.append(val_str.lower() == "true")
        else:
            parsed_values.append(str(val_str))

    new_id = max((row["ID"] for row in table_data), default=0) + 1
    new_row = {"ID": new_id}
    for val, col_name in zip(parsed_values, col_names):
        new_row[col_name] = val

    table_data.append(new_row)
    return table_data, None, new_id


@log_time
@handle_db_errors
def select(table_data, where_clause=None):
    key = str(where_clause)  # ключ кэша
    # Кэшируем только если данные таблицы не менялись
    # (простое приближение: кэш по условию)
    def compute():
        if not where_clause:
            return table_data
        result = []
        for row in table_data:
            if all(row.get(col) == val for col, val in where_clause.items()):
                result.append(row)
        return result

    return _cacher(key, compute)


@handle_db_errors
def update(table_data, set_clause, where_clause):
    count = 0
    for row in table_data:
        if all(row.get(col) == val for col, val in where_clause.items()):
            row.update(set_clause)
            count += 1
    return table_data, count


@confirm_action("удаление записи")
@handle_db_errors
def delete(table_data, where_clause):
    new_data = []
    count = 0
    for row in table_data:
        if all(row.get(col) == val for col, val in where_clause.items()):
            count += 1
        else:
            new_data.append(row)
    return new_data, count


@handle_db_errors
def print_table(table_data):
    if not table_data:
        print("Данных нет.")
        return
    expected_keys = list(table_data[0].keys())
    for row in table_data:
        if list(row.keys()) != expected_keys:
            print("Ошибка: данные повреждены. Удалите файл data/users.json.")
            return
    table = PrettyTable()
    table.field_names = expected_keys
    for row in table_data:
        table.add_row(list(row.values()))
    print(table)


@handle_db_errors
def get_info(metadata, table_data, table_name):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None
    schema = metadata[table_name]
    cols_desc = ", ".join([f"{k}:{v}" for k, v in schema.items()])
    return (
        f"Таблица: {table_name}\n"
        f"Столбцы: {cols_desc}\n"
        f"Количество записей: {len(table_data)}"
    )