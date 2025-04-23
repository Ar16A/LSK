class OccupiedEmail(ValueError):
    """Ошибка: в БД уже есть пользователь с такой почтой"""
    def __init__(self, email):
        self.email = email

    def __str__(self):
        return f"Пользователь с почтой {self.email} уже существует"


class OccupiedUsername(ValueError):
    """Ошибка: в БД уже есть пользователь с такой именем"""
    def __init__(self, username):
        self.username = username

    def __str__(self):
        return f"Пользователь с именем {self.username} уже существует"


class OccupiedUsernameAndEmail(ValueError):
    """Ошибка: в БД уже есть пользователь с такой именем и почтой"""
    def __str__(self):
        return "Такой пользователь уже зарегистрирован"


class OccupiedNameNote(ValueError):
    """Ошибка: в БД уже есть заметка с таким именем"""
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"Заметка \"{self.name}\" уже существует. Выберите другое название для заметки"