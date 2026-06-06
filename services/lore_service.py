from sqlalchemy import or_
from database.db import SessionLocal, LoreEntry
from typing import List, Dict


def store_lore_entry(character_id: int, lore_type: str, title: str, content: str):
    """
    Store a lore entry in the relational database.
    """
    session = SessionLocal()
    try:
        entry = LoreEntry(
            character_id=character_id,
            lore_type=lore_type,
            title=title,
            content=content
        )
        session.add(entry)
        session.commit()
        session.refresh(entry)
        return entry.id
    except Exception:
        session.rollback()
        return None
    finally:
        session.close()


def query_lore(character_id: int, query: str, n_results: int = 5) -> List[Dict]:
    """
    Query lore entries by title or content matching the query.
    """
    session = SessionLocal()
    try:
        results = (
            session.query(LoreEntry)
            .filter(
                LoreEntry.character_id == character_id,
                or_(LoreEntry.content.contains(query), LoreEntry.title.contains(query))
            )
            .order_by(LoreEntry.created_at.desc())
            .limit(n_results)
            .all()
        )
        return [
            {
                "content": entry.content,
                "metadata": {
                    "title": entry.title,
                    "type": entry.lore_type,
                    "created_at": entry.created_at.isoformat()
                }
            }
            for entry in results
        ]
    finally:
        session.close()


def get_all_lore(character_id: int) -> List[Dict]:
    """Get all lore entries for a character."""
    session = SessionLocal()
    try:
        results = (
            session.query(LoreEntry)
            .filter(LoreEntry.character_id == character_id)
            .order_by(LoreEntry.created_at.desc())
            .all()
        )
        return [
            {
                "content": entry.content,
                "metadata": {
                    "title": entry.title,
                    "type": entry.lore_type,
                    "created_at": entry.created_at.isoformat()
                }
            }
            for entry in results
        ]
    finally:
        session.close()


def format_lore_for_context(lore_entries: List[Dict]) -> str:
    """Format lore entries into context string."""
    if not lore_entries:
        return ""

    context = "\n**World Knowledge & Lore:**\n"
    for entry in lore_entries:
        title = entry.get("metadata", {}).get("title", "Entry")
        context += f"- **{title}**: {entry['content']}\n"
    return context


def clear_lore(character_id: int) -> bool:
    """Clear all lore entries for a character."""
    session = SessionLocal()
    try:
        session.query(LoreEntry).filter(LoreEntry.character_id == character_id).delete()
        session.commit()
        return True
    except Exception:
        session.rollback()
        return False
    finally:
        session.close()


def build_rag_context(character_id: int, user_query: str) -> str:
    """
    Build RAG context by retrieving relevant lore for a query.
    """
    lore_entries = query_lore(character_id, user_query, n_results=5)
    return format_lore_for_context(lore_entries)
