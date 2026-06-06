import chromadb
from datetime import datetime
import json

# Initialize ChromaDB client
chroma_client = chromadb.Client()

def get_or_create_collection(character_name):
    """Get or create a collection for character memory."""
    collection_name = f"character_{character_name.lower().replace(' ', '_')}"
    return chroma_client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

def store_memory(character_name, memory_type, content):
    """
    Store a memory for a character.
    
    Args:
        character_name: Name of the character
        memory_type: Type of memory (conversation, preference, event, relationship)
        content: The memory content
    """
    collection = get_or_create_collection(character_name)
    
    memory_data = {
        "type": memory_type,
        "content": content,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    collection.add(
        documents=[content],
        metadatas=[memory_data],
        ids=[f"{memory_type}_{datetime.utcnow().timestamp()}"]
    )

def retrieve_memories(character_name, query, n_results=5):
    """
    Retrieve relevant memories for a character.
    
    Args:
        character_name: Name of the character
        query: Search query
        n_results: Number of memories to retrieve
    
    Returns:
        List of relevant memories
    """
    try:
        collection = get_or_create_collection(character_name)
        results = collection.query(
            query_texts=[query],
            n_results=min(n_results, 5)
        )
        
        memories = []
        if results and results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                memory = {
                    "content": doc,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {}
                }
                memories.append(memory)
        
        return memories
    except:
        return []

def get_all_memories(character_name):
    """Get all memories for a character."""
    try:
        collection = get_or_create_collection(character_name)
        results = collection.get()
        
        memories = []
        if results and results['documents']:
            for i, doc in enumerate(results['documents']):
                memory = {
                    "content": doc,
                    "metadata": results['metadatas'][i] if results['metadatas'] else {}
                }
                memories.append(memory)
        
        return memories
    except:
        return []

def clear_memories(character_name):
    """Clear all memories for a character."""
    try:
        collection_name = f"character_{character_name.lower().replace(' ', '_')}"
        chroma_client.delete_collection(name=collection_name)
        return True
    except:
        return False

def format_memories_for_context(memories):
    """Format memories into a context string for the AI."""
    if not memories:
        return ""
    
    context = "\n**Previous Interactions & Memory:**\n"
    for memory in memories:
        if isinstance(memory, dict) and 'content' in memory:
            context += f"- {memory['content']}\n"
        else:
            context += f"- {memory}\n"
    
    return context
