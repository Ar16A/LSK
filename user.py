import sqlite3
import os
import itertools
import hashlib
import requests
import re

from errors import *

__path_to_host__ = 'http://localhost:8000/'

# Команда для запуска сервера:
# uvicorn remoting:app --host 0.0.0.0 --port 8000


# class Note:
#     def __init__(self, id_note: int, name: str, text: str):
#         self.id_note = id_note
#         self.name = name
#         self.text = text

def new_photo(id_note: int, path: str, size: int) -> str:
    name = path.split('/')[-1]
    with sqlite3.connect(f"databases/mainbase.db") as database:
        cursor = database.cursor()
        cursor.execute("SELECT name FROM photos WHERE id_note = ?;", (id_note,))
        # result = cursor.fetchall()
        if name in itertools.chain(cursor.fetchall()):
            raise OccupiedName("photo", name)
        cursor.execute("INSERT INTO photos (name, size, id_note) VALUES (?, ?, ?)",
                       (name, size, id_note))
        cursor.execute("SELECT seq FROM sqlite_sequence WHERE name = photos;")
        if not os.path.exists(f"images/{id_note}"):
            os.mkdir(f"images/{id_note}")
        return f"images/{id_note}/{name}__{cursor.fetchone()[0]}"


def list_notes(id_folder: int) -> list[tuple[int, str]]:
    """Получение списка заметок из папки"""
    with sqlite3.connect(f"databases/mainbase.db") as database:
        cursor = database.cursor()
        cursor.execute("SELECT id_note, name FROM notes WHERE id_folder = ?;", (id_folder,))
        answer = cursor.fetchall()
        return [] if answer is None else answer


def folder_is_empty(id_folder: int) -> bool:
    """Проверка папки на наличие в ней заметок"""
    with sqlite3.connect(f"databases/mainbase.db") as database:
        cursor = database.cursor()
        cursor.execute("SELECT EXISTS (SELECT id_note FROM notes WHERE id_folder = ?);", (id_folder,))
        return not cursor.fetchone()[0]


def text_note(id_note: int) -> str:
    """Получение текста заметки по её id"""
    with open(f"notes/{id_note}.txt", 'r', encoding="UTF-8") as note:
        return note.read()


def delete_note(id_note: int) -> None:
    """Удаление заметки по id"""
    os.remove(f"notes/{id_note}.txt")
    with sqlite3.connect(f"databases/mainbase.db") as database:
        cursor = database.cursor()
        cursor.execute("DELETE FROM notes WHERE id_note = ?;", (id_note,))


def delete_folder(id_folder: int):
    """Удаление папки со всеми заметками внутри"""
    with sqlite3.connect(f"databases/mainbase.db") as database:
        cursor = database.cursor()
        cursor.execute("SELECT id_note FROM notes WHERE id_folder = ?", (id_folder,))
        for id_note in [x[0] for x in cursor.fetchall()]:
            delete_note(id_note)
        cursor.execute("DELETE FROM folders WHERE id_folder = ?;", (id_folder,))


def save_note(id_note: int, text: str) -> None:
    """Сохранение заметки"""
    with open(f"notes/{id_note}.txt", 'r+', encoding="UTF-8") as note:
        if text == note.read():
            raise NotChange
    with open(f"notes/{id_note}.txt", 'w', encoding="UTF-8") as note:
        note.write(text)

    img_now = re.findall(r"!\[(.*?)\]\((.*?)\)", text)


class Section:
    """:param id_section
    :param name
    :param color
    :param id_user
    :param id_root"""

    def __init__(self, id_section: int, name: str, color: str, id_user: int, id_root: int):
        self.id_section = id_section
        self.name = name
        self.color = color
        self.id_user = id_user
        self.id_root = id_root

    def menu(self) -> list[list[tuple[int, str]]]:
        """Получение списка заметок и папок из раздела"""
        with sqlite3.connect(f"databases/mainbase.db") as database:
            cursor = database.cursor()
            cursor.execute("SELECT id_folder, name FROM folders WHERE id_section = ? AND name IS NOT NULL;",
                           (self.id_user,))
            answer = [cursor.fetchall()]
            answer += [list_notes(self.id_root)]
            return [] if answer is None else answer

    def create_folder(self, name: str) -> None:
        """Создание папки"""
        with sqlite3.connect("databases/mainbase.db") as database:
            cursor = database.cursor()
            cursor.execute("SELECT name FROM folders WHERE id_section = ?;", (self.id_section,))
            if name in itertools.chain(*cursor.fetchall()):
                raise OccupiedName("folder", name)
            cursor.execute("INSERT INTO folders (name, id_section) VALUES (?, ?);",
                           (name, self.id_section))

    def create_note(self, name: str, text: str, id_folder: int = 0) -> None:
        """Создание заметки"""
        if not id_folder:
            id_folder = self.id_root
        with sqlite3.connect("databases/mainbase.db") as database:
            cursor = database.cursor()
            cursor.execute("SELECT name FROM notes WHERE id_folder = ?;", (id_folder,))
            if name in itertools.chain(*cursor.fetchall()):
                raise OccupiedName("note", name)
            cursor.execute("INSERT INTO notes (name, id_folder) VALUES (?, ?);",
                           (name, id_folder))
            cursor.execute("SELECT MAX(id_note) FROM notes WHERE id_folder = ?;", (id_folder,))
            id_note = cursor.fetchone()[0]
        with open(f"notes/{id_note}.txt", 'w', encoding="UTF-8") as note:
            note.write(text)

    def delete(self):
        with sqlite3.connect(f"databases/mainbase.db") as database:
            cursor = database.cursor()
            cursor.execute("SELECT id_folder FROM folders WHERE id_section = ?", (self.id_section,))
            for id_folder in [x[0] for x in cursor.fetchall()]:
                delete_folder(id_folder)
            cursor.execute("DELETE FROM sections WHERE id_section = ?;", (self.id_section,))


