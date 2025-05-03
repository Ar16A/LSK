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


class UserNotExists(ValueError):
    """Ошибка: пользователя с таким логином нет в БД"""
    def __init__(self, login):
        self.login = login

    def __str__(self):
        return f"Пользователя с {"почтой" if '@' in self.login else "именем"} {self.login} не существует"


class IncorrectPassword(ValueError):
    """Ошибка: введённый пароль не совпадает с паролем из БД"""
    def __str__(self):
        return "Неверный пароль"


class NotChange(ValueError):
    """Ошибка: в заметку не было внесено изменений"""
    def __str__(self):
        return "Заметка не изменена"