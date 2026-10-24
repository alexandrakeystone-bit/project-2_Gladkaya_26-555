import prompt


def welcome():
    print("\n***")
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")
    
    # Бесконечный цикл для запроса команд
    while True:
        command = prompt.string("Введите команду: ")
        
        if command == "exit":
            break
        elif command == "help":
            print("\n<command> exit - выйти из программы")
            print("<command> help - справочная информация")
        else:
            print("Неизвестная команда. Введите 'help' для списка команд.")