class User:
    """Класс пользователей\n
    Содержит: id пользователя, имя, почту, пароль, id корневой папки\n"""

    def __init__(self, id_user: int, username: str, email: str):
        self.id_user = id_user
        self.username = username
        self.email = email

    def create_section(self, name: str, color: str):
        with sqlite3.connect(f"databases/mainbase.db") as database:
            cursor = database.cursor()
            cursor.execute("SELECT EXISTS(SELECT name FROM sections WHERE name = ?);", (name,))
            if cursor.fetchone()[0]:
                raise OccupiedName("section", name)
            cursor.execute("INSERT INTO sections (name, color, id_user) VALUES (?, ?, ?);",
                           (name, color, self.id_user))

def list_sections(self) -> tuple[Section, ...]:
    with sqlite3.connect(f"databases/mainbase.db") as database:
        cursor = database.cursor()
        cursor.execute("SELECT * FROM sections;")
        return tuple(Section(*args) for args in cursor.fetchall())

def login_user(login: str, password: str) -> User:
    """Авторизация пользователя"""
    response = requests.get(__path_to_host__ + 'users/',
                            json={"login": login, "password": hashlib.sha256(password.encode()).hexdigest()})
    answer = response.json()
    print(response.status_code, response.json())
    match answer["status"]:
        case 2:
            raise UserNotExists(login)
        case 1:
            raise IncorrectPassword
        case 0:
            return User(*answer["user"])


def register_user(username: str, email: str, password: str) -> None:
    """Регистрация нового пользователя"""
    with sqlite3.connect("databases/mainbase.db") as database:
        cursor = database.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS sections (
        id_section INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        color TEXT NOT NULL,
        id_root INTEGER UNIQUE);''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS folders (
                        id_folder INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        id_section INTEGER NOT NULL);''')

        # cursor.execute("SELECT id_user FROM users WHERE username = ? AND email = ?;", (username, email))
        # id_user = cursor.fetchone()[0]

        cursor.execute('''CREATE TRIGGER IF NOT EXISTS add_main_folder
                AFTER INSERT ON sections
                FOR EACH ROW
                BEGIN
                    INSERT INTO folders (id_section) SELECT MAX(id_section) FROM sections;
                    UPDATE sections SET id_root = (
                    SELECT id_folder FROM folders WHERE id_section = (SELECT MAX(id_section) FROM sections) AND name IS NULL)
                    WHERE id_section = (SELECT MAX(id_section) FROM sections);
                END;''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS notes (
                            id_note INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            cnt_photos INTEGER DEFAULT 0 NOT NULL,
                            id_folder INTEGER NOT NULL);''')

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_section_folders ON folders (id_section);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_folder_notes ON notes (id_folder);")

        # cursor.execute('''CREATE TRIGGER IF NOT EXISTS autoincrement_notes
        # AFTER INSERT ON notes
        # FOR EACH ROW
        # BEGIN
        #     UPDATE notes SET id_note = (SELECT MAX(id_note) FROM notes) + 1
        #     WHERE id_note = NULL;
        # END;''')

        data = {"username": username, "email": email, "password": hashlib.sha256(password.encode()).hexdigest()}
        response = requests.post(__path_to_host__ + "users/", json=data)
        print(response.status_code, response.json())
        match response.json()["status"]:
            case 3:
                raise OccupiedName("all")
            case 2:
                raise OccupiedName("email", email)
            case 1:
                raise OccupiedName("username", username)
            case 0:
                pass
