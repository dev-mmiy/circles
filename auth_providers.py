"""
外部認証プロバイダー統合
Auth0, Google Cloud Identity, Keycloak, Firebase対応
"""

import os
import requests
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

class AuthProviderType(str, Enum):
    """認証プロバイダータイプ"""
    AUTH0 = "auth0"
    GOOGLE_CLOUD = "google_cloud"
    KEYCLOAK = "keycloak"
    FIREBASE = "firebase"
    CUSTOM = "custom"

@dataclass
class AuthProviderConfig:
    """認証プロバイダー設定"""
    provider_type: AuthProviderType
    client_id: str
    client_secret: str
    domain: str
    audience: Optional[str] = None
    scope: str = "openid profile email"
    redirect_uri: str = "http://localhost:3000/auth/callback"

class AuthProvider(ABC):
    """認証プロバイダー基底クラス"""
    
    def __init__(self, config: AuthProviderConfig):
        self.config = config
    
    @abstractmethod
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """ユーザー情報取得"""
        pass
    
    @abstractmethod
    async def validate_token(self, token: str) -> bool:
        """トークン検証"""
        pass
    
    @abstractmethod
    def get_auth_url(self, state: str) -> str:
        """認証URL生成"""
        pass
    
    @abstractmethod
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """認証コードをトークンに交換"""
        pass

class Auth0Provider(AuthProvider):
    """Auth0認証プロバイダー"""
    
    def __init__(self, config: AuthProviderConfig):
        super().__init__(config)
        self.base_url = f"https://{config.domain}"
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Auth0からユーザー情報取得"""
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{self.base_url}/userinfo", headers=headers)
        response.raise_for_status()
        return response.json()
    
    async def validate_token(self, token: str) -> bool:
        """Auth0トークン検証"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{self.base_url}/userinfo", headers=headers)
            return response.status_code == 200
        except:
            return False
    
    def get_auth_url(self, state: str) -> str:
        """Auth0認証URL生成"""
        params = {
            "response_type": "code",
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "scope": self.config.scope,
            "state": state,
            "audience": self.config.audience
        }
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.base_url}/authorize?{query_string}"
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """認証コードをトークンに交換"""
        data = {
            "grant_type": "authorization_code",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "code": code,
            "redirect_uri": self.config.redirect_uri
        }
        response = requests.post(f"{self.base_url}/oauth/token", data=data)
        response.raise_for_status()
        return response.json()

class GoogleCloudProvider(AuthProvider):
    """Google Cloud Identity認証プロバイダー"""
    
    def __init__(self, config: AuthProviderConfig):
        super().__init__(config)
        self.base_url = "https://oauth2.googleapis.com"
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Googleからユーザー情報取得"""
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get("https://www.googleapis.com/oauth2/v2/userinfo", headers=headers)
        response.raise_for_status()
        return response.json()
    
    async def validate_token(self, token: str) -> bool:
        """Googleトークン検証"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get("https://www.googleapis.com/oauth2/v2/userinfo", headers=headers)
            return response.status_code == 200
        except:
            return False
    
    def get_auth_url(self, state: str) -> str:
        """Google認証URL生成"""
        params = {
            "response_type": "code",
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "scope": self.config.scope,
            "state": state,
            "access_type": "offline",
            "prompt": "consent"
        }
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"https://accounts.google.com/o/oauth2/v2/auth?{query_string}"
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """認証コードをトークンに交換"""
        data = {
            "grant_type": "authorization_code",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "code": code,
            "redirect_uri": self.config.redirect_uri
        }
        response = requests.post(f"{self.base_url}/token", data=data)
        response.raise_for_status()
        return response.json()

class KeycloakProvider(AuthProvider):
    """Keycloak認証プロバイダー"""
    
    def __init__(self, config: AuthProviderConfig):
        super().__init__(config)
        self.base_url = f"{config.domain}/realms/{config.audience}"
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Keycloakからユーザー情報取得"""
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{self.base_url}/protocol/openid-connect/userinfo", headers=headers)
        response.raise_for_status()
        return response.json()
    
    async def validate_token(self, token: str) -> bool:
        """Keycloakトークン検証"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{self.base_url}/protocol/openid-connect/userinfo", headers=headers)
            return response.status_code == 200
        except:
            return False
    
    def get_auth_url(self, state: str) -> str:
        """Keycloak認証URL生成"""
        params = {
            "response_type": "code",
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "scope": self.config.scope,
            "state": state
        }
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.base_url}/protocol/openid-connect/auth?{query_string}"
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """認証コードをトークンに交換"""
        data = {
            "grant_type": "authorization_code",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "code": code,
            "redirect_uri": self.config.redirect_uri
        }
        response = requests.post(f"{self.base_url}/protocol/openid-connect/token", data=data)
        response.raise_for_status()
        return response.json()

