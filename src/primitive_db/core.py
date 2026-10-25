from prettytable import PrettyTable


def create_table(metadata, table_name, columns_list):
    if table_name in metadata:
        return metadata, f'Ошибка: Таблица "{table_name}" уже существует.'

    parsed_columns = {}
    for col in columns_list:
        if ":" not in col:
            return metadata, f"Некорректное значение: {col}. Попробуйте снова."
        
        col_name, col_type = col.split(":")
        col_type = col_type.lower()
        
        if col_type not in ["int", "str", "bool"]:
            return metadata, f"Некорректное значение: {col_type}. Попробуйте снова."
        
        parsed_columns[col_name] = col_type

    new_columns = {"ID": "int"}
    new_columns.update(parsed_columns)

    metadata[table_name] = new_columns
    return metadata, None


def drop_table(metadata, table_name):
    if table_name not in metadata:
        return metadata, f'Ошибка: Таблица "{table_name}" не существует.'
    
    del metadata[table_name]
    return metadata, None


def list_tables(metadata):
    return list(metadata.keys())


def insert(metadata, table_data, table_name, values):
    if table_name not in metadata:
        return table_data, f'Ошибка: Таблица "{table_name}" не существует.', None

    schema = metadata[table_name]
    col_names = list(schema.keys())[1:]  # Пропускаем ID
    
    # Проверка количества значений
    if len(values) != len(col_names):
        return (
            table_data, 
            f"Ошибка: неверное количество значений. "
            f"Ожидается {len(col_names)}, получено {len(values)}.", 
            None
        )

    parsed_values = []
    for val_str, col_name in zip(values, col_names):
        expected_type = schema[col_name]
        
        if expected_type == "int":
            try:
                parsed_values.append(int(val_str))
            except ValueError:
                return table_data, f"Неверный тип для {col_name}: ожидается int.", None
        elif expected_type == "bool":
            if val_str.lower() not in ["true", "false"]:
                return table_data, f"Неверный тип для {col_name}: ожидается bool.", None
            parsed_values.append(val_str.lower() == "true")
        else:
            parsed_values.append(str(val_str))

    new_id = max((row["ID"] for row in table_data), default=0) + 1

    new_row = {"ID": new_id}
    for val, col_name in zip(parsed_values, col_names):
        new_row[col_name] = val

    table_data.append(new_row)
    return table_data, None, new_id


def select(table_data, where_clause=None):
    if not where_clause:
        return table_data

    result = []
    for row in table_data:
        match = True
        for col, val in where_clause.items():
            if row.get(col) != val:
                match = False
                break
        if match:
            result.append(row)
    return result


def update(table_data, set_clause, where_clause):
    count = 0
    for row in table_data:
        match = True
        for col, val in where_clause.items():
            if row.get(col) != val:
                match = False
                break
        
        if match:
            row.update(set_clause)
            count += 1
    return table_data, count


def delete(table_data, where_clause):
    new_data = []
    count = 0
    for row in table_data:
        match = True
        for col, val in where_clause.items():
            if row.get(col) != val:
                match = False
                break
        
        if match:
            count += 1
        else:
            new_data.append(row)
    return new_data, count


def print_table(table_data):
    if not table_data:
        print("Данных нет.")
        return

    table = PrettyTable()
    table.field_names = list(table_data[0].keys())
    for row in table_data:
        table.add_row(list(row.values()))
    print(table)


def get_info(metadata, table_data, table_name):
    """Возвращает строку с информацией о таблице."""
    if table_name not in metadata:
        return None
    
    schema = metadata[table_name]
    cols_desc = ", ".join([f"{k}:{v}" for k, v in schema.items()])
    return (
        f"Таблица: {table_name}\n"
        f"Столбцы: {cols_desc}\n"
        f"Количество записей: {len(table_data)}"
    )