import os
import urllib.parse
import requests
from io import BytesIO

import streamlit as st
from PIL import Image
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

if "image" not in st.session_state:
    st.session_state.image = None


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
# CHAT FUNCTION
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
# IMAGE GENERATION (FIXED — NO BROWSER DEPENDENCY)
# ------------------------

def generate_image(prompt):

    url = (
        "https://image.pollinations.ai/prompt/"
        + urllib.parse.quote_plus(prompt)
    )

    st.write("Image URL:", url)

    try:
        response = requests.get(
            url,
            timeout=30
        )

        st.write("Status Code:", response.status_code)
        st.write(
            "Content-Type:",
            response.headers.get("content-type")
        )

        if (
            response.status_code == 200
            and response.headers.get(
                "content-type",
                ""
            ).startswith("image/")
        ):
            return Image.open(
                BytesIO(response.content)
            )

        st.warning(
            "Pollinations returned a non-image response."
        )

    except Exception as e:
        st.error(f"Image Error: {e}")

    return None


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

            st.session_state.character = generate_character(
                genre,
                personality,
                powers
            )

            image_prompt = (
                f"{genre} dark fantasy character portrait, "
                f"{personality}, "
                f"{powers}, cinematic lighting, ultra detailed"
            )

            st.session_state.image = generate_image(image_prompt)

            st.session_state.chat_history = []


# ------------------------
# MAIN UI
# ------------------------

st.title("🎭 CharacterForge AI")
st.caption("Groq + Pollinations Stable Image Mode (FIXED)")


# ------------------------
# DISPLAY CHARACTER
# ------------------------

if st.session_state.character:

    st.subheader("📜 Character Profile")

    col1, col2 = st.columns([1, 2])

    with col1:

        if st.session_state.image:
            st.image(
                st.session_state.image,
                caption="🎨 AI Character Portrait",
                use_container_width=True
            )
        else:
            st.warning("Image failed to generate (Pollinations may be blocked or slow)")

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
