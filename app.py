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
# POLLINATIONS IMAGE (STABLE)
# ------------------------

def generate_character_image_url(genre, personality, powers):

    prompt = (
        f"{genre} dark fantasy character portrait, "
        f"{personality}, "
        f"{powers}, "
        f"cinematic lighting, ultra detailed face, digital painting"
    )

    encoded = urllib.parse.quote_plus(prompt)

    return (
        "https://image.pollinations.ai/prompt/"
        f"{encoded}?model=flux&width=512&height=512&nologo=true"
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

            st.session_state.character = generate_character(
                genre,
                personality,
                powers
            )

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
st.caption("Groq + Pollinations AI (Fully Stable Rendering Mode)")


# ------------------------
# DISPLAY CHARACTER
# ------------------------

if st.session_state.character:

    st.subheader("📜 Character Profile")

    col1, col2 = st.columns([1, 2])

    with col1:

        fallback = (
            "https://api.dicebear.com/9.x/adventurer/png"
            f"?seed={urllib.parse.quote(st.session_state.character[:60])}"
        )

        img_url = st.session_state.image_url or fallback

        st.markdown(
            f"""
            <div style="display:flex; justify-content:center;">
                <img
                    src="{img_url}"
                    style="
                        width:100%;
                        max-width:420px;
                        border-radius:16px;
                        box-shadow:0px 10px 30px rgba(0,0,0,0.3);
                    "
                    onerror="this.onerror=null;this.src='{fallback}';"
                />
            </div>
            """,
            unsafe_allow_html=True
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
    # CHAT SECTION
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
        
