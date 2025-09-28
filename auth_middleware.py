"""
認証ミドルウェア
疾患を抱える消費者向けの認証システム
"""

import os
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel import Session
from typing import Optional, Callable
from auth_service import AuthService
from auth_models import UserProfile

# 開発環境用の認証スルー設定
DEV_AUTH_BYPASS = os.getenv("DEV_AUTH_BYPASS", "false").lower() == "true"


class AuthMiddleware:
    """認証ミドルウェア"""
    
    def __init__(self, db_session_factory: Callable[[], Session]):
        self.db_session_factory = db_session_factory
    
    async def __call__(self, request: Request, call_next):
        """認証ミドルウェア実行"""
        # 開発環境での認証スルー
        if DEV_AUTH_BYPASS:
            # 開発用のダミーユーザー情報をリクエストに追加
            request.state.current_user = self._get_dev_user()
            request.state.user_id = int(os.getenv("DEV_USER_ID", "1"))
            return await call_next(request)
        
        # 認証が必要なパスかチェック
        if self._is_auth_required_path(request.url.path):
            # 認証トークン取得
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Authentication required"}
                )
            
            token = auth_header.split(" ")[1]
            
            # データベースセッション取得
            db = self.db_session_factory()
            try:
                auth_service = AuthService(db)
                current_user = auth_service.get_current_user(token)
                
                if not current_user:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "Invalid token"}
                    )
                
                # ユーザー情報をリクエストに追加
                request.state.current_user = current_user
                request.state.user_id = current_user.account_id
                
            except Exception as e:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": f"Authentication error: {str(e)}"}
                )
            finally:
                db.close()
        
        return await call_next(request)
    
    def _is_auth_required_path(self, path: str) -> bool:
        """認証が必要なパスかチェック"""
        # 認証不要なパス
        public_paths = [
            "/auth/register",
            "/auth/login",
            "/auth/refresh",
            "/auth/health",
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc"
        ]
        
        # パスが認証不要リストに含まれているかチェック
        for public_path in public_paths:
            if path.startswith(public_path):
                return False
        
        # その他のパスは認証が必要
        return True
    
    def _get_dev_user(self) -> UserProfile:
        """開発環境用ユーザー取得"""
        return UserProfile(
            account_id=int(os.getenv("DEV_USER_ID", "1")),
            nickname="Dev User",
            first_name="Development",
            last_name="User",
            primary_condition="Test Condition",
            privacy_level="private",
            share_medical_info=False
        )


def create_auth_middleware(db_session_factory: Callable[[], Session]) -> AuthMiddleware:
    """認証ミドルウェア作成"""
    return AuthMiddleware(db_session_factory)


def get_current_user_from_request(request: Request) -> Optional[UserProfile]:
    """リクエストから現在のユーザー取得"""
    return getattr(request.state, "current_user", None)


def get_user_id_from_request(request: Request) -> Optional[int]:
    """リクエストからユーザーID取得"""
    return getattr(request.state, "user_id", None)


def require_auth(request: Request) -> UserProfile:
    """認証必須チェック"""
    current_user = get_current_user_from_request(request)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return current_user


def require_role(required_role: str):
    """特定のロールが必要なデコレータ"""
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            current_user = require_auth(request)
            
            # TODO: ロールチェックロジックを実装
            # 現在は簡易実装
            if not hasattr(current_user, 'roles'):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
