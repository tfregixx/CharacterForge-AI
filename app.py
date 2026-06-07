import os
from io import BytesIO

import requests
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

# ------------------------
# API KEYS
# ------------------------

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

client = Groq(
    api_key=GROQ_API_KEY
)

# Stable SDXL model
HF_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"

HF_API_URL = (
    "https://api-inference.huggingface.co/models/"
    "stabilityai/stable-diffusion-xl-base-1.0"
)

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
# CHARACTER GENERATION
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

    return str(
        response.choices[0].message.content
    )

# ------------------------
# CHARACTER CHAT
# ------------------------

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

    return str(
        response.choices[0].message.content
    )

# ------------------------
# HUGGING FACE IMAGE
# ------------------------

def generate_image(prompt):

    if not HF_TOKEN:
        st.error(
            "HF_TOKEN not found in environment variables."
        )
        return None

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}"
    }

    payload = {
        "inputs": prompt
    }

    try:

        response = requests.post(
            HF_API_URL,
            headers=headers,
            json=payload,
            timeout=180
        )

        if response.status_code == 200:

            image = Image.open(
                BytesIO(response.content)
            )

            return image

        st.error(
            f"Hugging Face Error {response.status_code}"
        )

        try:
            st.json(response.json())
        except Exception:
            st.text(response.text)

        return None

    except requests.exceptions.ConnectionError:
        st.error(
            "ConnectionError: Could not reach Hugging Face."
        )
        return None

    except requests.exceptions.Timeout:
        st.error(
            "Image generation timed out."
        )
        return None

    except Exception as e:
        st.error(str(e))
        return None

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

            character = generate_character(
                genre,
                personality,
                powers
            )

            st.session_state.character = character

            image_prompt = (
                f"{genre} character portrait, "
                f"{personality}, "
                f"{powers}, "
                f"fantasy concept art, "
                f"cinematic lighting, "
                f"highly detailed, "
                f"masterpiece"
            )

            st.session_state.image = (
                generate_image(
                    image_prompt
                )
            )

            st.session_state.chat_history = []

# ------------------------
# MAIN
# ------------------------

st.title("🎭 CharacterForge AI")

st.caption(
    "Groq + Hugging Face SDXL Character Generator"
)

# ------------------------
# PROFILE
# ------------------------

if st.session_state.character:

    st.subheader(
        "📜 Character Profile"
    )

    col1, col2 = st.columns(
        [1, 2]
    )

    with col1:

        if st.session_state.image:

            st.image(
                st.session_state.image,
                caption="🎨 AI Character Portrait",
                use_container_width=True
            )

        else:

            st.warning(
                "Image generation failed."
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
    # CHAT
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
            ("user", user_input)
        )

        with st.spinner(
            "Character is thinking..."
        ):

            response = chat_with_character(
                st.session_state.character,
                user_input
            )

        st.session_state.chat_history.append(
            ("assistant", response)
        )

        st.rerun()

else:

    st.info(
        "Create a character from the sidebar to begin."
    )

import requests

try:
    r = requests.get(
        "https://api-inference.huggingface.co",
        timeout=20
    )

    st.write("HF Reachable")
    st.write(r.status_code)

except Exception as e:
    st.error(f"HF Test Failed: {e}")
