import sqlite3

def init_db():
    conn = sqlite3.connect("characterforge.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS characters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT
    )
    """)

    conn.commit()
    conn.close()

def save_character(content):
    conn = sqlite3.connect("characterforge.db")
    c = conn.cursor()

    c.execute(
        "INSERT INTO characters (content) VALUES (?)",
        (content,)
    )

    conn.commit()
    conn.close()

def get_characters():
    conn = sqlite3.connect("characterforge.db")
    c = conn.cursor()

    c.execute("SELECT id, content FROM characters")

    rows = c.fetchall()

    conn.close()

    return rows
