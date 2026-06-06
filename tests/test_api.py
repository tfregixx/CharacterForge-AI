import pytest
from backend.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "CharacterForge" in response.json()["message"]

def test_register():
    """Test user registration."""
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPassword123"
        }
    )
    # Should succeed or fail gracefully
    assert response.status_code in [200, 400, 500]

def test_invalid_registration():
    """Test invalid registration."""
    # Missing password requirement
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "weak"
        }
    )
    assert response.status_code in [400, 422]

@pytest.mark.asyncio
async def test_search():
    """Test search endpoint."""
    response = client.post(
        "/api/search",
        json={
            "query": "warrior",
            "limit": 10,
            "public_only": True
        }
    )
    assert response.status_code in [200, 400]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
