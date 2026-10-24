import shlex

import prompt

from primitive_db import core, utils

DB_META_FILE = "db_meta.json"


def print_help():
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    print("\n***База данных***")
    print_help()

    while True:
        user_input = prompt.string(">>>Введите команду: ").strip()
        if not user_input:
            continue

        # Загружаем актуальные метаданные перед каждой командой
        metadata = utils.load_metadata(DB_META_FILE)

        try:
            # Надежный парсинг с помощью shlex
            parts = shlex.split(user_input)
        except ValueError as e:
            print(f"Ошибка парсинга: {e}")
            continue

        command = parts[0].lower()
        args = parts[1:]

        if command == "exit":
            print("Выход из программы.")
            break

        elif command == "help":
            print_help()

        elif command == "list_tables":
            tables = core.list_tables(metadata)
            if not tables:
                print("Таблиц пока нет.")
            else:
                for t in tables:
                    print(f"- {t}")

        elif command == "create_table":
            if len(args) < 2:
                print("Некорректное значение: недостаточно аргументов.")
                continue
            
            table_name = args[0]
            columns = args[1:]
            
            updated_metadata, error = core.create_table(metadata, table_name, columns)
            if error:
                print(error)
            else:
                utils.save_metadata(DB_META_FILE, updated_metadata)
                # Формируем красивый вывод для пользователя
                cols_display = ", ".join(
                    [f"{k}:{v}" for k, v in updated_metadata[table_name].items()]
                )
                print(
                    f'Таблица "{table_name}" успешно создана '
                    f"со столбцами: {cols_display}"
                )

        elif command == "drop_table":
            if len(args) != 1:
                print("Некорректное значение: требуется одно имя таблицы.")
                continue
            
            table_name = args[0]
            updated_metadata, error = core.drop_table(metadata, table_name)
            if error:
                print(error)
            else:
                utils.save_metadata(DB_META_FILE, updated_metadata)
                print(f'Таблица "{table_name}" успешно удалена.')

        else:
            print(f"Функции {command} нет. Попробуйте снова.")