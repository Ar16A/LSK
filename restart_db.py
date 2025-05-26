import sqlite3
import os

if os.path.exists("Docker_part/rembase.db"):
    os.remove("Docker_part/rembase.db")
# if os.path.exists("mainbase.db"):
#     os.remove("mainbase.db")

with sqlite3.connect("Docker_part/rembase.db") as database:
    cursor = database.cursor()

    cursor.execute('''CREATE TABLE users (
                    id_user INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    seq_sections INTEGER NOT NULL DEFAULT 0,
                    seq_folders INTEGER NOT NULL DEFAULT 0,
                    seq_notes INTEGER NOT NULL DEFAULT 0,
                    seq_photos INTEGER NOT NULL DEFAULT 0);''')

    cursor.execute('''CREATE TABLE sections (
                    id_section INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_local INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    color TEXT NOT NULL,
                    id_local_root INTEGER NOT NULL,
                    id_user INTEGER NOT NULL,
                    FOREIGN KEY (id_user) REFERENCES users (id_user));''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS folders (
                    id_folder INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_local INTEGER NOT NULL,
                    name TEXT,
                    id_local_section INTEGER NOT NULL,
                    id_user INTEGER NOT NULL,
                    FOREIGN KEY (id_user) REFERENCES users (id_user));''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS notes (
                        id_note INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_local INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        cnt_photos INTEGER DEFAULT 0 NOT NULL,
                        id_local_folder INTEGER NOT NULL,
                        id_user INTEGER NOT NULL,
                        FOREIGN KEY (id_user) REFERENCES users (id_user));''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS photos (
                            id_photo INTEGER PRIMARY KEY AUTOINCREMENT,
                            id_local INTEGER NOT NULL,
                            name TEXT NOT NULL,
                            size INTEGER NOT NULL,
                            id_local_note INTEGER NOT NULL,
                            id_user INTEGER NOT NULL,
                            FOREIGN KEY (id_user) REFERENCES users (id_user));''')

    # cursor.execute('''CREATE TRIGGER IF NOT EXISTS add_main_folder
    #         AFTER INSERT ON sections
    #         FOR EACH ROW
    #         BEGIN
    #             INSERT INTO folders (id_section) SELECT MAX(id_section) FROM sections;
    #             UPDATE sections SET id_root = (
    #             SELECT id_folder FROM folders WHERE id_section = (SELECT MAX(id_section) FROM sections) AND name IS NULL)
    #             WHERE id_section = (SELECT MAX(id_section) FROM sections);
    #         END;''')

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_sections ON sections (id_user);")
    cursor.execute("CREATE INDEX idx_user_folders on folders (id_user);")
    cursor.execute("CREATE INDEX idx_user_notes on notes (id_user);")
    cursor.execute("CREATE INDEX idx_user_photos on photos (id_user);")

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_section_folders ON folders (id_local_section);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_folder_notes ON notes (id_local_folder);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_photo_notes ON photos (id_local_note);")

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_users ON users (id_user);")
    # cursor.execute("CREATE INDEX IF NOT EXISTS idx_section_sections ON sections (id_section);")
    # cursor.execute("CREATE INDEX IF NOT EXISTS idx_folder_folders ON folders (id_folder);")
    # cursor.execute("CREATE INDEX IF NOT EXISTS idx_note_notes ON notes (id_note);")
    # cursor.execute("CREATE INDEX IF NOT EXISTS idx_photo_photos ON photos (id_photo);")

    # cursor.execute("CREATE INDEX idx_local_sections on sections (id_local);")
    # cursor.execute("CREATE INDEX idx_local_folders on folders (id_local);")
    # cursor.execute("CREATE INDEX idx_local_notes on notes (id_local);")
    # cursor.execute("CREATE INDEX idx_local_photos on photos (id_local);")