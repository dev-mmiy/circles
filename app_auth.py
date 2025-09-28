"""
認証統合FastAPIアプリケーション
疾患を抱える消費者向けの認証システム
"""

import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlmodel import Session, create_engine, SQLModel
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from auth_models import Account, UserProfile, UserSession, MFAConfig, UserRoleAssignment
from auth_endpoints import auth_router
from auth_middleware import create_auth_middleware, get_current_user_from_request
from auth_service import AuthService

# データベース設定
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://healthcare_user:healthcare_password@localhost:5432/healthcare_db")
engine = create_engine(DATABASE_URL, echo=True)

# 開発環境用の認証スルー設定
DEV_AUTH_BYPASS = os.getenv("DEV_AUTH_BYPASS", "false").lower() == "true"


def get_db() -> Session:
    """データベースセッション取得"""
    with Session(engine) as session:
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションライフサイクル管理"""
    # 起動時
    print("🚀 Starting Healthcare Community Platform with Authentication")
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

# 信頼できるホスト設定
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost"]
)

# 認証ミドルウェア追加
auth_middleware = create_auth_middleware(get_db)
app.middleware("http")(auth_middleware)

# ルーター登録
app.include_router(auth_router)

# 既存の投稿機能（認証統合版）
from app_simple import Post, PostCreate, PostRead, posts_db

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

@app.get("/posts", response_model=list[PostRead])
async def get_posts(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user_from_request)
):
    """投稿一覧取得（認証必須）"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    return posts_db[skip:skip + limit]

@app.post("/posts", response_model=PostRead, status_code=status.HTTP_201_CREATED)
async def create_post(
    post: PostCreate,
    current_user = Depends(get_current_user_from_request)
):
    """投稿作成（認証必須）"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    # 投稿作成
    new_post = Post(
        id=len(posts_db) + 1,
        title=post.title,
        content=post.content,
        author_id=current_user.account_id,
        author_name=current_user.nickname or "Anonymous"
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

@app.get("/posts/{post_id}", response_model=PostRead)
async def get_post(
    post_id: int,
    current_user = Depends(get_current_user_from_request)
):
    """投稿詳細取得（認証必須）"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    post = next((p for p in posts_db if p.id == post_id), None)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    return PostRead(
        id=post.id,
        title=post.title,
        content=post.content,
        author_id=post.author_id,
        author_name=post.author_name,
        created_at=post.created_at
    )

@app.put("/posts/{post_id}", response_model=PostRead)
async def update_post(
    post_id: int,
    post: PostCreate,
    current_user = Depends(get_current_user_from_request)
):
    """投稿更新（認証必須）"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    existing_post = next((p for p in posts_db if p.id == post_id), None)
    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # 投稿者チェック
    if existing_post.author_id != current_user.account_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post"
        )
    
    # 投稿更新
    existing_post.title = post.title
    existing_post.content = post.content
    
    return PostRead(
        id=existing_post.id,
        title=existing_post.title,
        content=existing_post.content,
        author_id=existing_post.author_id,
        author_name=existing_post.author_name,
        created_at=existing_post.created_at
    )

@app.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    current_user = Depends(get_current_user_from_request)
):
    """投稿削除（認証必須）"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    post_index = next((i for i, p in enumerate(posts_db) if p.id == post_id), None)
    if post_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # 投稿者チェック
    if posts_db[post_index].author_id != current_user.account_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post"
        )
    
    # 投稿削除
    del posts_db[post_index]
    
    return {"message": "Post deleted successfully"}

@app.get("/user/posts", response_model=list[PostRead])
async def get_user_posts(
    current_user = Depends(get_current_user_from_request)
):
    """ユーザーの投稿一覧取得（認証必須）"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    user_posts = [p for p in posts_db if p.author_id == current_user.account_id]
    return user_posts


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
