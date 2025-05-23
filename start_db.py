import sqlite3

with sqlite3.connect("fakedocker/rembase.db") as database:
    cursor = database.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    id_user INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL);''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS sections (
    id_section INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    color TEXT NOT NULL,
    id_user INTEGER NOT NULL,
    id_root INTEGER UNIQUE);''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS folders (
                    id_folder INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    id_section INTEGER NOT NULL);''')

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

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_users ON users (id_user);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_sections ON sections (id_user);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_section_folders ON folders (id_section);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_folder_notes ON notes (id_folder);")

    cursor.execute('''CREATE TABLE IF NOT EXISTS photos (
                    id_photo INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    size INTEGER NOT NULL,
                    id_note INTEGER NOT NULL);''')
