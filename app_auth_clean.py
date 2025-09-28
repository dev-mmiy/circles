"""
認証統合FastAPIアプリケーション（クリーン版）
疾患を抱える消費者向けの認証システム
"""

import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlmodel import Session, create_engine, SQLModel
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from datetime import datetime, timezone

from auth_models import Account, UserProfile, UserSession, MFAConfig, UserRoleAssignment
from auth_endpoints import auth_router
from auth_middleware import create_auth_middleware, get_current_user_from_request
from auth_service import AuthService

# データベース設定
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(DATABASE_URL, echo=True)

# 開発環境用の認証スルー設定
DEV_AUTH_BYPASS = False  # 認証スルー機能を無効化


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

@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "Healthcare Community Platform API",
        "version": "2.0.0",
        "features": {
            "authentication": True,
            "posts": False,
            "internationalization": True,
            "dev_bypass": DEV_AUTH_BYPASS
        }
    }

@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "healthcare-community-platform",
        "version": "2.0.0",
        "authentication": {
            "enabled": True,
            "dev_bypass": DEV_AUTH_BYPASS
        }
    }
