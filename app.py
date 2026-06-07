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
# SESSION STATE
# ------------------------

if "character" not in st.session_state:
    st.session_state.character = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "image_url" not in st.session_state:
    st.session_state.image_url = None


# ------------------------
# CHARACTER GENERATION (GROQ)
# ------------------------

def generate_character(genre, personality, powers):

    prompt = f"""
Create a detailed fictional character.

Genre: {genre}
Personality: {personality}
Powers: {powers}

Include:
Name
Age
Appearance
Backstory
Strengths
Weaknesses
Abilities
Catchphrase
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return str(response.choices[0].message.content)


# ------------------------
# CHAT
# ------------------------

def chat_with_character(character, user_message):

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": f"You are this character:\n\n{character}\n\nUser: {user_message}"
        }]
    )

    return str(response.choices[0].message.content)


# ------------------------
# FREE IMAGE SYSTEM (STABLE)
# ------------------------

def generate_image_url(genre, personality, powers):

    prompt = urllib.parse.quote_plus(
        f"{genre} fantasy character portrait, {personality}, {powers}, cinematic lighting, ultra detailed"
    )

    # Pollinations (try first)
    return f"https://image.pollinations.ai/prompt/{prompt}?model=flux"


def fallback_avatar(personality, powers):

    return (
        "https://api.dicebear.com/9.x/adventurer/png"
        f"?seed={urllib.parse.quote_plus(personality + powers)}"
    )


# ------------------------
# SIDEBAR
# ------------------------

with st.sidebar:

    st.header("🎨 Create Character")

    genre = st.selectbox("Genre", ["Fantasy", "Sci-Fi", "Anime", "Cyberpunk", "Horror"])
    personality = st.text_input("Personality", "Brave and mysterious")
    powers = st.text_input("Powers", "Shadow Magic")

    if st.button("Generate Character", use_container_width=True):

        st.session_state.character = generate_character(
            genre,
            personality,
            powers
        )

        st.session_state.image_url = generate_image_url(
            genre,
            personality,
            powers
        )

        st.session_state.chat_history = []


# ------------------------
# MAIN UI
# ------------------------

st.title("🎭 CharacterForge AI")
st.caption("Groq + Free Stable Image System (No API keys needed)")

# ------------------------
# DISPLAY
# ------------------------

if st.session_state.character:

    st.subheader("📜 Character Profile")

    col1, col2 = st.columns([1, 2])

    with col1:

        img = st.session_state.image_url

        st.markdown(
            f"""
            <img src="{img}"
                 style="width:100%; border-radius:12px;"
                 onerror="this.src='{fallback_avatar(personality, powers)}'">
            """,
            unsafe_allow_html=True
        )

        st.caption("If image fails → fallback avatar used")

    with col2:
        st.markdown(st.session_state.character)

    st.download_button(
        "📥 Download Character",
        st.session_state.character,
        file_name="character.txt"
    )

    st.divider()

    # ------------------------
    # CHAT
    # ------------------------

    st.subheader("💬 Chat With Character")

    for role, msg in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(msg)

    user_input = st.chat_input("Talk to your character...")

    if user_input:

        st.session_state.chat_history.append(("user", user_input))

        response = chat_with_character(
            st.session_state.character,
            user_input
        )

        st.session_state.chat_history.append(("assistant", response))

        st.rerun()

else:

    st.info("Create a character from the sidebar to begin.")
