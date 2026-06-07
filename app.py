```python
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

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

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
# AI FUNCTIONS
# ------------------------

def generate_character(
    genre,
    personality,
    powers
):
    prompt = f"""
Create a detailed fictional character.

Genre: {genre}
Personality: {personality}
Powers: {powers}

Generate:

# Name
# Age
# Appearance
# Backstory
# Strengths
# Weaknesses
# Abilities
# Catchphrase

Format using markdown.
"""

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


def chat_with_character(
    character_profile,
    user_message
):
    prompt = f"""
You are this character.

Character:
{character_profile}

Stay completely in character.

User:
{user_message}
"""

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


def generate_character_image_url(
    genre,
    personality,
    powers
):
    prompt = urllib.parse.quote(
        f"""
        {genre} fantasy character,
        {personality},
        powers: {powers},
        character portrait,
        highly detailed,
        fantasy concept art,
        cinematic lighting,
        masterpiece,
        ultra detailed,
        sharp focus,
        digital painting,
        artstation quality
        """
    )

    return (
        f"https://image.pollinations.ai/prompt/{prompt}"
        "?width=1024"
        "&height=1024"
        "&seed=42"
        "&nologo=true"
    )

# ------------------------
# SIDEBAR
# ------------------------

with st.sidebar:

    st.header("🎨 Create Character")

    genre = st.selectbox(
        "Genre",
        [
            "Fantasy",
            "Sci-Fi",
            "Anime",
            "Cyberpunk",
            "Superhero",
            "Steampunk",
            "Horror"
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

    if st.button(
        "Generate Character",
        use_container_width=True
    ):

        with st.spinner(
            "Generating character..."
        ):

            st.session_state.character = (
                generate_character(
                    genre,
                    personality,
                    powers
                )
            )

            st.session_state.image_url = (
                generate_character_image_url(
                    genre,
                    personality,
                    powers
                )
            )

            st.session_state.chat_history = []

# ------------------------
# MAIN
# ------------------------

st.title("🎭 CharacterForge AI")

st.caption(
    "Generate, visualize, and chat with AI-powered characters."
)

# ------------------------
# CHARACTER PROFILE
# ------------------------

if st.session_state.character:

    st.subheader(
        "📜 Character Profile"
    )

    col1, col2 = st.columns(
        [1, 2]
    )

    with col1:

        st.image(
            st.session_state.image_url,
            caption="🎨 AI Generated Character",
            use_container_width=True
        )

    with col2:

        st.markdown(
            st.session_state.character
        )

    st.download_button(
        label="📥 Download Character",
        data=st.session_state.character,
        file_name="character.txt",
        mime="text/plain",
        use_container_width=True
    )

    st.divider()

    # ------------------------
    # CHAT SECTION
    # ------------------------

    st.subheader(
        "💬 Chat With Character"
    )

    for role, message in (
        st.session_state.chat_history
    ):

        with st.chat_message(role):

            st.markdown(message)

    user_input = st.chat_input(
        "Talk to your character..."
    )

    if user_input:

        st.session_state.chat_history.append(
            (
                "user",
                user_input
            )
        )

        with st.spinner(
            "Character is thinking..."
        ):

            response = (
                chat_with_character(
                    st.session_state.character,
                    user_input
                )
            )

        st.session_state.chat_history.append(
            (
                "assistant",
                response
            )
        )

        st.rerun()

else:

    st.info(
        "Create a character from the sidebar to begin."
    )
```
