import os
import base64
import requests
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

groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

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
# GROQ: CHARACTER GENERATION
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

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return str(response.choices[0].message.content)


# ------------------------
# GROQ: CHAT
# ------------------------

def chat_with_character(character, user_message):

    prompt = f"""
You are this character:

{character}

Stay fully in character.

User: {user_message}
"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return str(response.choices[0].message.content)


# ------------------------
# TOGETHER AI IMAGE
# ------------------------

def generate_image_together(prompt):

    url = "https://api.together.xyz/v1/images/generations"

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "stabilityai/stable-diffusion-xl-base-1.0",
        "prompt": prompt,
        "width": 1024,
        "height": 1024,
        "steps": 30,
        "n": 1
    }

    response = requests.post(url, headers=headers, json=payload)

    data = response.json()

    try:
        return data["data"][0]["url"]
    except:
        return None


def build_image_prompt(genre, personality, powers):

    return (
        f"{genre} fantasy character portrait, "
        f"{personality}, "
        f"{powers}, "
        f"ultra detailed, cinematic lighting, digital painting, masterpiece"
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

            character = generate_character(
                genre,
                personality,
                powers
            )

            st.session_state.character = character

            image_prompt = build_image_prompt(
                genre,
                personality,
                powers
            )

            image_url = generate_image_together(image_prompt)

            st.session_state.image = image_url

            st.session_state.chat_history = []


# ------------------------
# MAIN UI
# ------------------------

st.title("🎭 CharacterForge AI")
st.caption("Groq + Together AI powered character generator")

# ------------------------
# CHARACTER DISPLAY
# ------------------------

if st.session_state.character:

    st.subheader("📜 Character Profile")

    col1, col2 = st.columns([1, 2])

    with col1:

        if st.session_state.image:
            st.image(st.session_state.image, use_container_width=True)
        else:
            st.warning("Image generation failed")

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

