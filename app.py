import os
import time
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

HF_API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"

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
# CHARACTER GENERATION
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
# IMAGE GENERATION (SAFE + DEBUG)
# ------------------------

def generate_image(prompt_text):

    payload = {"inputs": prompt_text}

    st.write("HF API:", HF_API_URL)
    st.write("HF Token Loaded:", bool(HF_TOKEN))

    for attempt in range(3):

        try:
            response = requests.post(
                HF_API_URL,
                headers=headers,
                json=payload,
                timeout=90
            )

        except requests.exceptions.ConnectionError:
            st.error("❌ ConnectionError: Hugging Face unreachable")
            return None

        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
            return None

        # ------------------------
        # DEBUG OUTPUT
        # ------------------------
        st.write("STATUS CODE:", response.status_code)

        try:
            st.write("RESPONSE TEXT (preview):", str(response.text)[:200])
        except:
            st.write("RESPONSE TEXT: binary data")

        # ------------------------
        # SUCCESS
        # ------------------------
        if response.status_code == 200:
            try:
                return Image.open(BytesIO(response.content))
            except:
                st.error("Failed to decode image")
                return None

        # ------------------------
        # MODEL LOADING
        # ------------------------
        if response.status_code == 503:
            st.warning("Model loading... retrying")
            time.sleep(5)
            continue

        # ------------------------
        # AUTH ERROR
        # ------------------------
        if response.status_code == 401:
            st.error("Invalid HF token")
            return None

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

            st.session_state.character = generate_character(
                genre, personality, powers
            )

            image_prompt = (
                f"{genre} fantasy warrior, "
                f"{personality}, "
                f"{powers}, cinematic lighting, ultra detailed"
            )

            st.session_state.image = generate_image(image_prompt)

            st.session_state.chat_history = []


# ------------------------
# MAIN UI
# ------------------------

st.title("🎭 CharacterForge AI")
st.caption("Groq + Hugging Face Debug Mode Enabled")


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
            st.warning("Image failed (check HF logs above)")

    with col2:
        st.markdown(st.session_state.character)

    st.download_button(
        "📥 Download Character",
        st.session_state.character,
        file_name="character.txt"
    )

    st.divider()

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
