class OccupiedEmail(ValueError):
    def __init__(self, email):
        self.email = email

    def __str__(self):
        return f"Пользователь с почтой {self.email} уже существует"


class OccupiedUsername(ValueError):
    def __init__(self, username):
        self.username = username

    def __str__(self):
        return f"Пользователь с именем {self.username} уже существует"


class OccupiedUsernameAndEmail(ValueError):
    def __str__(self):
        return f"Такой пользователь уже зарегистрирован"
