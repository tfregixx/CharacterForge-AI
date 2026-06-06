import sqlite3

DB_NAME = "characterforge.db"

def store_memory(memory):

```
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS memories(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        memory TEXT
    )
""")

cursor.execute(
    "INSERT INTO memories(memory) VALUES(?)",
    (memory,)
)

conn.commit()
conn.close()
```

def retrieve_memories(limit=10):

```
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS memories(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        memory TEXT
    )
""")

cursor.execute(
    "SELECT memory FROM memories ORDER BY id DESC LIMIT ?",
    (limit,)
)

rows = cursor.fetchall()

conn.close()

return [row[0] for row in rows]
```

def format_memories_for_context(memories):

```
if not memories:
    return ""

return "\n".join(memories)
```

def clear_memories():

```
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("DELETE FROM memories")

conn.commit()
conn.close()
```
