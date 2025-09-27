"""
Simple FastAPI application for healthcare community platform.
This is a minimal version without complex internationalization features.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os

# Create FastAPI app
app = FastAPI(
    title="Healthcare Community Platform",
    description="A platform for supporting people with serious illnesses",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class HealthCheck(BaseModel):
    status: str
    message: str

class PostCreate(BaseModel):
    title: str
    content: str
    group_id: int

class PostRead(BaseModel):
    id: int
    title: str
    content: str
    group_id: int
    created_at: str

# Routes
@app.get("/", response_model=HealthCheck)
async def root():
    """Root endpoint."""
    return HealthCheck(status="ok", message="Healthcare Community Platform API")

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint."""
    return HealthCheck(status="healthy", message="API is running")

@app.get("/api/status", response_model=HealthCheck)
async def api_status():
    """API status endpoint."""
    return HealthCheck(status="active", message="API is active and ready")

# Simple in-memory storage for demo
posts_storage = []
post_id_counter = 1

@app.post("/api/posts", response_model=PostRead)
async def create_post(post: PostCreate):
    """Create a new post."""
    global post_id_counter
    
    new_post = {
        "id": post_id_counter,
        "title": post.title,
        "content": post.content,
        "group_id": post.group_id,
        "created_at": "2024-01-01T00:00:00Z"
    }
    
    posts_storage.append(new_post)
    post_id_counter += 1
    
    return PostRead(**new_post)

@app.get("/api/posts", response_model=List[PostRead])
async def get_posts():
    """Get all posts."""
    return [PostRead(**post) for post in posts_storage]

@app.get("/api/posts/{post_id}", response_model=PostRead)
async def get_post(post_id: int):
    """Get a specific post."""
    for post in posts_storage:
        if post["id"] == post_id:
            return PostRead(**post)
    
    raise HTTPException(status_code=404, detail="Post not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
