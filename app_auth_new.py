"""
新しいデータベース構造に対応した認証システム
"""

import os
from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, create_engine, SQLModel, select
from contextlib import asynccontextmanager
from typing import Optional
import json
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
import hashlib
import secrets
import PyJWT as jwt
from passlib.context import CryptContext

# データベース設定
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(DATABASE_URL, echo=True)

# 開発環境用の認証スルー設定
DEV_AUTH_BYPASS = os.getenv("DEV_AUTH_BYPASS", "false").lower() == "true"
DEV_USER_ID = int(os.getenv("DEV_USER_ID", "1"))

# JWT設定
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

# パスワードハッシュ
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

class TokenRefresh(BaseModel):
    refresh_token: str

# データベースセッション取得
def get_db() -> Session:
    with Session(engine) as session:
        yield session

# パスワード関連の関数
def create_password_hash(password: str) -> str:
    """パスワードハッシュ作成"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """パスワード検証"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """アクセストークン作成"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """リフレッシュトークン作成"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """トークン検証"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError:
        return None

# 開発環境用の認証スルー
def dev_auth_bypass() -> AuthResponse:
    """開発環境用の認証スルー"""
    # 新しいデータベース構造からユーザー情報を取得
    with Session(engine) as db:
        from sqlalchemy import text
        user_result = db.exec(text("""
            SELECT id, email, first_name_local, last_name_local, nickname, created_at
            FROM users WHERE id = :user_id
        """).params(user_id=DEV_USER_ID)).first()
        
        if not user_result:
            # デフォルトユーザーを作成
            user_data = {
                "id": DEV_USER_ID,
                "email": "dev@example.com",
                "nickname": "Dev User",
                "first_name": "Dev",
                "last_name": "User",
                "primary_condition": "Development",
                "language": "en-US",
                "country": "US",
                "timezone": "UTC"
            }
        else:
            user_data = {
                "id": user_result[0],
                "email": user_result[1],
                "nickname": user_result[4] if user_result[4] else "User",
                "first_name": user_result[2] if user_result[2] else "User",
                "last_name": user_result[3] if user_result[3] else "User",
                "primary_condition": "Test",
                "language": "en-US",
                "country": "US",
                "timezone": "UTC"
            }
    
    access_token = create_access_token({"sub": str(user_data["id"])})
    refresh_token = create_refresh_token({"sub": str(user_data["id"])})
    
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_data
    )

# FastAPIアプリケーション
@asynccontextmanager
async def lifespan(app: FastAPI):
    # アプリケーション起動時の処理
    yield
    # アプリケーション終了時の処理

app = FastAPI(
    title="Healthcare Auth API",
    description="疾患を抱える消費者向けの認証システム",
    version="1.0.0",
    lifespan=lifespan
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {"message": "Healthcare Auth API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "healthy", "message": "Auth API is running"}

@app.post("/auth/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """ユーザー登録"""
    try:
        # メールアドレスの重複チェック
        from sqlalchemy import text
        existing_user = db.exec(text("SELECT id FROM users WHERE email = :email").params(email=user_data.email)).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # パスワードハッシュ作成
        password_hash = create_password_hash(user_data.password)
        
        # 新しいユーザーを作成（新しいデータベース構造）
        new_user = {
            "email": user_data.email,
            "password_hash": password_hash,
            "first_name_local": user_data.first_name,
            "last_name_local": user_data.last_name,
            "nickname": user_data.nickname,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "is_active": True
        }
        
        # データベースに挿入（直接SQL実行）
        from sqlalchemy import text
        db.exec(text("""
            INSERT INTO users (email, password_hash, first_name_local, last_name_local, 
                             nickname, created_at, updated_at, is_active)
            VALUES (:email, :password_hash, :first_name_local, :last_name_local, 
                   :nickname, :created_at, :updated_at, :is_active)
        """).params(**new_user))
        db.commit()
        
        # 作成されたユーザーを取得
        created_user = db.exec(text("""
            SELECT id, email, first_name_local, last_name_local, nickname, created_at
            FROM users WHERE email = :email
        """).params(email=user_data.email)).first()
        
        # トークン作成
        access_token = create_access_token({"sub": str(created_user[0])})
        refresh_token = create_refresh_token({"sub": str(created_user[0])})
        
        user_response = {
            "id": created_user[0],
            "email": created_user[1],
            "nickname": created_user[4] if created_user[4] else user_data.nickname,
            "first_name": created_user[2] if created_user[2] else user_data.first_name,
            "last_name": created_user[3] if created_user[3] else user_data.last_name,
            "primary_condition": user_data.primary_condition,
            "language": user_data.language,
            "country": user_data.country,
            "timezone": user_data.timezone,
            "created_at": created_user[5].isoformat() if created_user[5] else datetime.now(timezone.utc).isoformat()
        }
        
        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=user_response
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login", response_model=AuthResponse)
async def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """ユーザーログイン"""
    try:
        # 開発環境での認証スルー
        if DEV_AUTH_BYPASS:
            return dev_auth_bypass()
        
        # ユーザー検索（新しいデータベース構造）
        from sqlalchemy import text
        user_result = db.exec(text("""
            SELECT id, email, password_hash, first_name_local, last_name_local, 
                   nickname, created_at, updated_at, is_active
            FROM users WHERE email = :email
        """).params(email=login_data.email)).first()
        
        if not user_result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # アカウントがアクティブかチェック
        if not user_result[8]:  # is_active
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is inactive"
            )
        
        # パスワード検証
        if not verify_password(login_data.password, user_result[2]):  # password_hash
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # トークン作成
        access_token = create_access_token({"sub": str(user_result[0])})
        refresh_token = create_refresh_token({"sub": str(user_result[0])})
        
        user_response = {
            "id": user_result[0],
            "email": user_result[1],
            "nickname": user_result[5] if user_result[5] else "User",
            "first_name": user_result[3] if user_result[3] else "User",
            "last_name": user_result[4] if user_result[4] else "User",
            "primary_condition": "Test",  # デフォルト値
            "language": "en-US",
            "country": "US",
            "timezone": "UTC",
            "created_at": user_result[6].isoformat() if user_result[6] else datetime.now(timezone.utc).isoformat()
        }
        
        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/refresh", response_model=AuthResponse)
async def refresh_token(refresh_data: TokenRefresh, db: Session = Depends(get_db)):
    """トークンリフレッシュ"""
    try:
        # リフレッシュトークンの検証
        payload = verify_token(refresh_data.refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # ユーザー存在確認
        from sqlalchemy import text
        user_result = db.exec(text("""
            SELECT id, email, first_name_local, last_name_local, nickname, is_active
            FROM users WHERE id = :user_id
        """).params(user_id=user_id)).first()
        
        if not user_result or not user_result[5]:  # is_active
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # 新しいトークン作成
        access_token = create_access_token({"sub": str(user_result[0])})
        refresh_token = create_refresh_token({"sub": str(user_result[0])})
        
        user_response = {
            "id": user_result[0],
            "email": user_result[1],
            "nickname": user_result[4] if user_result[4] else "User",
            "first_name": user_result[2] if user_result[2] else "User",
            "last_name": user_result[3] if user_result[3] else "User",
            "primary_condition": "Test",
            "language": "en-US",
            "country": "US",
            "timezone": "UTC"
        }
        
        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
