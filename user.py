import sqlite3
from errors import *


class Note:
    def __init__(self, id_note: int, name: str, text: str):
        self.id_note = id_note
        self.name = name
        self.text = text


class User:
    """Класс пользователей\n
    Содержит: id пользователя, имя, почту, пароль"""
    def __init__(self, id_user: int, username: str, email: str, password: str):
        self.id_user = id_user
        self.username = username
        self.email = email
        self.password = password

    def ListNotes(self) -> list:
        with sqlite3.connect(f"databases/notes.db") as note:
            cursor = note.cursor()
            cursor.execute("SELECT * FROM ?", (str(self.id_user),))
            return cursor.fetchall()

    def Notes(self) -> list:
        """Получение заметок пользователя\n
                Возвращает список кортежей:\n
                1-ый элемент кортежа - id заметки,\n
                2-ой - название"""
        pass

    def findNote(self, id_note: int) -> str:
        pass


    def saveNote(self, cur_note: Note) -> None:
        with open(f"notes/{self.id_user}_{cur_note.id_note}.txt", "w", encoding="UTF-8") as note:
            print(cur_note.text, file=note)

    def newNote(self, name: str, text: str) -> Note:
        with sqlite3.connect(f"databases/notes.db") as note:
            cursor = note.cursor()
            cursor.execute("SELECT name FROM ? WHERE name = ?", (str(self.id_user), name))
            if cursor.fetchone() is not None:
                raise OccupiedNameNote(name)
            cursor.execute("INSERT INTO ? name VALUES (?)", (self.id_user, name))
            cursor.execute("SELECT MAX(id_note) FROM ?", (self.id_user,))
            cur_note = Note(cursor.fetchone()[0], name, text)
        self.saveNote(cur_note)
        return cur_note



def newUser(username: str, email: str, password: str) -> User:
    with sqlite3.connect("databases/mainbase.db") as database:
        cursor = database.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id_user INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL);''')
        cursor.execute("SELECT username, email FROM users WHERE username = ? OR email = ?", (username, email))
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
        cursor.execute('''INSERT INTO users (username, email, password)
        VALUES (?, ?, ?)''',
                       (username, email, password))
        cursor.execute("SELECT MAX(id_user) FROM users")
        answer = User(cursor.fetchone()[0], username, email, password)

    with sqlite3.connect(f"databases/notes.db") as note:
        cursor = note.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS ? (
        id_note INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE)''', (str(answer.id_user),))

    return answer
