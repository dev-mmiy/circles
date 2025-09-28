"""
認証エンドポイント
疾患を抱える消費者向けの認証API
"""

import os
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from typing import Optional

from auth_models import (
    UserRegister, UserLogin, UserProfileUpdate, AuthResponse,
    TokenRefresh, PasswordChange, PasswordReset, PasswordResetConfirm,
    UserProfileRead
)
from auth_service import AuthService
from sqlmodel import Session, create_engine

# データベース設定
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(DATABASE_URL)

def get_db() -> Session:
    """データベースセッション取得"""
    with Session(engine) as session:
        yield session

# 認証スキーム
security = HTTPBearer()

# ルーター
auth_router = APIRouter(prefix="/auth", tags=["authentication"])


def get_auth_service(db: Session) -> AuthService:
    """認証サービス取得"""
    return AuthService(db)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[UserProfile]:
    """現在のユーザー取得（依存性注入）"""
    auth_service = get_auth_service(db)
    return auth_service.get_current_user(credentials.credentials)


@auth_router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegister,
    auth_service: AuthService = Depends(get_auth_service)
):
    """ユーザー登録"""
    try:
        return auth_service.register_user(user_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@auth_router.post("/login", response_model=AuthResponse)
async def login_user(
    login_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """ユーザーログイン"""
    try:
        return auth_service.login_user(login_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@auth_router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    refresh_data: TokenRefresh,
    auth_service: AuthService = Depends(get_auth_service)
):
    """トークンリフレッシュ"""
    try:
        return auth_service.refresh_token(refresh_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )


@auth_router.post("/logout")
async def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
):
    """ユーザーログアウト"""
    try:
        success = auth_service.logout_user(credentials.credentials)
        if success:
            return {"message": "Logout successful"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Logout failed"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )


@auth_router.get("/me", response_model=UserProfileRead)
async def get_current_user_profile(
    current_user: Optional[UserProfile] = Depends(get_current_user)
):
    """現在のユーザープロフィール取得"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    return UserProfileRead(
        account_id=current_user.account_id,
        nickname=current_user.nickname,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        date_of_birth=current_user.date_of_birth,
        gender=current_user.gender,
        phone=current_user.phone,
        primary_condition=current_user.primary_condition,
        conditions=current_user.conditions,
        medications=current_user.medications,
        emergency_contact=current_user.emergency_contact,
        privacy_level=current_user.privacy_level,
        share_medical_info=current_user.share_medical_info,
        accessibility_needs=current_user.accessibility_needs,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@auth_router.put("/me", response_model=UserProfileRead)
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: Optional[UserProfile] = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """ユーザープロフィール更新"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        return auth_service.update_user_profile(current_user.account_id, profile_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile update failed: {str(e)}"
        )


@auth_router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: Optional[UserProfile] = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """パスワード変更"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    # TODO: パスワード変更ロジックを実装
    return {"message": "Password change functionality will be implemented"}


@auth_router.post("/reset-password")
async def request_password_reset(
    reset_data: PasswordReset,
    auth_service: AuthService = Depends(get_auth_service)
):
    """パスワードリセット要求"""
    # TODO: パスワードリセットロジックを実装
    return {"message": "Password reset functionality will be implemented"}


@auth_router.post("/reset-password/confirm")
async def confirm_password_reset(
    confirm_data: PasswordResetConfirm,
    auth_service: AuthService = Depends(get_auth_service)
):
    """パスワードリセット確認"""
    # TODO: パスワードリセット確認ロジックを実装
    return {"message": "Password reset confirmation functionality will be implemented"}


@auth_router.get("/health")
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
            "dev_bypass": False  # 認証スルー機能を無効化
        }
    }
