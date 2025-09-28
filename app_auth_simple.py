"""
簡易認証システム
疾患を抱える消費者向けの認証システム（簡易版）
"""

import os
from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, create_engine, SQLModel
from contextlib import asynccontextmanager
from typing import Optional
import json
from pydantic import BaseModel
from datetime import datetime, timezone
import hashlib
import secrets

# データベース設定
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(DATABASE_URL, echo=True)

# 開発環境用の認証スルー設定
DEV_AUTH_BYPASS = False  # 認証スルー機能を無効化
DEV_USER_ID = int(os.getenv("DEV_USER_ID", "1"))

# 認証用のデータモデル
class UserRegister(BaseModel):
    email: str
    password: str
    nickname: str
    first_name: str
    last_name: str
    primary_condition: str
    language: str = "en-US"
    country: str = "US"
    timezone: str = "UTC"

class UserLogin(BaseModel):
    email: str
    password: str
    remember_me: bool = False

class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: dict

class UserProfileUpdate(BaseModel):
    nickname: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    primary_condition: Optional[str] = None
    language: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None

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

@app.post("/auth/register", response_model=AuthResponse)
async def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """ユーザー登録"""
    try:
        # 簡単なパスワードハッシュ（実際の実装ではbcryptを使用）
        password_hash = hashlib.sha256(user_data.password.encode()).hexdigest()
        
        # アクセストークンとリフレッシュトークンを生成
        access_token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32)
        
        # ユーザー情報を作成
        user_info = {
            "id": 1,  # 実際の実装ではデータベースから取得
            "email": user_data.email,
            "nickname": user_data.nickname,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "primary_condition": user_data.primary_condition,
            "language": user_data.language,
            "country": user_data.country,
            "timezone": user_data.timezone,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=user_info
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login", response_model=AuthResponse)
async def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """ユーザーログイン"""
    try:
        # 簡単な認証（実際の実装ではデータベースで認証）
        if login_data.email and login_data.password:
            # アクセストークンとリフレッシュトークンを生成
            access_token = secrets.token_urlsafe(32)
            refresh_token = secrets.token_urlsafe(32)
            
            # ユーザー情報を作成
            user_info = {
                "id": 1,
                "email": login_data.email,
                "nickname": "User",
                "first_name": "Test",
                "last_name": "User",
                "primary_condition": "Test Condition",
                "language": "en-US",
                "country": "US",
                "timezone": "UTC",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            return AuthResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                user=user_info
            )
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/auth/profile")
async def update_user_profile(
    profile_data: UserProfileUpdate, 
    db: Session = Depends(get_db),
    authorization: str = Header(None)
):
    """ユーザープロフィール更新"""
    try:
        # 簡単な認証チェック（実際の実装ではJWTトークンを検証）
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # 現在のユーザー情報を取得（実際の実装ではデータベースから取得）
        current_user = {
            "id": 1,
            "email": "user@example.com",
            "nickname": "User",
            "first_name": "Test",
            "last_name": "User",
            "primary_condition": "Test Condition",
            "language": "en-US",
            "country": "US",
            "timezone": "UTC",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # プロフィール情報を更新
        updated_user = {**current_user}
        for field, value in profile_data.model_dump(exclude_unset=True).items():
            if value is not None:
                updated_user[field] = value
        
        updated_user["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        return {
            "message": "Profile updated successfully",
            "user": updated_user
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
