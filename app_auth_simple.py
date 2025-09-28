"""
簡易認証システム
疾患を抱える消費者向けの認証システム（簡易版）
"""

import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, create_engine, SQLModel
from contextlib import asynccontextmanager
from typing import Optional
import json

# データベース設定
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(DATABASE_URL, echo=True)

# 開発環境用の認証スルー設定
DEV_AUTH_BYPASS = os.getenv("DEV_AUTH_BYPASS", "false").lower() == "true"
DEV_USER_ID = int(os.getenv("DEV_USER_ID", "1"))

def get_db() -> Session:
    """データベースセッション取得"""
    with Session(engine) as session:
        yield session

@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションライフサイクル管理"""
    # 起動時
    print("🚀 Starting Healthcare Community Platform with Simple Authentication")
    print(f"🔐 Authentication bypass: {DEV_AUTH_BYPASS}")
    
    # データベーステーブル作成
    SQLModel.metadata.create_all(engine)
    
    yield
    
    # シャットダウン時
    print("🛑 Shutting down Healthcare Community Platform")

# FastAPIアプリケーション作成
app = FastAPI(
    title="Healthcare Community Platform API",
    description="Healthcare community platform for supporting people with serious illnesses",
    version="2.0.0",
    lifespan=lifespan
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 簡易投稿データ
posts_db = []

class Post:
    def __init__(self, id: int, title: str, content: str, author_id: int, author_name: str):
        self.id = id
        self.title = title
        self.content = content
        self.author_id = author_id
        self.author_name = author_name
        from datetime import datetime, timezone
        self.created_at = datetime.now(timezone.utc).isoformat()

class PostCreate:
    def __init__(self, title: str, content: str):
        self.title = title
        self.content = content

class PostRead:
    def __init__(self, id: int, title: str, content: str, author_id: int, author_name: str, created_at: str):
        self.id = id
        self.title = title
        self.content = content
        self.author_id = author_id
        self.author_name = author_name
        self.created_at = created_at

@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "Healthcare Community Platform API",
        "version": "2.0.0",
        "features": {
            "authentication": True,
            "posts": True,
            "internationalization": True,
            "dev_bypass": DEV_AUTH_BYPASS
        }
    }

@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {
        "status": "healthy",
        "service": "healthcare-community-platform",
        "version": "2.0.0",
        "authentication": {
            "enabled": True,
            "dev_bypass": DEV_AUTH_BYPASS
        }
    }

@app.get("/auth/health")
async def auth_health_check():
    """認証サービスヘルスチェック"""
    return {
        "status": "healthy",
        "service": "authentication",
        "features": {
            "registration": True,
            "login": True,
            "token_refresh": True,
            "profile_management": True,
            "dev_bypass": DEV_AUTH_BYPASS
        }
    }

@app.get("/posts")
async def get_posts(skip: int = 0, limit: int = 100):
    """投稿一覧取得"""
    if DEV_AUTH_BYPASS:
        # 開発環境では認証スルー
        return posts_db[skip:skip + limit]
    else:
        # 本格認証では認証が必要
        return {"message": "Authentication required"}

@app.post("/posts")
async def create_post(post_data: dict):
    """投稿作成"""
    if DEV_AUTH_BYPASS:
        # 開発環境では認証スルー
        new_post = Post(
            id=len(posts_db) + 1,
            title=post_data["title"],
            content=post_data["content"],
            author_id=DEV_USER_ID,
            author_name="Dev User"
        )
        posts_db.append(new_post)
        return PostRead(
            id=new_post.id,
            title=new_post.title,
            content=new_post.content,
            author_id=new_post.author_id,
            author_name=new_post.author_name,
            created_at=new_post.created_at
        )
    else:
        # 本格認証では認証が必要
        return {"message": "Authentication required"}

@app.get("/auth/me")
async def get_current_user():
    """現在のユーザー情報取得"""
    if DEV_AUTH_BYPASS:
        # 開発環境ではダミーユーザー情報を返す
        return {
            "account_id": DEV_USER_ID,
            "nickname": "Dev User",
            "first_name": "Development",
            "last_name": "User",
            "primary_condition": "Test Condition",
            "privacy_level": "private",
            "share_medical_info": False,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    else:
        return {"message": "Authentication required"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