class FirebaseProvider(AuthProvider):
    """Firebase認証プロバイダー"""
    
    def __init__(self, config: AuthProviderConfig):
        super().__init__(config)
        self.base_url = f"https://identitytoolkit.googleapis.com/v1"
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Firebaseからユーザー情報取得"""
        # Firebaseの場合は、IDトークンからユーザー情報を取得
        import jwt
        decoded = jwt.decode(access_token, options={"verify_signature": False})
        return decoded
    
    async def validate_token(self, token: str) -> bool:
        """Firebaseトークン検証"""
        try:
            # Firebaseの場合は、IDトークンの検証が必要
            # 実際の実装では、Firebase Admin SDKを使用
            return True
        except:
            return False
    
    def get_auth_url(self, state: str) -> str:
        """Firebase認証URL生成"""
        # Firebaseの場合は、通常はクライアントサイドで認証
        return f"https://accounts.google.com/o/oauth2/v2/auth?client_id={self.config.client_id}&redirect_uri={self.config.redirect_uri}&response_type=code&scope={self.config.scope}&state={state}"
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """認証コードをトークンに交換"""
        # Firebaseの場合は、通常はクライアントサイドで処理
        return {"access_token": code, "token_type": "Bearer"}

class AuthProviderFactory:
    """認証プロバイダーファクトリー"""
    
    @staticmethod
    def create_provider(provider_type: AuthProviderType, config: AuthProviderConfig) -> AuthProvider:
        """認証プロバイダー作成"""
        if provider_type == AuthProviderType.AUTH0:
            return Auth0Provider(config)
        elif provider_type == AuthProviderType.GOOGLE_CLOUD:
            return GoogleCloudProvider(config)
        elif provider_type == AuthProviderType.KEYCLOAK:
            return KeycloakProvider(config)
        elif provider_type == AuthProviderType.FIREBASE:
            return FirebaseProvider(config)
        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")

class ExternalAuthService:
    """外部認証サービス統合"""
    
    def __init__(self, provider: AuthProvider):
        self.provider = provider
    
    async def authenticate_user(self, code: str, state: str) -> Dict[str, Any]:
        """外部認証によるユーザー認証"""
        # 認証コードをトークンに交換
        token_data = await self.provider.exchange_code_for_token(code)
        
        # ユーザー情報取得
        user_info = await self.provider.get_user_info(token_data["access_token"])
        
        return {
            "access_token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token"),
            "user_info": user_info,
            "provider": self.provider.__class__.__name__
        }
    
    def get_auth_url(self, state: str) -> str:
        """認証URL取得"""
        return self.provider.get_auth_url(state)
    
    async def validate_external_token(self, token: str) -> bool:
        """外部トークン検証"""
        return await self.provider.validate_token(token)

# 設定例
def get_auth_provider_config() -> AuthProviderConfig:
    """認証プロバイダー設定取得"""
    provider_type = os.getenv("AUTH_PROVIDER", "auth0")
    
    if provider_type == "auth0":
        return AuthProviderConfig(
            provider_type=AuthProviderType.AUTH0,
            client_id=os.getenv("AUTH0_CLIENT_ID", ""),
            client_secret=os.getenv("AUTH0_CLIENT_SECRET", ""),
            domain=os.getenv("AUTH0_DOMAIN", ""),
            audience=os.getenv("AUTH0_AUDIENCE", ""),
            scope="openid profile email",
            redirect_uri=os.getenv("AUTH0_REDIRECT_URI", "http://localhost:3000/auth/callback")
        )
    elif provider_type == "google_cloud":
        return AuthProviderConfig(
            provider_type=AuthProviderType.GOOGLE_CLOUD,
            client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
            domain="accounts.google.com",
            scope="openid profile email",
            redirect_uri=os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/callback")
        )
    elif provider_type == "keycloak":
        return AuthProviderConfig(
            provider_type=AuthProviderType.KEYCLOAK,
            client_id=os.getenv("KEYCLOAK_CLIENT_ID", ""),
            client_secret=os.getenv("KEYCLOAK_CLIENT_SECRET", ""),
            domain=os.getenv("KEYCLOAK_DOMAIN", ""),
            audience=os.getenv("KEYCLOAK_REALM", ""),
            scope="openid profile email",
            redirect_uri=os.getenv("KEYCLOAK_REDIRECT_URI", "http://localhost:3000/auth/callback")
        )
    else:
        raise ValueError(f"Unsupported provider type: {provider_type}")
