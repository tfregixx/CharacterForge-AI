from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, MetaData, Table, select, Boolean, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
from enum import Enum
import os
from typing import Optional

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///characters.db")

# Auto-configure for PostgreSQL
if "postgresql" in DATABASE_URL:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ==================== User Models ====================

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    characters = relationship("Character", back_populates="user")
    chats = relationship("ChatHistory", back_populates="user")
    analytics = relationship("Analytics", back_populates="user")


# ==================== Character Models ====================

class Character(Base):
    __tablename__ = "characters"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    name = Column(String, index=True)
    genre = Column(String)
    content = Column(Text)
    current_version = Column(Integer, default=1)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="characters")
    versions = relationship("CharacterVersion", back_populates="character", cascade="all, delete-orphan")
    relationships = relationship("CharacterRelationship", back_populates="character", foreign_keys="[CharacterRelationship.character_id]")
    related_to = relationship("CharacterRelationship", back_populates="related_character", foreign_keys="[CharacterRelationship.related_character_id]")
    lore = relationship("LoreEntry", back_populates="character", cascade="all, delete-orphan")
    analytics = relationship("Analytics", back_populates="character")


class CharacterVersion(Base):
    __tablename__ = "character_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), index=True)
    version = Column(Integer)
    content = Column(Text)
    changes = Column(String)  # Description of changes
    created_at = Column(DateTime, default=datetime.utcnow)
    
    character = relationship("Character", back_populates="versions")


class CharacterRelationship(Base):
    __tablename__ = "character_relationships"
    
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), index=True)
    related_character_id = Column(Integer, ForeignKey("characters.id"), index=True)
    relationship_type = Column(String)  # friend, enemy, family, guild, kingdom
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    character = relationship("Character", back_populates="relationships", foreign_keys=[character_id])
    related_character = relationship("Character", back_populates="related_to", foreign_keys=[related_character_id])


# ==================== Lore & Knowledge Models ====================

class LoreEntry(Base):
    __tablename__ = "lore_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), index=True)
    lore_type = Column(String)  # world_history, city, kingdom, artifact, war, etc.
    title = Column(String)
    content = Column(Text)
    embedding_vector = Column(String)  # Store as JSON string for ChromaDB integration
    created_at = Column(DateTime, default=datetime.utcnow)
    
    character = relationship("Character", back_populates="lore")


# ==================== Chat & Interaction Models ====================

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), index=True)
    role = Column(String)  # user, assistant
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="chats")


# ==================== Analytics Models ====================

class Analytics(Base):
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=True, index=True)
    event_type = Column(String)  # character_view, character_chat, character_created, character_exported
    metadata = Column(String)  # JSON string with additional data
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="analytics")
    character = relationship("Character", back_populates="analytics")


# Create all tables
Base.metadata.create_all(bind=engine)


# ==================== Database Functions ====================

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# User Functions
def create_user(username: str, email: str, password_hash: str, is_admin: bool = False):
    """Create a new user."""
    session = SessionLocal()
    try:
        user = User(username=username, email=email, password_hash=password_hash, is_admin=is_admin)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except Exception as e:
        session.rollback()
        return None
    finally:
        session.close()


def get_user_by_username(username: str) -> Optional[User]:
    """Get user by username."""
    session = SessionLocal()
    try:
        return session.query(User).filter(User.username == username).first()
    finally:
        session.close()


def get_user_by_email(email: str) -> Optional[User]:
    """Get user by email."""
    session = SessionLocal()
    try:
        return session.query(User).filter(User.email == email).first()
    finally:
        session.close()


# Character Functions
def save_character(user_id: int, name: str, genre: str, content: str):
    """Save a new character."""
    session = SessionLocal()
    try:
        character = Character(user_id=user_id, name=name, genre=genre, content=content)
        session.add(character)
        session.commit()
        session.refresh(character)
        
        # Create initial version
        version = CharacterVersion(character_id=character.id, version=1, content=content, changes="Initial version")
        session.add(version)
        session.commit()
        
        return character
    except Exception as e:
        session.rollback()
        return None
    finally:
        session.close()


def get_user_characters(user_id: int):
    """Get all characters for a user."""
    session = SessionLocal()
    try:
        characters = session.query(Character).filter(Character.user_id == user_id).all()
        return [
            {
                "id": char.id,
                "name": char.name,
                "genre": char.genre,
                "content": char.content,
                "version": char.current_version,
                "created_at": char.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "is_public": char.is_public
            }
            for char in characters
        ]
    finally:
        session.close()


def get_character(char_id: int):
    """Get a specific character."""
    session = SessionLocal()
    try:
        character = session.query(Character).filter(Character.id == char_id).first()
        if character:
            return {
                "id": character.id,
                "user_id": character.user_id,
                "name": character.name,
                "genre": character.genre,
                "content": character.content,
                "version": character.current_version,
                "created_at": character.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "is_public": character.is_public
            }
        return None
    finally:
        session.close()


