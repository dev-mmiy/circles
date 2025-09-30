"""
外部認証サービス統合エンドポイント
Auth0, Google Cloud Identity, Keycloak, Firebase対応
"""

import os
import secrets
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.responses import RedirectResponse
from sqlmodel import Session
from typing import Optional, Dict, Any
import urllib.parse

from auth_providers import (
    AuthProviderFactory, ExternalAuthService, AuthProviderType,
    get_auth_provider_config
)
from auth_service import AuthService
from auth_models import UserProfile, UserProfileRead

# ルーター
external_auth_router = APIRouter(prefix="/auth/external", tags=["external-authentication"])

def get_external_auth_service() -> ExternalAuthService:
    """外部認証サービス取得"""
    config = get_auth_provider_config()
    provider = AuthProviderFactory.create_provider(config.provider_type, config)
    return ExternalAuthService(provider)

@external_auth_router.get("/login/{provider}")
async def external_login(
    provider: str,
    request: Request,
    auth_service: ExternalAuthService = Depends(get_external_auth_service)
):
    """外部認証プロバイダーでのログイン"""
    # 状態トークン生成
    state = secrets.token_urlsafe(32)
    
    # セッションに状態を保存（実際の実装ではRedis等を使用）
    request.session["auth_state"] = state
    request.session["auth_provider"] = provider
    
    # 認証URL取得
    auth_url = auth_service.get_auth_url(state)
    
    return RedirectResponse(url=auth_url)

@external_auth_router.get("/callback")
async def external_callback(
    code: str = Query(...),
    state: str = Query(...),
    request: Request,
    auth_service: ExternalAuthService = Depends(get_external_auth_service),
    db: Session = Depends(get_db)
):
    """外部認証コールバック"""
    # 状態トークン検証
    stored_state = request.session.get("auth_state")
    if not stored_state or stored_state != state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter"
        )
    
    try:
        # 外部認証によるユーザー認証
        auth_result = await auth_service.authenticate_user(code, state)
        
        # ユーザー情報からアカウント作成または取得
        user_info = auth_result["user_info"]
        email = user_info.get("email")
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by external provider"
            )
        
        # 既存ユーザー検索
        auth_service_db = AuthService(db)
        existing_user = db.exec(select(Account).where(Account.email == email)).first()
        
        if existing_user:
            # 既存ユーザーの場合、ログイン
            profile = db.exec(select(UserProfile).where(UserProfile.account_id == existing_user.id)).first()
            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile not found"
                )
        else:
            # 新規ユーザーの場合、アカウント作成
            from auth_models import UserRegister, AccountStatus, UserRole
            
            # アカウント作成
            account = Account(
                email=email,
                password_hash="",  # 外部認証の場合は空
                status=AccountStatus.ACTIVE
            )
            db.add(account)
            db.commit()
            db.refresh(account)
            
            # プロフィール作成
            profile = UserProfile(
                account_id=account.id,
                nickname=user_info.get("nickname") or user_info.get("name"),
                first_name=user_info.get("given_name") or user_info.get("first_name"),
                last_name=user_info.get("family_name") or user_info.get("last_name"),
                language="en-US",
                country="US",
                timezone="UTC"
            )
            db.add(profile)
            
            # デフォルトロール（患者）を追加
            user_role = UserRole(
                account_id=account.id,
                role=UserRoleEnum.PATIENT
            )
            db.add(user_role)
            
            db.commit()
            db.refresh(profile)
        
        # セッション作成
        from auth_models import UserSession
        session = UserSession(
            account_id=profile.account_id,
            session_token=secrets.token_urlsafe(32),
            refresh_token=auth_result.get("refresh_token", ""),
            expires_at=datetime.now(timezone.utc) + timedelta(days=30)
        )
        db.add(session)
        db.commit()
        
        # セッション情報をクリア
        request.session.pop("auth_state", None)
        request.session.pop("auth_provider", None)
        
        # フロントエンドにリダイレクト
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        return RedirectResponse(url=f"{frontend_url}/dashboard?token={auth_result['access_token']}")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"External authentication failed: {str(e)}"
        )

