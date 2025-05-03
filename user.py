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
    Содержит: id пользователя, имя, почту, пароль"""

    def __init__(self, id_user: int, username: str, email: str, password: str):
        self.id_user = id_user
        self.username = username
        self.email = email
        self.password = password

    def listNotes(self) -> list[tuple[int, str]]:
        """Получение списка заметок пользователя"""
        with sqlite3.connect(f"databases/mainbase.db") as database:
            cursor = database.cursor()
            cursor.execute(f"SELECT id_note, name FROM notes WHERE id_user = ?;", (self.id_user,))
            answer = cursor.fetchall()
            return [] if answer is None else answer

    def textNote(self, id_note: int) -> str:
        with open(f"notes/{self.id_user}_{id_note}.txt", 'r', encoding="UTF-8") as note:
            return note.read()

    def deleteNote(self, id_note: int) -> None:
        os.remove(f"notes/{self.id_user}_{id_note}.txt")
        with sqlite3.connect(f"databases/mainbase.db") as database:
            cursor = database.cursor()
            cursor.execute("DELETE FROM notes WHERE id_note = ?;", (id_note,))

    def saveNote(self, id_note: int, text: str) -> None:
        with open(f"notes/{self.id_user}_{id_note}.txt", 'r+', encoding="UTF-8") as note:
            if text == note.read():
                raise NotChange
        with open(f"notes/{self.id_user}_{id_note}.txt", 'w', encoding="UTF-8") as note:
            note.write(text)

    def createNote(self, name: str, text: str) -> None:
        with sqlite3.connect(f"databases/mainbase.db") as database:
            cursor = database.cursor()
            cursor.execute("SELECT name FROM notes WHERE id_user = ?", (self.id_user,))
            if name in itertools.chain(*cursor.fetchall()):
                raise OccupiedNameNote(name)
            cursor.execute("INSERT INTO notes (name, id_user) VALUES (?, ?);",
                           (name, self.id_user))
            cursor.execute("SELECT MAX(id_note) FROM notes WHERE id_user = ?", (self.id_user,))
            id_note = cursor.fetchone()[0]
        with open(f"notes/{self.id_user}_{id_note}.txt", 'w', encoding="UTF-8") as note:
            note.write(text)


def loginUser(login: str, password: str) -> User:
    """Авторизация пользователя"""
    with sqlite3.connect("databases/mainbase.db") as database:
        cursor = database.cursor()
        cursor.execute(f"SELECT * FROM users WHERE {"email" if '@' in login else "username"} = ?;", (login,))
        answer = cursor.fetchone()
        if answer is None:
            raise UserNotExists(login)
        if password != answer[3]:
            raise IncorrectPassword
        cursor.execute('''CREATE TABLE IF NOT EXISTS notes (
        id_note INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        id_user INTEGER NOT NULL,
        FOREIGN KEY (id_user) REFERENCES users (id_user) ON DELETE CASCADE);''')

        # cursor.execute('''CREATE TRIGGER IF NOT EXISTS autoincrement_notes
        # AFTER INSERT ON notes
        # FOR EACH ROW
        # BEGIN
        #     UPDATE notes SET id_note = (SELECT MAX(id_note) FROM notes) + 1
        #     WHERE id_note = NULL;
        # END;''')
    return User(*answer)


def registerUser(username: str, email: str, password: str) -> None:
    """Регистрация нового пользователя"""
    with sqlite3.connect("databases/mainbase.db") as database:
        cursor = database.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id_user INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL);''')
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
        cursor.execute('''INSERT INTO users (username, email, password) VALUES (?, ?, ?);''',
                       (username, email, password))
