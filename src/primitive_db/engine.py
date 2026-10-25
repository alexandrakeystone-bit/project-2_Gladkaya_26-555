import re
import shlex

import prompt

from primitive_db import core, parser, utils

DB_META_FILE = "db_meta.json"


def print_help():
    print("\n***Операции с данными***")
    print("Функции:")
    print(
        "<command> insert into <имя_таблицы> values "
        "(<значение1>, ...) - создать запись."
    )
    print(
        "<command> select from <имя_таблицы> where <столбец> = <значение> "
        "- прочитать записи."
    )
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print(
        "<command> update <имя> set <col> = <val> "
        "where <col> = <val> - обновить."
    )
    print("<command> delete from <имя> where <col> = <val> - удалить.")
    print("<command> info <имя_таблицы> - информация о таблице.")

    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    print("\n***База данных***")
    print_help()

    while True:
        user_input = prompt.string(">>>Введите команду: ").strip()
        if not user_input:
            continue

        metadata = utils.load_metadata(DB_META_FILE)

        if user_input.lower().startswith("insert into"):
            insert_pattern = r"insert\s+into\s+(\w+)\s+values\s*\((.*)\)"
            match = re.match(insert_pattern, user_input, re.IGNORECASE)
            if not match:
                print("Некорректный формат insert.")
                continue

            table_name = match.group(1)
            values_str = match.group(2)

            try:
                values = shlex.split(values_str.replace(",", " "))
            except ValueError as e:
                print(f"Ошибка парсинга: {e}")
                continue

            table_data = utils.load_table_data(table_name)
            updated_data, _, new_id = core.insert(
                metadata, table_data, table_name, values
            )
            if new_id is not None:
                utils.save_table_data(table_name, updated_data)
                print(
                    f'Запись с ID={new_id} успешно добавлена '
                    f'в таблицу "{table_name}".'
                )
            continue

        try:
            parts = shlex.split(user_input)
        except ValueError as e:
            print(f"Ошибка парсинга: {e}")
            continue

        command = parts[0].lower()

        if command == "create_table":
            if len(parts) < 3:
                print("Некорректное значение: недостаточно аргументов.")
                continue
            table_name = parts[1]
            columns = parts[2:]
            updated_metadata, _ = core.create_table(metadata, table_name, columns)
            if updated_metadata is not None:
                utils.save_metadata(DB_META_FILE, updated_metadata)
                cols_display = ", ".join(
                    [f"{k}:{v}" for k, v in updated_metadata[table_name].items()]
                )
                print(
                    f'Таблица "{table_name}" успешно создана '
                    f"со столбцами: {cols_display}"
                )

        elif command == "list_tables":
            tables = core.list_tables(metadata)
            if not tables:
                print("Таблиц пока нет.")
            else:
                for t in tables:
                    print(f"- {t}")

        elif command == "drop_table":
            if len(parts) != 2:
                print("Некорректное значение: требуется одно имя таблицы.")
                continue
            table_name = parts[1]
            updated_metadata, _ = core.drop_table(metadata, table_name)
            if updated_metadata is not None:
                utils.save_metadata(DB_META_FILE, updated_metadata)
                print(f'Таблица "{table_name}" успешно удалена.')

        elif command == "select":
            if len(parts) < 3 or parts[1] != "from":
                print("Некорректный формат select.")
                continue

            table_name = parts[2]
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue

            where_clause = None
            if len(parts) > 3:
                if parts[3] == "where":
                    where_clause = parser.parse_where(parts[4:])
                    if where_clause is None:
                        print("Некорректное условие where.")
                        continue
                else:
                    print("Некорректный формат select.")
                    continue

            table_data = utils.load_table_data(table_name)
            filtered_data = core.select(table_data, where_clause)
            core.print_table(filtered_data)

        elif command == "update":
            try:
                table_name = parts[1]
                if table_name not in metadata:
                    print(f'Ошибка: Таблица "{table_name}" не существует.')
                    continue

                if parts[2] != "set" or "where" not in parts:
                    print("Некорректный формат update.")
                    continue

                where_idx = parts.index("where")
                set_args = parts[3:where_idx]
                where_args = parts[where_idx + 1:]

                set_clause = parser.parse_set(set_args)
                where_clause = parser.parse_where(where_args)

                if set_clause is None or where_clause is None:
                    print("Некорректные условия set или where.")
                    continue

                table_data = utils.load_table_data(table_name)
                updated_data, count = core.update(
                    table_data, set_clause, where_clause
                )
                utils.save_table_data(table_name, updated_data)
                print(f"Обновлено записей: {count}.")

            except IndexError:
                print("Некорректный формат update.")

        elif command == "delete":
            if len(parts) < 5 or parts[1] != "from" or parts[3] != "where":
                print("Некорректный формат delete.")
                continue

            table_name = parts[2]
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue

            where_clause = parser.parse_where(parts[4:])
            if where_clause is None:
                print("Некорректное условие where.")
                continue

            table_data = utils.load_table_data(table_name)
            result = core.delete(table_data, where_clause)
            if result is not None:
                updated_data, count = result
                utils.save_table_data(table_name, updated_data)
                print(f"Удалено записей: {count}.")

        elif command == "info":
            if len(parts) != 2:
                print("Некорректное значение: требуется имя таблицы.")
                continue
            table_name = parts[1]
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue
            table_data = utils.load_table_data(table_name)
            info_str = core.get_info(metadata, table_data, table_name)
            if info_str:
                print(info_str)

        elif command == "exit":
            print("Выход из программы.")
            break

        elif command == "help":
            print_help()

        else:
            print(f"Функции {command} нет. Попробуйте снова.")