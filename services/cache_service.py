import redis
import json
import os
import sys
from typing import Optional, Any

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    REDIS_AVAILABLE = True
except:
    REDIS_AVAILABLE = False
    redis_client = None

# Cache TTL (Time To Live) in seconds
CACHE_TTL = {
    "character": 3600,  # 1 hour
    "chat_response": 1800,  # 30 minutes
    "search_results": 900,  # 15 minutes
    "lore": 3600,  # 1 hour
    "user_profile": 600,  # 10 minutes
    "analytics": 300,  # 5 minutes
}

def cache_key(prefix: str, identifier: str) -> str:
    """Generate a cache key."""
    return f"{prefix}:{identifier}"

def set_cache(key: str, value: Any, ttl: int = 3600, prefix: str = "cache") -> bool:
    """Set a cache value."""
    if not REDIS_AVAILABLE:
        return False
    
    try:
        full_key = cache_key(prefix, key)
        redis_client.setex(
            full_key,
            ttl,
            json.dumps(value) if not isinstance(value, str) else value
        )
        return True
    except:
        return False

def get_cache(key: str, prefix: str = "cache") -> Optional[Any]:
    """Get a cache value."""
    if not REDIS_AVAILABLE:
        return None
    
    try:
        full_key = cache_key(prefix, key)
        value = redis_client.get(full_key)
        if value:
            try:
                return json.loads(value)
            except:
                return value
        return None
    except:
        return None

def delete_cache(key: str, prefix: str = "cache") -> bool:
    """Delete a cache value."""
    if not REDIS_AVAILABLE:
        return False
    
    try:
        full_key = cache_key(prefix, key)
        redis_client.delete(full_key)
        return True
    except:
        return False

def clear_cache_prefix(prefix: str) -> bool:
    """Clear all cache entries with a specific prefix."""
    if not REDIS_AVAILABLE:
        return False
    
    try:
        pattern = f"{prefix}:*"
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
        return True
    except:
        return False

# Specific cache functions

def cache_character(character_id: int, character_data: dict) -> bool:
    """Cache character data."""
    return set_cache(
        f"char_{character_id}",
        character_data,
        ttl=CACHE_TTL["character"],
        prefix="character"
    )

def get_cached_character(character_id: int) -> Optional[dict]:
    """Get cached character data."""
    return get_cache(f"char_{character_id}", prefix="character")

def cache_chat_response(conversation_id: str, response: str) -> bool:
    """Cache chat response."""
    return set_cache(
        f"response_{conversation_id}",
        response,
        ttl=CACHE_TTL["chat_response"],
        prefix="chat"
    )

def get_cached_chat_response(conversation_id: str) -> Optional[str]:
    """Get cached chat response."""
    return get_cache(f"response_{conversation_id}", prefix="chat")

def cache_search_results(query: str, results: list) -> bool:
    """Cache search results."""
    query_hash = hash(query) % ((sys.maxsize + 1) * 2)
    return set_cache(
        f"search_{query_hash}",
        results,
        ttl=CACHE_TTL["search_results"],
        prefix="search"
    )

def get_cached_search_results(query: str) -> Optional[list]:
    """Get cached search results."""
    query_hash = hash(query) % ((sys.maxsize + 1) * 2)
    return get_cache(f"search_{query_hash}", prefix="search")

def cache_user_profile(user_id: int, profile_data: dict) -> bool:
    """Cache user profile."""
    return set_cache(
        f"user_{user_id}",
        profile_data,
        ttl=CACHE_TTL["user_profile"],
        prefix="user"
    )

def get_cached_user_profile(user_id: int) -> Optional[dict]:
    """Get cached user profile."""
    return get_cache(f"user_{user_id}", prefix="user")

def invalidate_character_cache(character_id: int) -> bool:
    """Invalidate character cache."""
    return delete_cache(f"char_{character_id}", prefix="character")

def invalidate_user_cache(user_id: int) -> bool:
    """Invalidate user profile cache."""
    return delete_cache(f"user_{user_id}", prefix="user")

def get_cache_stats() -> dict:
    """Get cache statistics."""
    if not REDIS_AVAILABLE:
        return {"available": False}
    
    try:
        info = redis_client.info()
        return {
            "available": True,
            "connected_clients": info.get("connected_clients", 0),
            "used_memory": info.get("used_memory_human", "N/A"),
            "total_keys": len(redis_client.keys("*"))
        }
    except:
        return {"available": False}
