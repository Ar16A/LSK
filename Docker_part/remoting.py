import os
import shutil

from fastapi import FastAPI, UploadFile, File, Form, Body
from fastapi.responses import StreamingResponse
import sqlite3
import json, io, zipfile

app = FastAPI()


@app.get("/check/")
def check_connect():
    print({"status": 0})
    return {"status": 0}

def safe_remove(path: str):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass

@app.post("/all/")
def synchro_client(json_str: str = Form(...),
                   photos: list[UploadFile] = File([]),
                   file_notes: list[UploadFile] = File([])):
    data = json.loads(json_str)
    id_user = data["id_user"]
    # json = {"id_user": id_user, "sections": sections, "folders": folders, "notes": notes,
    #         "photos": photos})
    select_exists = lambda x: f"SELECT EXISTS(SELECT NULL FROM {x} WHERE id_local = ? AND id_user = ?);"

    with sqlite3.connect("rembase.db") as database:
        cursor = database.cursor()
        cursor.execute(
            '''UPDATE users SET seq_sections = ?, seq_folders = ?, seq_notes = ?, seq_photos = ? WHERE id_user = ?;''',
            (*data["seqs"], id_user))

        for section in data["sections"]:
            cursor.execute(select_exists("sections"), (section[0], id_user))
            if not cursor.fetchone()[0]:
                cursor.execute('''INSERT INTO sections (id_local, name, color, id_local_root, id_user)
                               VALUES (?, ?, ?, ?, ?)''',
                               (*section, id_user))
        for folder in data["folders"]:
            cursor.execute(select_exists("folders"), (folder[0], id_user))
            if not cursor.fetchone()[0]:
                cursor.execute('''INSERT INTO folders (id_local, name, id_local_section, id_user)
                               VALUES (?, ?, ?, ?)''',
                               (*folder, id_user))
        for note in data["notes"]:
            cursor.execute(select_exists("notes"), (note[0], id_user))
            if not cursor.fetchone()[0]:
                cursor.execute('''INSERT INTO notes (id_local, name, cnt_photos, id_local_folder, id_user)
                               VALUES (?, ?, ?, ?, ?)''',
                               (*note, id_user))
            else:
                cursor.execute('''UPDATE notes SET cnt_photos = ? WHERE id_local = ? AND id_user = ?''',
                               (note[2], note[0], id_user))
        for file in file_notes:
            os.makedirs(f"{id_user}/imgs/{file.filename}", exist_ok=True)
            with open(f"{id_user}/notes/{file.filename}.txt", "wb") as f:
                f.write(file.file.read())

        for photo in data["photos"]:
            cursor.execute(select_exists("photos"), (photo[0], id_user))
            if not cursor.fetchone()[0]:
                cursor.execute('''INSERT INTO photos (id_local, name, size, id_local_note, id_user)
                               VALUES (?, ?, ?, ?, ?)''',
                               (*photo, id_user))
            else:
                cursor.execute('''UPDATE photos SET size = ? WHERE id_local = ? AND id_user = ?''',
                               (photo[2], photo[0], id_user))
        for file in photos:
            with open(f"{id_user}/imgs/{file.filename}", "wb") as f:
                f.write(file.file.read())

        for obj in data["deleted"]:
            match obj[0]:
                case "photos":
                    cursor.execute("SELECT name, id_local_note FROM photos WHERE id_user = ? AND id_local = ?;",
                                   (id_user, obj[1]))
                    photo = cursor.fetchone()
                    if photo is not None:
                        # shutil.rmtree(f"{id_user}/imgs/{photo[1]}/{photo[0]}")
                        os.remove(f"{id_user}/imgs/{photo[1]}/{photo[0]}")
                        # safe_remove(f"{id_user}/imgs/{photo[1]}/{photo[0]}")
                        cursor.execute("DELETE FROM photos WHERE id_user = ? AND id_local = ?;",
                                       (id_user, obj[1]))
                case "notes":
                    safe_remove(f"{id_user}/notes/{obj[1]}.txt")
                    cursor.execute("DELETE FROM notes WHERE id_user = ? AND id_local = ?;",
                                   (id_user, obj[1]))
                case _:
                    cursor.execute(f"DELETE FROM {obj[0]} WHERE id_user = ? AND id_local = ?",
                                   (id_user, obj[1]))
    print(f"Пользователь {id_user} успешно синхронизировался")
    return {"status": 0}


