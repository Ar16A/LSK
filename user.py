import sqlite3
from errors import *


class Node:
    pass


class User:
    def __init__(self, username: str, email: str, password: str):
        self.username = username
        self.email = email
        self.password = password


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
                    raise OccipiedUsernameAndEmail
                case 2:
                    raise OccipiedEmail
                case 1:
                    raise OccipiedUsername
                case 0:
                    pass
        cursor.execute('''INSERT INTO users (username, email, password)
        VALUES (?, ?, ?)''',
                       (username, email, password))
        return User(username, email, password)