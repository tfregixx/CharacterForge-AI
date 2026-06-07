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
# CHARACTER GENERATION
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

    prompt = f"""
You are this character:

{character}

Stay fully in character.

User: {user_message}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return str(response.choices[0].message.content)


# ------------------------
# IMAGE (STABLE + SAFE)
# ------------------------

def generate_character_image_url(genre, personality, powers):

    prompt = (
        f"{genre} fantasy character portrait, "
        f"{personality}, "
        f"{powers}, "
        f"cinematic lighting, ultra detailed, high quality digital art"
    )

    encoded = urllib.parse.quote(prompt)

    # Pollinations (optional, may fail)
    return (
        "https://image.pollinations.ai/prompt/"
        f"{encoded}"
        "?model=flux&width=1024&height=1024&nologo=true"
    )


# ------------------------
# SIDEBAR
# ------------------------

with st.sidebar:

    st.header("🎨 Create Character")

    genre = st.selectbox(
        "Genre",
        ["Fantasy", "Sci-Fi", "Anime", "Cyberpunk", "Superhero", "Steampunk", "Horror"]
    )

    personality = st.text_input("Personality", "Brave and mysterious")
    powers = st.text_input("Powers", "Shadow Magic")

    if st.button("Generate Character", use_container_width=True):

        with st.spinner("Generating character..."):

            character = generate_character(genre, personality, powers)

            # IMPORTANT: prevent accidental bad values like 0
            st.session_state.character = str(character)

            st.session_state.image_url = generate_character_image_url(
                genre,
                personality,
                powers
            )

            st.session_state.chat_history = []


# ------------------------
# MAIN UI
# ------------------------

st.title("🎭 CharacterForge AI")
st.caption("Groq-powered character generator")

# ------------------------
# CHARACTER DISPLAY
# ------------------------

if st.session_state.character:

    st.subheader("📜 Character Profile")

    col1, col2 = st.columns([1, 2])

    with col1:

        # ALWAYS WORKING IMAGE (NO FAIL)
        fallback_avatar = (
            "https://api.dicebear.com/9.x/adventurer/png"
            f"?seed={urllib.parse.quote(personality + powers)}"
        )

        # Pollinations try → fallback guaranteed
        if st.session_state.image_url:
            st.image(
                st.session_state.image_url,
                caption="🎨 AI Character Portrait",
                use_container_width=True
            )
        else:
            st.image(
                fallback_avatar,
                caption="🎨 Character Avatar",
                use_container_width=True
            )

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
