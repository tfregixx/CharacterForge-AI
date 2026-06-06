import streamlit as st
import sqlite3
import os
import urllib.parse

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# ----------------------------------

# CONFIG

# ----------------------------------

st.set_page_config(
page_title="CharacterForge AI",
page_icon="🎭",
layout="wide"
)

client = Groq(
api_key=os.getenv("GROQ_API_KEY")
)

# ----------------------------------

# DATABASE

# ----------------------------------

DB_NAME = "characterforge.db"

def init_db():

```
conn = sqlite3.connect(DB_NAME)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS characters(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS memories(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory TEXT
)
""")

conn.commit()
conn.close()
```

init_db()

# ----------------------------------

# CHARACTER STORAGE

# ----------------------------------

def save_character(content):

```
conn = sqlite3.connect(DB_NAME)

cursor = conn.cursor()

cursor.execute(
    "INSERT INTO characters(content) VALUES(?)",
    (content,)
)

conn.commit()
conn.close()
```

def get_characters():

```
conn = sqlite3.connect(DB_NAME)

cursor = conn.cursor()

cursor.execute(
    "SELECT id, content FROM characters ORDER BY id DESC"
)

rows = cursor.fetchall()

conn.close()

return rows
```

# ----------------------------------

# MEMORY

# ----------------------------------

def store_memory(memory):

```
conn = sqlite3.connect(DB_NAME)

cursor = conn.cursor()

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

cursor.execute(
    "SELECT memory FROM memories ORDER BY id DESC LIMIT ?",
    (limit,)
)

rows = cursor.fetchall()

conn.close()

return [row[0] for row in rows]
```

def clear_memories():

```
conn = sqlite3.connect(DB_NAME)

cursor = conn.cursor()

cursor.execute("DELETE FROM memories")

conn.commit()
conn.close()
```

# ----------------------------------

# AI FUNCTIONS

# ----------------------------------

def generate_character(
genre,
personality,
powers
):

```
prompt = f"""
```

Create a detailed fictional character.

Genre: {genre}
Personality: {personality}
Powers: {powers}

Generate:

Name
Age
Backstory
Strengths
Weaknesses
Abilities
Catchphrase
"""

```
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

return response.choices[0].message.content
```

def chat_with_character(
profile,
memory_context,
user_message
):

```
prompt = f"""
```

You are the character below.

Stay fully in character.

Character:
{profile}

Memory:
{memory_context}

User:
{user_message}

Respond as the character.
"""

```
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

return response.choices[0].message.content
```

# ----------------------------------

# SESSION STATE

# ----------------------------------

if "character" not in st.session_state:
st.session_state.character = None

if "chat_history" not in st.session_state:
st.session_state.chat_history = []

# ----------------------------------

# SIDEBAR

# ----------------------------------

with st.sidebar:

```
st.header("Create Character")

genre = st.selectbox(
    "Genre",
    [
        "Fantasy",
        "Sci-Fi",
        "Anime",
        "Cyberpunk"
    ]
)

personality = st.text_input(
    "Personality",
    "Brave and mysterious"
)

powers = st.text_input(
    "Powers",
    "Shadow Magic"
)

if st.button("Generate Character"):

    character = generate_character(
        genre,
        personality,
        powers
    )

    st.session_state.character = character
    st.session_state.chat_history = []

    st.success(
        "Character Generated!"
    )

st.divider()

st.subheader("Saved Characters")

for char_id, content in get_characters():

    if st.button(
        f"Character {char_id}"
    ):
        st.session_state.character = content
```

# ----------------------------------

# MAIN UI

# ----------------------------------

st.title("🎭 CharacterForge AI")
st.caption(
"Generate, chat, save and manage AI characters"
)

if st.session_state.character:

```
st.subheader("Character Profile")

prompt = urllib.parse.quote(
    f"""
    fantasy character portrait,
    {st.session_state.character[:500]},
    ultra detailed,
    fantasy concept art,
    cinematic lighting,
    masterpiece,
    highly detailed face
    """
)

image_url = (
    f"https://image.pollinations.ai/prompt/{prompt}"
)

col1, col2 = st.columns([1, 2])

with col1:

    st.image(
        image_url,
        caption="🎨 AI Generated Portrait",
        use_container_width=True
    )

with col2:

    st.markdown(
        st.session_state.character
    )

col1, col2 = st.columns(2)

with col1:

    if st.button(
        "💾 Save Character"
    ):
        save_character(
            st.session_state.character
        )

        st.success(
            "Character Saved!"
        )

with col2:

    st.download_button(
        label="📥 Download Character",
        data=st.session_state.character,
        file_name="character.txt",
        mime="text/plain"
    )

st.divider()

st.subheader("💬 Chat With Character")

for role, message in st.session_state.chat_history:

    with st.chat_message(role):

        st.markdown(message)

user_input = st.chat_input(
    "Talk to your character..."
)

if user_input:

    memories = retrieve_memories()

    memory_context = "\n".join(
        memories
    )

    response = chat_with_character(
        st.session_state.character,
        memory_context,
        user_input
    )

    store_memory(
        f"User: {user_input}"
    )

    store_memory(
        f"AI: {response}"
    )

    st.session_state.chat_history.append(
        ("user", user_input)
    )

    st.session_state.chat_history.append(
        ("assistant", response)
    )

    st.rerun()

if st.button(
    "🗑 Clear Memory"
):

    clear_memories()

    st.session_state.chat_history = []

    st.success(
        "Memory Cleared"
    )
```

else:

```
st.info(
    "Create a character from the sidebar to begin."
)
```
