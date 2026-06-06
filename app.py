import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

from services.character_generator import generate_character
from services.chat_service import chat_with_character
from services.memory_service import store_memory, retrieve_memories, format_memories_for_context, clear_memories
from services.image_generator import generate_character_image, create_placeholder_image, get_character_image
from services.export_service import export_to_json, export_to_txt, export_to_pdf, save_export
from database.db import save_character, get_characters, get_character, delete_character, search_characters

# Page configuration
st.set_page_config(
    page_title="CharacterForge AI",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #2c1b4e 0%, #1a0f3f 100%);
    }
    
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    h1 {
        color: #ff6b9d;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    h2 {
        color: #c44569;
    }
    
    .character-card {
        background: linear-gradient(135deg, #3d2466 0%, #2c1b4e 100%);
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #ff6b9d;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "current_character" not in st.session_state:
    st.session_state.current_character = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "search_query" not in st.session_state:
    st.session_state.search_query = ""

# Header
st.title("🎭 CharacterForge AI")
st.markdown("### Create, Chat, and Export Fantasy Characters")

# Sidebar - Character Gallery
st.sidebar.title("📚 Saved Characters")

# Search functionality
search_query = st.sidebar.text_input("🔍 Search characters", value=st.session_state.search_query)
st.session_state.search_query = search_query

if search_query:
    characters = search_characters(search_query)
else:
    characters = get_characters()

if characters:
    st.sidebar.markdown("---")
    for char in characters:
        col1, col2, col3 = st.sidebar.columns([3, 1, 1])
        
        with col1:
            if st.button(f"📖 {char['name']}", key=f"select_{char['id']}", use_container_width=True):
                st.session_state.current_character = char
                st.session_state.chat_history = []
                st.rerun()
        
        with col2:
            if st.button("👁️", key=f"view_{char['id']}", help="View"):
                st.session_state.current_character = char
                st.rerun()
        
        with col3:
            if st.button("🗑️", key=f"delete_{char['id']}", help="Delete"):
                delete_character(char['id'])
                st.session_state.current_character = None
                st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("**Statistics**")
st.sidebar.metric("Total Characters", len(characters))

# Main content area
if st.session_state.current_character is None:
    # Home/Creation tab
    tab1, tab2 = st.tabs(["🆕 Create Character", "📖 View Gallery"])
    
    with tab1:
        st.markdown("### Generate a New Character")
        
        col1, col2 = st.columns(2)
        
        with col1:
            genre = st.selectbox(
                "Select Genre",
                ["Fantasy", "Sci-Fi", "Horror", "Romance", "Mystery", "Adventure", "Custom"]
            )
            
            if genre == "Custom":
                genre_custom = st.text_input("Enter custom genre")
                genre = genre_custom if genre_custom else "Fantasy"
        
        with col2:
            character_type = st.selectbox(
                "Character Type",
                ["Warrior", "Mage", "Rogue", "Paladin", "Ranger", "Custom"]
            )
        
        prompt = st.text_area(
            "Describe your character (optional additional details)",
            placeholder="E.g., Dark elf with a mysterious past, skilled in shadow magic..."
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✨ Generate Character", use_container_width=True, type="primary"):
                with st.spinner("🎨 Generating character..."):
                    full_prompt = f"{genre} {character_type}. {prompt}" if prompt else f"{genre} {character_type}"
                    character_content = generate_character(full_prompt)
                    
                    # Extract name from content for better storage
                    char_name = f"{genre} {character_type}"
                    if "Name:" in character_content:
                        try:
                            name_line = [line for line in character_content.split("\n") if "Name:" in line][0]
                            char_name = name_line.split("Name:")[-1].strip()
                        except:
                            pass
                    
                    st.session_state.current_character = {
                        "id": None,
                        "name": char_name,
                        "genre": genre,
                        "content": character_content,
                        "created_at": "Just now"
                    }
                    
                    st.rerun()
        
        with col2:
            if st.button("🎲 Random Character", use_container_width=True):
                with st.spinner("🎨 Generating random character..."):
                    random_prompt = f"Create a unique {genre} {character_type} character with an interesting backstory"
                    character_content = generate_character(random_prompt)
                    char_name = f"{genre} {character_type} #{str(hash(character_content))[-4:]}"
                    
                    st.session_state.current_character = {
                        "id": None,
                        "name": char_name,
                        "genre": genre,
                        "content": character_content,
                        "created_at": "Just now"
                    }
                    
                    st.rerun()
    
    with tab2:
        st.markdown("### Character Gallery")
        
        if characters:
            cols = st.columns(2)
            for idx, char in enumerate(characters):
                with cols[idx % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {char['name']}")
                        st.markdown(f"**Genre:** {char['genre']}")
                        st.markdown(f"**Created:** {char['created_at']}")
                        
                        if st.button("View Full Character", key=f"gallery_view_{char['id']}", use_container_width=True):
                            st.session_state.current_character = char
                            st.rerun()

else:
    # Character detail view
    character = st.session_state.current_character
    
    # Tabs for different views
    tab_character, tab_chat, tab_export = st.tabs(["📋 Character", "💬 Chat", "📥 Export"])
    
    with tab_character:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"## {character['name']}")
            st.markdown(f"**Genre:** {character['genre']}")
            st.markdown(f"**Created:** {character['created_at']}")
            
            st.markdown("### Character Details")
            st.markdown(character['content'])
            
            # Save character if not already saved
            if character['id'] is None:
                if st.button("💾 Save Character to Database", use_container_width=True, type="primary"):
                    saved_char = save_character(
                        name=character['name'],
                        genre=character['genre'],
                        content=character['content']
                    )
                    st.success("✅ Character saved!")
                    st.session_state.current_character['id'] = saved_char.id
                    st.rerun()
        
        with col2:
            st.markdown("### Image Generation")
            
            image_path = get_character_image(character['name'])
            
            if image_path and os.path.exists(image_path):
                st.image(image_path, use_column_width=True)
                st.success("✅ Image generated")
            else:
                if st.button("🎨 Generate Portrait", use_container_width=True):
                    with st.spinner("Generating portrait (this may take a moment)..."):
                        image_path = generate_character_image(
                            character['content'],
                            character['name']
                        )
                        if image_path:
                            st.rerun()
                        else:
                            # Create placeholder if generation fails
                            placeholder = create_placeholder_image(character['name'])
                            st.info("Using placeholder image")
                            st.rerun()
    
    with tab_chat:
        st.markdown(f"### Chat with {character['name']}")
        
        # Clear chat button
        if st.button("🔄 Clear Chat History"):
            st.session_state.chat_history = []
            clear_memories(character['name'])
            st.rerun()
        
        # Display chat history
        st.markdown("---")
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f"**You:** {message['content']}")
            else:
                st.markdown(f"**{character['name']}:** {message['content']}")
            st.markdown("---")
        
        # Chat input
        user_input = st.chat_input("Say something to the character...")
        
        if user_input:
            with st.spinner(f"🤔 {character['name']} is thinking..."):
                # Store user message in history
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": user_input
                })
                
                # Store in memory
                store_memory(character['name'], "conversation", f"User: {user_input}")
                
                # Retrieve relevant memories for context
                memories = retrieve_memories(character['name'], user_input, n_results=3)
                memory_context = format_memories_for_context(memories)
                
                # Generate response with memory context
                enhanced_content = character['content'] + memory_context
                response = chat_with_character(
                    enhanced_content,
                    user_input,
                    st.session_state.chat_history[:-1]  # Exclude the latest user message
                )
                
                # Store response in memory
                store_memory(character['name'], "conversation", f"{character['name']}: {response}")
                
                # Add to chat history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response
                })
                
                st.rerun()
    
    with tab_export:
        st.markdown(f"### Export {character['name']}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Export as JSON", use_container_width=True):
                json_data = export_to_json(character)
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name=f"{character['name'].replace(' ', '_')}.json",
                    mime="application/json",
                    use_container_width=True
                )
        
        with col2:
            if st.button("📝 Export as TXT", use_container_width=True):
                txt_data = export_to_txt(character)
                st.download_button(
                    label="Download TXT",
                    data=txt_data,
                    file_name=f"{character['name'].replace(' ', '_')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        
        with col3:
            if st.button("📕 Export as PDF", use_container_width=True):
                pdf_data = export_to_pdf(character)
                if pdf_data:
                    st.download_button(
                        label="Download PDF",
                        data=pdf_data,
                        file_name=f"{character['name'].replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
    
    # Back button
    st.markdown("---")
    if st.button("← Back to Gallery", use_container_width=True):
        st.session_state.current_character = None
        st.rerun()

