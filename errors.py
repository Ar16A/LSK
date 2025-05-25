# class OccupiedEmail(ValueError):
#     """Ошибка: в БД уже есть пользователь с такой почтой"""
#
#     def __init__(self, email):
#         self.email = email
#
#     def __str__(self):
#         return f"Пользователь с почтой {self.email} уже существует"
#
#
# class OccupiedUsername(ValueError):
#     """Ошибка: в БД уже есть пользователь с такой именем"""
#
#     def __init__(self, username):
#         self.username = username
#
#     def __str__(self):
#         return f"Пользователь с именем {self.username} уже существует"
#
#
# class OccupiedUsernameAndEmail(ValueError):
#     """Ошибка: в БД уже есть пользователь с такой именем и почтой"""
#
#     def __str__(self):
#         return "Такой пользователь уже зарегистрирован"
#
#
# class OccupiedNameNote(ValueError):
#     """Ошибка: в БД уже есть заметка с таким именем"""
#
#     def __init__(self, name):
#         self.name = name
#
#     def __str__(self):
#         return f"Заметка \"{self.name}\" уже существует. Выберите другое название для заметки"
#
#
# class OccupiedNameFolder(ValueError):
#     """Ошибка: в БД уже есть папка с таким именем"""
#
#     def __init__(self, name):
#         self.name = name
#
#     def __str__(self):
#         return f"Папка \"{self.name}\" уже существует. Выберите другое название для папки"
from httpx import ConnectError


class OccupiedName(ValueError):
    """Ошибка: в БД уже существует объект с таким названием"""

    def __init__(self, type: str, name: str = None):
        self.name = name
        self.type = type

    def __str__(self):
        match self.type:
            case "username":
                return f"Пользователь с именем {self.name} уже существует"
            case "email":
                return f"Пользователь с почтой {self.name} уже существует"
            case "all":
                return "Такой пользователь уже зарегистрирован"
            case "note":
                return f"Заметка \"{self.name}\" уже существует. Выберите другое название для заметки"
            case "folder":
                return f"Папка \"{self.name}\" уже существует. Выберите другое название для папки"
            case "section":
                return f"Раздел \"{self.name}\" уже существует. Выберите другое название для раздела"
            case "photo":
                return f'''В этой заметке уже есть картинка {self.name}.\n
                        Во избежание конфликтов, пожалуйста, переименуйте файл или выберите другой'''


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

class NotConnect(ConnectionError):
    pass