# @app.post("/notes/")
# def new_note(json_str: str = Form(...),
#              note: UploadFile = File(...),
#              photos: list[UploadFile] = File([])):
#     data = json.loads(json_str)
#     id_user = data["id_user"]
#     with sqlite3.connect("rembase.db") as database:
#         cursor = database.cursor()
#         cursor.execute("INSERT INTO notes (id_local, name, id_local_section, id_user) VALUES (?, ?, ?, ?);",
#                        (data["id_local"], data["name"], data["id_local_folder"], id_user))
#         cursor.execute(
#             "UPDATE users SET seq_note = seq_note + 1 WHERE id_user = ?",
#             (id_user,))
#         for img in data["photos"]:
#             cursor.execute("SELECT EXISTS(SELECT NULL FROM photos WHERE id_user = ? AND id_local = ?);",
#                            (id_user, img[0]))
#             if cursor.fetchone()[0]:
#                 cursor.execute("UPDATE photos SET size = ? WHERE id_user = ? AND id_local = ?;",
#                                (img[2], img[0], id_user))
#             else:
#                 cursor.execute('''INSERT INTO photos (id_local, name, size, id_local_note, id_user) VALUES (?, ?, ?, ?, ?)''',
#                                (*img, data["id_local"], id_user))
#         for file in photos:
#             with open(f"{id_user}/imgs/{file.filename}", "wb") as f:
#                 f.write(file.file.read())
#         with open(f"{id_user}/notes/{data["id_note"]}.txt", "wb") as f:
#             f.write(note.file.read())
#         print("Тут нечего принтить")
#
#
# @app.post("/folders/")
# def new_folder(data: dict = Body(...)):
#     with sqlite3.connect("rembase.db") as database:
#         cursor = database.cursor()
#         cursor.execute("INSERT INTO folders (id_local, name, id_local_section, id_user) VALUES (?, ?, ?, ?);",
#                        (data["id_local"], data["name"], data["id_local_section"], data["id_user"]))
#         cursor.execute(
#             "UPDATE users SET seq_folders = seq_folders + 1 WHERE id_user = ?",
#             (data["id_user"],))
#         print("Тут нечего принтить")
#
#
# @app.post("/sections/")
# def new_section(data: dict = Body(...)):
#     with sqlite3.connect("rembase.db") as database:
#         cursor = database.cursor()
#         cursor.execute("INSERT INTO sections (id_local, name, color, id_user, id_local_root) VALUES (?, ?, ?, ?, ?);",
#                        (data["id_local"], data["name"], data["color"], data["id_user"], data["id_root"]))
#         cursor.execute("INSERT INTO folders (id_local, id_local_section, id_user) VALUES (?, ?, ?);",
#                        (data["id_root"], data["id_local"], data["id_user"]))
#         cursor.execute(
#             "UPDATE users SET seq_sections = seq_sections + 1, seq_folders = seq_folders + 1 WHERE id_user = ?",
#             (data["id_user"],))
#         print("Тут нечего принтить")


@app.get("/users/")
def get_user(data: dict = Body(...)):
    login = data["login"]
    password = data["password"]
    with sqlite3.connect("rembase.db") as database:
        cursor = database.cursor()
        cursor.execute(f"SELECT * FROM users WHERE {"email" if '@' in login else "username"} = ?;",
                       (login,))
        answer = cursor.fetchone()
        notes = []
        photos = []
        if answer is None:
            result = {"status": 2}
        elif password != answer[3]:
            result = {"status": 1}
        else:
            cursor.execute("SELECT * FROM sections WHERE id_user = ?;", (answer[0],))
            sections = cursor.fetchall()

            cursor.execute("SELECT * FROM folders WHERE id_user = ?;", (answer[0],))
            folders = cursor.fetchall()

            cursor.execute("SELECT * FROM notes WHERE id_user = ?;", (answer[0],))
            notes = cursor.fetchall()

            cursor.execute("SELECT * FROM photos WHERE id_user = ?;", (answer[0],))
            photos = cursor.fetchall()

            slicing = lambda data: [x[1:-1] for x in data]

            result = {"status": 0, "user": answer[:3], "seqs": answer[4:],
                      "sections": slicing(sections), "folders": slicing(folders),
                      "notes": slicing(notes), "photos": slicing(photos)}

    # result = {"status": 0, "user": answer[:3],
    #           "sections": [x[1:-1] for x in sections], "folders": [x[1:-1] for x in folders],
    #           "notes": [x[1:-1] for x in notes], "photos": [x[1:-1] for x in photos]}

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("data.json", json.dumps(result))
        for cur_note in notes:
            zf.write(f"{answer[0]}/notes/{cur_note[1]}.txt", arcname=f"notes/{cur_note[1]}.txt")
        for img in photos:
            zf.write(f"{answer[0]}/imgs/{img[4]}/{img[2]}", arcname=f"imgs/{img[4]}/{img[2]}")

    zip_buffer.seek(0)

    return StreamingResponse(zip_buffer, media_type="application/zip",
                             headers={"Content-Disposition": "attachment; filename=archive.zip"})
    # print(result)
    # return result


@app.post("/users/")
def new_user(data: dict = Body(...)):
    username = data["username"]
    email = data["email"]
    password = data["password"]
    id_user = None
    with sqlite3.connect("rembase.db") as database:
        cursor = database.cursor()
        cursor.execute("SELECT username, email FROM users WHERE username = ? OR email = ?;", (username, email))
        check = cursor.fetchone()
        if check is not None:
            answer = int(check[0] == username) + int(check[1] == email) * 2
            print({"status": answer})
            return {"status": answer}
        cursor.execute('''INSERT INTO users (username, email, password) VALUES (?, ?, ?);''',
                         (username, email, password))
        id_user = cursor.lastrowid
    os.makedirs(f"{id_user}/notes", exist_ok=True)
    os.makedirs(f"{id_user}/imgs", exist_ok=True)
    print({"status": 0})
    return {"status": 0}
