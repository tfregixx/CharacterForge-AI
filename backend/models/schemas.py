from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# ==================== User Models ====================

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    class Config:
        schema_extra = {
            "example": {
                "username": "kael_warrior",
                "email": "kael@example.com",
                "password": "SecurePass123"
            }
        }

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== Character Models ====================

class CharacterCreate(BaseModel):
    name: str
    genre: str
    content: str
    is_public: bool = False

class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    genre: Optional[str] = None
    content: Optional[str] = None
    is_public: Optional[bool] = None
    changes: str = ""  # For version tracking

class CharacterResponse(BaseModel):
    id: int
    user_id: int
    name: str
    genre: str
    content: str
    version: int
    is_public: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class CharacterDetailResponse(CharacterResponse):
    versions: List['CharacterVersionResponse'] = []
    relationships: List['RelationshipResponse'] = []

# ==================== Character Version Models ====================

class CharacterVersionResponse(BaseModel):
    id: int
    version: int
    content: str
    changes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== Relationship Models ====================

class RelationshipCreate(BaseModel):
    related_character_id: int
    relationship_type: str = Field(..., pattern="^(friend|enemy|family|guild|kingdom)$")
    description: Optional[str] = None

class RelationshipResponse(BaseModel):
    id: int
    related_character_id: int
    related_character_name: str
    relationship_type: str
    description: Optional[str]
    
    class Config:
        from_attributes = True

# ==================== Lore Models ====================

class LoreEntryCreate(BaseModel):
    lore_type: str = Field(..., pattern="^(world_history|city|kingdom|artifact|war|character|other)$")
    title: str
    content: str

class LoreEntryResponse(BaseModel):
    id: int
    type: str
    title: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== Chat Models ====================

class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str

class ChatRequest(BaseModel):
    message: str
    character_id: int

class ChatResponse(BaseModel):
    role: str
    content: str
    timestamp: datetime

# ==================== Analytics Models ====================

class AnalyticsResponse(BaseModel):
    total_events: int
    character_views: int
    character_chats: int
    characters_created: int
    characters_exported: int

# ==================== Token Models ====================

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None

# ==================== Search Models ====================

class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    public_only: bool = True

class SearchResult(BaseModel):
    id: int
    name: str
    genre: str
    created_at: datetime
