from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from database.db import (
    create_user, get_user_by_username, get_user_by_email, 
    get_user_characters, save_character, delete_character, search_characters
)
from services.auth_service import (
    hash_password, verify_password, create_access_token, 
    validate_username, validate_password, validate_email
)
from backend.models.schemas import (
    UserRegister, UserLogin, UserResponse, Token, 
    CharacterCreate, CharacterResponse, SearchRequest, SearchResult
)

router = APIRouter()

# ==================== Authentication Routes ====================

@router.post("/auth/register", response_model=UserResponse)
async def register(user_data: UserRegister):
    """Register a new user."""
    # Validate inputs
    if not validate_username(user_data.username):
        raise HTTPException(status_code=400, detail="Invalid username format")
    
    if not validate_password(user_data.password):
        raise HTTPException(
            status_code=400, 
            detail="Password must be at least 8 chars, include uppercase and number"
        )
    
    if not validate_email(user_data.email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    # Check if user exists
    if get_user_by_username(user_data.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    
    if get_user_by_email(user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    password_hash = hash_password(user_data.password)
    user = create_user(user_data.username, user_data.email, password_hash)
    
    if not user:
        raise HTTPException(status_code=500, detail="Failed to create user")
    
    return user

@router.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login user and return JWT token."""
    user = get_user_by_username(credentials.username)
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# ==================== Character Routes ====================

@router.post("/characters", response_model=CharacterResponse)
async def create_character(character_data: CharacterCreate, current_user: UserResponse = Depends(get_current_user)):
    """Create a new character."""
    character = save_character(
        current_user.id,
        character_data.name,
        character_data.genre,
        character_data.content
    )
    
    if not character:
        raise HTTPException(status_code=500, detail="Failed to create character")
    
    return character

@router.get("/characters", response_model=List[CharacterResponse])
async def list_characters(current_user: UserResponse = Depends(get_current_user)):
    """Get all characters for the current user."""
    characters = get_user_characters(current_user.id)
    return characters

@router.get("/characters/{character_id}", response_model=CharacterResponse)
async def get_character(character_id: int):
    """Get a specific character."""
    from database.db import get_character
    character = get_character(character_id)
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    return character

@router.delete("/characters/{character_id}")
async def delete_char(character_id: int, current_user: UserResponse = Depends(get_current_user)):
    """Delete a character."""
    from database.db import get_character
    character = get_character(character_id)
    
    if not character or character["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    if not delete_character(character_id):
        raise HTTPException(status_code=500, detail="Failed to delete character")
    
    return {"message": "Character deleted"}

# ==================== Search Routes ====================

@router.post("/search", response_model=List[SearchResult])
async def search(search_data: SearchRequest):
    """Search characters."""
    results = search_characters(search_data.query, search_data.public_only)
    return results[:search_data.limit]

# ==================== Helper ====================

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserResponse:
    """Get current user from token."""
    from services.auth_service import decode_token
    
    token_data = decode_token(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user_by_username(token_data["username"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return UserResponse.from_orm(user)

# OAuth2 scheme
from fastapi.security import HTTPBearer
oauth2_scheme = HTTPBearer()
