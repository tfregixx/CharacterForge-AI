import os
import urllib.parse

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# ------------------------
# CONFIG
# ------------------------

st.set_page_config(
    page_title="🎭 CharacterForge AI",
    page_icon="🎭",
    layout="wide"
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ------------------------
# STATE
# ------------------------

if "character" not in st.session_state:
    st.session_state.character = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ------------------------
# GROQ CHARACTER
# ------------------------

def generate_character(genre, personality, powers):

    prompt = f"""
Create a detailed fictional character.

Genre: {genre}
Personality: {personality}
Powers: {powers}

Include:
Name, Age, Appearance, Backstory, Strengths, Weaknesses, Abilities, Catchphrase
"""

    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return str(res.choices[0].message.content)


# ------------------------
# CHAT
# ------------------------

def chat_with_character(character, user_message):

    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": f"You are this character:\n\n{character}\n\nUser: {user_message}"
        }]
    )

    return str(res.choices[0].message.content)


# ------------------------
# STABLE IMAGE (NO FAIL)
# ------------------------

def generate_avatar(personality, powers):

    seed = urllib.parse.quote_plus(personality + powers)

    return f"https://api.dicebear.com/9.x/adventurer/png?seed={seed}"


# ------------------------
# UI
# ------------------------

st.title("🎭 CharacterForge AI")
st.caption("Groq-powered character generator (stable mode)")

with st.sidebar:

    st.header("🎨 Create Character")

    genre = st.selectbox(
        "Genre",
        ["Fantasy", "Sci-Fi", "Anime", "Cyberpunk", "Horror"]
    )

    personality = st.text_input("Personality", "Brave and mysterious")
    powers = st.text_input("Powers", "Shadow Magic")

    if st.button("Generate Character"):

        st.session_state.character = generate_character(
            genre, personality, powers
        )

        st.session_state.chat_history = []


# ------------------------
# MAIN
# ------------------------

if st.session_state.character:

    st.subheader("📜 Character Profile")

    col1, col2 = st.columns([1, 2])

    with col1:

        avatar_url = generate_avatar(personality, powers)

        st.image(
            avatar_url,
            caption="🎨 Character Avatar",
            use_container_width=True
        )

    with col2:

        st.markdown(st.session_state.character)

    st.divider()

    st.subheader("💬 Chat With Character")

    for role, msg in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(msg)

    user_input = st.chat_input("Talk to your character...")

    if user_input:

        st.session_state.chat_history.append(("user", user_input))

        reply = chat_with_character(st.session_state.character, user_input)

        st.session_state.chat_history.append(("assistant", reply))

        st.rerun()

else:

    st.info("Create a character from the sidebar to begin.")
