from sqlalchemy import text
from database.db import engine


def store_memory(character_name, memory):
    with engine.connect() as conn:
        conn.execute(
            text("""
            INSERT INTO memories
            (character_name, memory)
            VALUES
            (:character_name, :memory)
            """),
            {
                "character_name": character_name,
                "memory": memory
            }
        )
        conn.commit()


def retrieve_memories(character_name):
    with engine.connect() as conn:
        result = conn.execute(
            text("""
            SELECT memory
            FROM memories
            WHERE character_name=:character_name
            ORDER BY id DESC
            LIMIT 10
            """),
            {
                "character_name": character_name
            }
        )

        return [row[0] for row in result.fetchall()]


def format_memories_for_context(memories):
    if not memories:
        return ""

    return "\n".join(memories)


def clear_memories(character_name):
    with engine.connect() as conn:
        conn.execute(
            text("""
            DELETE FROM memories
            WHERE character_name=:character_name
            """),
            {
                "character_name": character_name
            }
        )
        conn.commit()
