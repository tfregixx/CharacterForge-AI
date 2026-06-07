import os
import time
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

HF_TOKEN = os.getenv("HF_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

# Hugging Face SDXL endpoint
HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

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
# IMAGE GENERATION (HUGGING FACE FIXED)
# ------------------------

def generate_image(prompt_text):

    payload = {"inputs": prompt_text}

    for attempt in range(3):  # retry system

        response = requests.post(
            HF_API_URL,
            headers=headers,
            json=payload,
            timeout=90
        )

        # ✅ success
        if response.status_code == 200:
            try:
                return Image.open(BytesIO(response.content))
            except:
                return None

        # ⏳ model loading
        if response.status_code == 503:
            time.sleep(5)
            continue

        # ❌ invalid token
        if response.status_code == 401:
            st.error("HF Token invalid or missing")
            return None

        # ❌ other errors
        st.warning(f"HF error: {response.status_code}")
        return None

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

            character = generate_character(genre, personality, powers)
            st.session_state.character = character

            # 🔥 SIMPLE SAFE IMAGE PROMPT (IMPORTANT)
            image_prompt = (
                f"{genre} fantasy warrior, "
                f"{personality}, "
                f"{powers}, "
                f"cinematic lighting, ultra detailed"
            )

            st.session_state.image = generate_image(image_prompt)

            st.session_state.chat_history = []


# ------------------------
# MAIN UI
# ------------------------

st.title("🎭 CharacterForge AI")
st.caption("Groq + Hugging Face SDXL Character Generator")


# ------------------------
# DISPLAY
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
            st.warning("Image generation failed (HF is loading or rate limited)")

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
