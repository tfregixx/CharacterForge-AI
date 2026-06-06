import streamlit as st
from dotenv import load_dotenv

from services.character_generator import generate_character
from services.chat_service import chat_with_character
from services.memory_service import (
    store_memory,
    retrieve_memories,
    clear_memories,
    format_memories_for_context
)

load_dotenv()

st.set_page_config(
    page_title="CharacterForge AI",
    page_icon="🎭",
    layout="wide"
)

st.title("🎭 CharacterForge AI")
st.caption("Generate, chat, and build fictional AI characters")

# Session State
if "character" not in st.session_state:
    st.session_state.character = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar
with st.sidebar:
    st.header("Create Character")

    genre = st.selectbox(
        "Genre",
        ["Fantasy", "Sci-Fi", "Anime", "Cyberpunk"]
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

        prompt = f"""
        Genre: {genre}
        Personality: {personality}
        Powers: {powers}

        Generate:
        Name
        Age
        Backstory
        Strengths
        Weaknesses
        Catchphrase
        """

        character = generate_character(prompt)

        st.session_state.character = character
        st.session_state.chat_history = []

        st.success("Character Generated!")

# Main Content
if st.session_state.character:

    st.subheader("Character Profile")

    st.markdown(st.session_state.character)

    st.divider()

    st.subheader("Chat with Character")

    user_input = st.chat_input(
        "Talk to your character..."
    )

    for role, message in st.session_state.chat_history:

        with st.chat_message(role):
            st.markdown(message)

    if user_input:

        character_name = "Character"

        memories = retrieve_memories(character_name)

        memory_context = format_memories_for_context(
            memories
        )

        response = chat_with_character(
            character_profile=st.session_state.character,
            memory_context=memory_context,
            user_message=user_input
        )

        store_memory(
            character_name,
            f"User: {user_input}"
        )

        store_memory(
            character_name,
            f"AI: {response}"
        )

        st.session_state.chat_history.append(
            ("user", user_input)
        )

        st.session_state.chat_history.append(
            ("assistant", response)
        )

        st.rerun()

    if st.button("Clear Memory"):

        clear_memories("Character")

        st.session_state.chat_history = []

        st.success("Memory Cleared")

else:

    st.info(
        "Create a character from the sidebar to begin."
    )
