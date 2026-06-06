import os
import urllib.parse
import requests
from PIL import Image
from io import BytesIO

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# ------------------------
# CONFIG
# ------------------------

st.set_page_config(
    page_title="CharacterForge AI",
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


# ------------------------
# SIDEBAR
# ------------------------

with st.sidebar:

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

        with st.spinner("Generating Character..."):

            st.session_state.character = generate_character(
                genre,
                personality,
                powers
            )

            st.session_state.chat_history = []

# ------------------------
# MAIN
# ------------------------

st.title("🎭 CharacterForge AI")
st.caption(
    "Generate, chat, and manage AI characters"
)

if st.session_state.character:

    st.subheader("Character Profile")

image_prompt = urllib.parse.quote(
    f"""
    {genre} character portrait,
    {personality},
    {powers},
    fantasy concept art,
    highly detailed face,
    cinematic lighting,
    professional digital painting,
    masterpiece,
    ultra realistic,
    4k
    """
)

image_url = (
    f"https://image.pollinations.ai/prompt/{image_prompt}"
    f"?width=512"
    f"&height=512"
    f"&model=flux"
)

col1, col2 = st.columns([1, 2])

with col1:

    try:

        response = requests.get(
            image_url,
            timeout=60
        )

        if response.status_code == 200:

            image = Image.open(
                BytesIO(response.content)
            )
st.write("Genre:", genre)
st.write("Personality:", personality)
st.write("Powers:", powers)

image_prompt = urllib.parse.quote(
f"{genre} character portrait, {personality}, {powers}"
)

image_url = (
f"https://image.pollinations.ai/prompt/{image_prompt}"
)

st.write(image_ur
            st.image(
                image,
                caption="🎨 AI Character Portrait",
                use_container_width=True
            )

        else:

            st.warning(
                "Portrait generation unavailable"
            )

    except Exception:

        st.warning(
            "Unable to load portrait"
        )

    with st.expander("Debug Image URL"):
        st.code(image_url)

with col2:

    st.markdown(
        st.session_state.character
    )

if st.session_state.character:

st.download_button(
    label="📥 Download Character",
    data=str(st.session_state.character),
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

    response = chat_with_character(
        st.session_state.character,
        user_input
    )

    st.session_state.chat_history.append(
        ("user", user_input)
    )

    st.session_state.chat_history.append(
        ("assistant", response)
    )

    st.rerun()


else:
    st.info(
        "Create a character from the sidebar to begin."
    )
