from fastapi import FastAPI, Body
import sqlite3

app = FastAPI()

@app.get("/users/")
def get_user(data: dict =  Body(...)):
    login = data["login"]
    password = data["password"]
    with sqlite3.connect("fakedocker/rembase.db") as database:
        cursor = database.cursor()
        cursor.execute(f"SELECT * FROM users WHERE {"email" if '@' in login else "username"} = ?;", (login,))
        answer = cursor.fetchone()
        if answer is None:
            return {"status": 2}
        if password != answer[3]:
            return {"status": 1}
    return {"status": 0, "user": answer[:3]}

@app.post("/users/")
def new_user(data: dict = Body(...)):
    username = data["username"]
    email = data["email"]
    password = data["password"]
    with sqlite3.connect("fakedocker/rembase.db") as database:
        cursor = database.cursor()
        cursor.execute("SELECT username, email FROM users WHERE username = ? OR email = ?;", (username, email))
        check = cursor.fetchone()
        if check is not None:
            answer = int(check[0] == username) + int(check[1] == email) * 2
            return {"status": answer}
        database.execute('''INSERT INTO users (username, email, password) VALUES (?, ?, ?);''',
                         (username, email, password))
    return {"status": 0}

# with sqlite3.connect("databases/rembase.db") as database:
#     database.row_factory = sqlite3.Row
#     items = database.execute("SELECT * FROM users").fetchall()
#     # print([[items[i][j] for i in range(len(items))] for j in range(len(items[0]))])
#     print([dict(item) for item in items])

# from fastapi import FastAPI
# import sqlite3
#
# app = FastAPI()
#
#
# def get_db_connection():
#     conn = sqlite3.connect('database.db')
#     conn.row_factory = sqlite3.Row
#     return conn
#
#
# @app.get("/items/")
# def read_items():
#     conn = get_db_connection()
#     items = conn.execute('SELECT * FROM items').fetchall()
#     conn.close()
#     return [dict(item) for item in items]
#
#
# @app.post("/items/")
# def create_item(name: str, description: str):
#     conn = get_db_connection()
#     conn.execute('INSERT INTO items (name, description) VALUES (?, ?)', (name, description))
#     conn.commit()
#     conn.close()
#     return {"message": "Item created successfully"}