@external_auth_router.get("/providers")
async def get_available_providers():
    """利用可能な認証プロバイダー一覧取得"""
    providers = []
    
    # Auth0
    if os.getenv("AUTH0_CLIENT_ID"):
        providers.append({
            "id": "auth0",
            "name": "Auth0",
            "description": "Secure authentication with Auth0",
            "icon": "auth0",
            "enabled": True
        })
    
    # Google Cloud Identity
    if os.getenv("GOOGLE_CLIENT_ID"):
        providers.append({
            "id": "google",
            "name": "Google",
            "description": "Sign in with Google",
            "icon": "google",
            "enabled": True
        })
    
    # Keycloak
    if os.getenv("KEYCLOAK_CLIENT_ID"):
        providers.append({
            "id": "keycloak",
            "name": "Keycloak",
            "description": "Enterprise authentication with Keycloak",
            "icon": "keycloak",
            "enabled": True
        })
    
    # Firebase
    if os.getenv("FIREBASE_PROJECT_ID"):
        providers.append({
            "id": "firebase",
            "name": "Firebase",
            "description": "Sign in with Firebase",
            "icon": "firebase",
            "enabled": True
        })
    
    return {
        "providers": providers,
        "total": len(providers)
    }

@external_auth_router.post("/link/{provider}")
async def link_external_account(
    provider: str,
    request: Request,
    current_user: UserProfile = Depends(get_current_user_from_request),
    auth_service: ExternalAuthService = Depends(get_external_auth_service)
):
    """外部アカウント連携"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    # 状態トークン生成
    state = secrets.token_urlsafe(32)
    request.session["link_state"] = state
    request.session["link_provider"] = provider
    request.session["link_user_id"] = current_user.account_id
    
    # 認証URL取得
    auth_url = auth_service.get_auth_url(state)
    
    return {"auth_url": auth_url}

@external_auth_router.get("/link/callback")
async def link_callback(
    code: str = Query(...),
    state: str = Query(...),
    request: Request,
    auth_service: ExternalAuthService = Depends(get_external_auth_service),
    db: Session = Depends(get_db)
):
    """外部アカウント連携コールバック"""
    # 状態トークン検証
    stored_state = request.session.get("link_state")
    if not stored_state or stored_state != state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter"
        )
    
    user_id = request.session.get("link_user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found in session"
        )
    
    try:
        # 外部認証によるユーザー認証
        auth_result = await auth_service.authenticate_user(code, state)
        user_info = auth_result["user_info"]
        
        # 外部アカウント情報を保存
        from auth_models import ExternalAccount
        external_account = ExternalAccount(
            account_id=user_id,
            provider=provider,
            external_id=user_info.get("sub") or user_info.get("id"),
            external_email=user_info.get("email"),
            external_name=user_info.get("name"),
            access_token=auth_result["access_token"],
            refresh_token=auth_result.get("refresh_token"),
            expires_at=datetime.now(timezone.utc) + timedelta(days=30)
        )
        db.add(external_account)
        db.commit()
        
        # セッション情報をクリア
        request.session.pop("link_state", None)
        request.session.pop("link_provider", None)
        request.session.pop("link_user_id", None)
        
        return {"message": "External account linked successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Account linking failed: {str(e)}"
        )

@external_auth_router.get("/health")
async def external_auth_health():
    """外部認証サービスヘルスチェック"""
    providers = []
    
    # 各プロバイダーの設定確認
    if os.getenv("AUTH0_CLIENT_ID"):
        providers.append({"name": "Auth0", "status": "configured"})
    
    if os.getenv("GOOGLE_CLIENT_ID"):
        providers.append({"name": "Google Cloud", "status": "configured"})
    
    if os.getenv("KEYCLOAK_CLIENT_ID"):
        providers.append({"name": "Keycloak", "status": "configured"})
    
    if os.getenv("FIREBASE_PROJECT_ID"):
        providers.append({"name": "Firebase", "status": "configured"})
    
    return {
        "status": "healthy",
        "service": "external-authentication",
        "providers": providers,
        "total_providers": len(providers)
    }



