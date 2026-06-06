from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import os

# Import routes
from backend.routes.auth import router as auth_router

# Initialize FastAPI app
app = FastAPI(
    title="CharacterForge AI API",
    description="AI-powered character generation and interaction platform",
    version="2.0.0"
)

# ==================== CORS Configuration ====================
origins = [
    "http://localhost:3000",
    "http://localhost:8501",
    "http://localhost:8502",
    os.getenv("FRONTEND_URL", "http://localhost:3000"),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Routes ====================
app.include_router(auth_router, prefix="/api", tags=["auth"])

# ==================== Health Check ====================
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "service": "CharacterForge AI"
    }

# ==================== OpenAPI Documentation ====================
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="CharacterForge AI API",
        version="2.0.0",
        description="AI-powered character generation and interaction API",
        routes=app.routes,
    )
    
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# ==================== Root ====================
@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "message": "CharacterForge AI API",
        "docs": "/docs",
        "version": "2.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