def delete_character(char_id: int):
    """Delete a character."""
    session = SessionLocal()
    try:
        character = session.query(Character).filter(Character.id == char_id).first()
        if character:
            session.delete(character)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        return False
    finally:
        session.close()


def search_characters(query: str, public_only: bool = True):
    """Search characters."""
    session = SessionLocal()
    try:
        q = session.query(Character).filter(
            (Character.name.ilike(f"%{query}%")) | 
            (Character.genre.ilike(f"%{query}%"))
        )
        if public_only:
            q = q.filter(Character.is_public == True)
        
        characters = q.all()
        return [
            {
                "id": char.id,
                "name": char.name,
                "genre": char.genre,
                "created_at": char.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for char in characters
        ]
    finally:
        session.close()


# Character Version Functions
def save_character_version(character_id: int, content: str, changes: str):
    """Save a new version of a character."""
    session = SessionLocal()
    try:
        character = session.query(Character).filter(Character.id == character_id).first()
        if not character:
            return None
        
        new_version_num = character.current_version + 1
        version = CharacterVersion(
            character_id=character_id,
            version=new_version_num,
            content=content,
            changes=changes
        )
        session.add(version)
        
        # Update character
        character.content = content
        character.current_version = new_version_num
        character.updated_at = datetime.utcnow()
        
        session.commit()
        session.refresh(version)
        return version
    except Exception as e:
        session.rollback()
        return None
    finally:
        session.close()


def get_character_versions(character_id: int):
    """Get all versions of a character."""
    session = SessionLocal()
    try:
        versions = session.query(CharacterVersion).filter(
            CharacterVersion.character_id == character_id
        ).all()
        return [
            {
                "id": v.id,
                "version": v.version,
                "content": v.content,
                "changes": v.changes,
                "created_at": v.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            for v in versions
        ]
    finally:
        session.close()


def get_character_version(character_id: int, version_num: int):
    """Get a specific version of a character."""
    session = SessionLocal()
    try:
        version = session.query(CharacterVersion).filter(
            CharacterVersion.character_id == character_id,
            CharacterVersion.version == version_num
        ).first()
        if version:
            return {
                "version": version.version,
                "content": version.content,
                "changes": version.changes,
                "created_at": version.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
        return None
    finally:
        session.close()


# Character Relationship Functions
def add_relationship(character_id: int, related_character_id: int, relationship_type: str, description: str = ""):
    """Add a relationship between characters."""
    session = SessionLocal()
    try:
        rel = CharacterRelationship(
            character_id=character_id,
            related_character_id=related_character_id,
            relationship_type=relationship_type,
            description=description
        )
        session.add(rel)
        session.commit()
        session.refresh(rel)
        return rel
    except Exception as e:
        session.rollback()
        return None
    finally:
        session.close()


def get_character_relationships(character_id: int):
    """Get all relationships for a character."""
    session = SessionLocal()
    try:
        relationships = session.query(CharacterRelationship).filter(
            CharacterRelationship.character_id == character_id
        ).all()
        return [
            {
                "id": rel.id,
                "related_character_id": rel.related_character_id,
                "related_character_name": rel.related_character.name if rel.related_character else "Unknown",
                "relationship_type": rel.relationship_type,
                "description": rel.description
            }
            for rel in relationships
        ]
    finally:
        session.close()


# Analytics Functions
def log_event(user_id: int, event_type: str, character_id: int = None, metadata: str = ""):
    """Log an analytics event."""
    session = SessionLocal()
    try:
        event = Analytics(
            user_id=user_id,
            character_id=character_id,
            event_type=event_type,
            metadata=metadata
        )
        session.add(event)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        return False
    finally:
        session.close()


def get_analytics(days: int = 30):
    """Get analytics data."""
    from datetime import timedelta
    
    session = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(days=days)
        events = session.query(Analytics).filter(Analytics.created_at >= cutoff).all()
        
        return {
            "total_events": len(events),
            "character_views": len([e for e in events if e.event_type == "character_view"]),
            "character_chats": len([e for e in events if e.event_type == "character_chat"]),
            "characters_created": len([e for e in events if e.event_type == "character_created"]),
            "characters_exported": len([e for e in events if e.event_type == "character_exported"]),
        }
    finally:
        session.close()


# Lore Functions
def save_lore_entry(character_id: int, lore_type: str, title: str, content: str):
    """Save a lore entry."""
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
        return entry
    except Exception as e:
        session.rollback()
        return None
    finally:
        session.close()


def get_character_lore(character_id: int):
    """Get all lore entries for a character."""
    session = SessionLocal()
    try:
        lore = session.query(LoreEntry).filter(LoreEntry.character_id == character_id).all()
        return [
            {
                "id": entry.id,
                "type": entry.lore_type,
                "title": entry.title,
                "content": entry.content,
                "created_at": entry.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            for entry in lore
        ]
    finally:
        session.close()
