import sqlite3

from errors import *
import os
import itertools


# class Note:
#     def __init__(self, id_note: int, name: str, text: str):
#         self.id_note = id_note
#         self.name = name
#         self.text = text

class User:
    """Класс пользователей\n
    Содержит: id пользователя, имя, почту, пароль, id корневой папки"""

    def __init__(self, id_user: int, username: str, email: str, password: str, id_root: int):
        self.id_user = id_user
        self.username = username
        self.email = email
        self.password = password
        self.id_root = id_root

    def list_notes(self) -> list[list[tuple[int, str]]]:
        """Получение списка заметок и папок пользователя"""
        with sqlite3.connect(f"databases/mainbase.db") as database:
            cursor = database.cursor()
            cursor.execute("SELECT id_folder, name FROM folders WHERE id_user = ? AND name IS NOT NULL;", (self.id_user,))
            answer = [cursor.fetchall()]
            answer += [self.list_folder(self.id_root)]
            return [] if answer is None else answer

    def list_folder(self, id_folder: int) -> list[tuple[int, str]]:
        """Получение списка заметок из папки"""
        with sqlite3.connect(f"databases/mainbase.db") as database:
            cursor = database.cursor()
            cursor.execute("SELECT id_note, name FROM notes WHERE id_folder = ?;", (id_folder,))
            answer = cursor.fetchall()
            return [] if answer is None else answer

    def folder_is_empty(self, id_folder: int) -> bool:
        """Проверка папки на наличие в ней заметок"""
        with sqlite3.connect(f"databases/mainbase.db") as database:
            cursor = database.cursor()
            cursor.execute("SELECT EXISTS (SELECT id_note FROM notes WHERE id_folder = ?);", (id_folder,))
            return not cursor.fetchone()[0]

    def text_note(self, id_note: int) -> str:
        """Получение текста заметки по её id"""
        with open(f"notes/{self.id_user}_{id_note}.txt", 'r', encoding="UTF-8") as note:
            return note.read()

    def delete_note(self, id_note: int) -> None:
        """Удаление заметки по id"""
        os.remove(f"notes/{self.id_user}_{id_note}.txt")
        with sqlite3.connect(f"databases/mainbase.db") as database:
            cursor = database.cursor()
            cursor.execute("DELETE FROM notes WHERE id_note = ?;", (id_note,))

    def delete_folder(self, id_folder: int):
        """Удаление папки со всеми заметками внутри"""
        with sqlite3.connect(f"databases/mainbase.db") as database:
            cursor = database.cursor()
            cursor.execute("SELECT id_note FROM notes WHERE id_folder = ?", (id_folder,))
            for id_note in [x[0] for x in cursor.fetchall()]:
                self.delete_note(id_note)
            cursor.execute("DELETE FROM folders WHERE id_folder = ?;", (id_folder,))

    def save_note(self, id_note: int, text: str) -> None:
        """Сохранение заметки"""
        with open(f"notes/{self.id_user}_{id_note}.txt", 'r+', encoding="UTF-8") as note:
            if text == note.read():
                raise NotChange
        with open(f"notes/{self.id_user}_{id_note}.txt", 'w', encoding="UTF-8") as note:
            note.write(text)

    def create_folder(self, name: str) -> None:
        """Создание папки"""
        with sqlite3.connect("databases/mainbase.db") as database:
            cursor = database.cursor()
            cursor.execute("SELECT name FROM folders WHERE id_user = ?;", (self.id_user,))
            if name in itertools.chain(*cursor.fetchall()):
                raise OccupiedNameFolder(name)
            cursor.execute("INSERT INTO folders (name, id_user) VALUES (?, ?);",
                           (name, self.id_user))

    def create_note(self, name: str, text: str, id_folder: int = 0) -> None:
        """Создание заметки"""
        if not id_folder:
            id_folder = self.id_root
        with sqlite3.connect("databases/mainbase.db") as database:
            cursor = database.cursor()
            cursor.execute("SELECT name FROM notes WHERE id_folder = ?;", (id_folder,))
            if name in itertools.chain(*cursor.fetchall()):
                raise OccupiedNameNote(name)
            cursor.execute("INSERT INTO notes (name, id_folder) VALUES (?, ?);",
                           (name, id_folder))
            cursor.execute("SELECT MAX(id_note) FROM notes WHERE id_folder = ?;", (id_folder,))
            id_note = cursor.fetchone()[0]
        with open(f"notes/{self.id_user}_{id_note}.txt", 'w', encoding="UTF-8") as note:
            note.write(text)


def login_user(login: str, password: str) -> User:
    """Авторизация пользователя"""
    with sqlite3.connect("databases/mainbase.db") as database:
        cursor = database.cursor()
        cursor.execute(f"SELECT * FROM users WHERE {"email" if '@' in login else "username"} = ?;", (login,))
        answer = cursor.fetchone()
        if answer is None:
            raise UserNotExists(login)
        if password != answer[3]:
            raise IncorrectPassword
    return User(*answer)


def register_user(username: str, email: str, password: str) -> None:
    """Регистрация нового пользователя"""
    with sqlite3.connect("databases/mainbase.db") as database:
        cursor = database.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id_user INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        id_root_folder INTEGER UNIQUE);''')

        cursor.execute("SELECT username, email FROM users WHERE username = ? OR email = ?;", (username, email))
        check = cursor.fetchone()
        if check is not None:
            match int(check[0] == username) + int(check[1] == email) * 2:
                case 3:
                    raise OccupiedUsernameAndEmail()
                case 2:
                    raise OccupiedEmail(email)
                case 1:
                    raise OccupiedUsername(username)
                case 0:
                    pass

        cursor.execute('''CREATE TABLE IF NOT EXISTS folders (
                        id_folder INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        id_user INTEGER NOT NULL);''')

        # cursor.execute("SELECT id_user FROM users WHERE username = ? AND email = ?;", (username, email))
        # id_user = cursor.fetchone()[0]

        cursor.execute('''CREATE TRIGGER IF NOT EXISTS add_main_folder
                AFTER INSERT ON users
                FOR EACH ROW
                BEGIN
                    INSERT INTO folders (id_user) SELECT MAX(id_user) FROM users;
                    UPDATE users SET id_root_folder = (
                    SELECT id_folder FROM folders WHERE id_user = (SELECT MAX(id_user) FROM users) AND name IS NULL)
                    WHERE id_user = (SELECT MAX(id_user) FROM users);
                END;''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS notes (
                        id_note INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        id_folder INTEGER NOT NULL);''')

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_users ON users (id_user);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_folders ON folders (id_user);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_folder_notes ON notes (id_folder);")

        # cursor.execute('''CREATE TRIGGER IF NOT EXISTS autoincrement_notes
        # AFTER INSERT ON notes
        # FOR EACH ROW
        # BEGIN
        #     UPDATE notes SET id_note = (SELECT MAX(id_note) FROM notes) + 1
        #     WHERE id_note = NULL;
        # END;''')

        cursor.execute('''INSERT INTO users (username, email, password) VALUES (?, ?, ?);''',
                       (username, email, password))