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
        id_user INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        password TEXT NOT NULL);''')
        cursor.execute("SELECT username, email FROM users")
        for elem in cursor.fetchall():
            if elem[0] == username:
                raise OccipiedUsername
            if elem[1] == email:
                raise OccipiedEmail
        cursor.execute("SELECT id_user FROM users")
        cursor.execute('''INSERT INTO users (id_user, username, email, password)
        VALUES (?, ?, ?, ?)''',
                       (cursor.fetchall()[-1][0] + 1, username, email, password))
        return User(username, email, password)