import prompt

import primitive_db.db as db


def print_help():
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def welcome():
    # Загружаем данные при старте
    db.load_metadata()
    
    print("\n***База данных***")
    print_help()

    while True:
        # Получаем строку от пользователя и убираем лишние пробелы по краям
        user_input = prompt.string(">>>Введите команду: ").strip()
        
        if not user_input:
            continue

        # Разбиваем строку на отдельные слова
        parts = user_input.split()
        command = parts[0].lower()
        args = parts[1:]

        if command == "exit":
            print("Выход из программы.")
            break
            
        elif command == "help":
            print_help()
            
        elif command == "list_tables":
            db.list_tables()
            
        elif command == "create_table":
            if len(args) < 2:
                print(
    "Некорректное значение: недостаточно аргументов. "
    "Попробуйте снова."
                )
                continue
            table_name = args[0]
            columns = args[1:]
            db.create_table(table_name, columns)
            
        elif command == "drop_table":
            if len(args) != 1:
                print(
    "Некорректное значение: требуется одно имя таблицы. "
    "Попробуйте снова."
                )
                continue
            db.drop_table(args[0])
            
        else:
            print(f"Функции {command} нет. Попробуйте снова.")