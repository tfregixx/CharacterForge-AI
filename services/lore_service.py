import chromadb
from sentence_transformers import SentenceTransformer
import json
from typing import List, Dict

# Initialize ChromaDB client for lore/RAG
chroma_client = chromadb.Client()

# Initialize sentence transformer for embeddings
try:
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
except:
    embedder = None

def get_or_create_lore_collection(character_id: int):
    """Get or create a lore collection for a character."""
    collection_name = f"lore_character_{character_id}"
    return chroma_client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

def store_lore_entry(character_id: int, lore_type: str, title: str, content: str):
    """
    Store a lore entry in ChromaDB.
    
    Args:
        character_id: Character ID
        lore_type: Type of lore (world_history, city, kingdom, artifact, war, character)
        title: Title of the lore entry
        content: Content of the lore entry
    """
    collection = get_or_create_lore_collection(character_id)
    
    lore_entry = {
        "type": lore_type,
        "title": title,
        "character_id": character_id,
        "timestamp": str(__import__('datetime').datetime.utcnow().isoformat())
    }
    
    entry_id = f"{lore_type}_{character_id}_{len(collection.get()['ids']) + 1}"
    
    collection.add(
        documents=[content],
        metadatas=[lore_entry],
        ids=[entry_id]
    )
    
    return entry_id

def query_lore(character_id: int, query: str, n_results: int = 5) -> List[Dict]:
    """
    Query the lore knowledge base using semantic search.
    
    Args:
        character_id: Character ID
        query: Search query
        n_results: Number of results to return
    
    Returns:
        List of relevant lore entries
    """
    try:
        collection = get_or_create_lore_collection(character_id)
        results = collection.query(
            query_texts=[query],
            n_results=min(n_results, 5)
        )
        
        lore_entries = []
        if results and results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                entry = {
                    "content": doc,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {}
                }
                lore_entries.append(entry)
        
        return lore_entries
    except:
        return []

def get_all_lore(character_id: int) -> List[Dict]:
    """Get all lore entries for a character."""
    try:
        collection = get_or_create_lore_collection(character_id)
        results = collection.get()
        
        lore_entries = []
        if results and results['documents']:
            for i, doc in enumerate(results['documents']):
                entry = {
                    "content": doc,
                    "metadata": results['metadatas'][i] if results['metadatas'] else {}
                }
                lore_entries.append(entry)
        
        return lore_entries
    except:
        return []

def format_lore_for_context(lore_entries: List[Dict]) -> str:
    """Format lore entries into context string."""
    if not lore_entries:
        return ""
    
    context = "\n**World Knowledge & Lore:**\n"
    for entry in lore_entries:
        if isinstance(entry, dict) and 'content' in entry:
            title = entry.get('metadata', {}).get('title', 'Entry')
            context += f"- **{title}**: {entry['content']}\n"
        else:
            context += f"- {entry}\n"
    
    return context

def clear_lore(character_id: int) -> bool:
    """Clear all lore for a character."""
    try:
        collection_name = f"lore_character_{character_id}"
        chroma_client.delete_collection(name=collection_name)
        return True
    except:
        return False

def build_rag_context(character_id: int, user_query: str) -> str:
    """
    Build RAG context by retrieving relevant lore for a query.
    
    Args:
        character_id: Character ID
        user_query: User's question/query
    
    Returns:
        Formatted context string
    """
    lore_entries = query_lore(character_id, user_query, n_results=5)
    return format_lore_for_context(lore_entries)
