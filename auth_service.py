"""
認証サービス
疾患を抱える消費者向けの認証システム
"""

import os
import secrets
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, Tuple
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select
from fastapi import HTTPException, status
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from auth_models import (
    Account, UserProfile, UserSession, MFAConfig, UserRoleAssignment,
    UserRegister, UserLogin, UserProfileUpdate, AuthResponse,
    TokenRefresh, PasswordChange, PasswordReset, PasswordResetConfirm,
    AccountStatus, UserRole
)

# 設定
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

# パスワードハッシュ
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 開発環境用の認証スルー設定
DEV_AUTH_BYPASS = False  # 認証スルー機能を無効化
DEV_USER_ID = int(os.getenv("DEV_USER_ID", "1"))


class AuthService:
    """認証サービス"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_password_hash(self, password: str) -> str:
        """パスワードハッシュ作成"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """パスワード検証"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """アクセストークン作成"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def create_refresh_token(self, data: dict) -> str:
        """リフレッシュトークン作成"""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """トークン検証"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None
    
    def register_user(self, user_data: UserRegister) -> AuthResponse:
        """ユーザー登録"""
        # メールアドレス重複チェック
        existing_user = self.db.exec(select(Account).where(Account.email == user_data.email)).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # アカウント作成
        account = Account(
            email=user_data.email,
            password_hash=self.create_password_hash(user_data.password),
            status=AccountStatus.PENDING_VERIFICATION
        )
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        
        # ユーザープロフィール作成
        profile = UserProfile(
            account_id=account.id,
            nickname=user_data.nickname,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            primary_condition=user_data.primary_condition,
            language=user_data.language,
            country=user_data.country,
            timezone=user_data.timezone
        )
        self.db.add(profile)
        
        # デフォルトロール（患者）を追加
        user_role = UserRoleAssignment(
            account_id=account.id,
            role="patient"
        )
        self.db.add(user_role)
        
        self.db.commit()
        self.db.refresh(profile)
        
        # 認証トークン作成
        access_token = self.create_access_token({"sub": str(account.id)})
        refresh_token = self.create_refresh_token({"sub": str(account.id)})
        
        # セッション作成
        session = UserSession(
            account_id=account.id,
            session_token=secrets.token_urlsafe(32),
            refresh_token=refresh_token,
            expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )
        self.db.add(session)
        self.db.commit()
        
        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserProfileRead(
                account_id=profile.account_id,
                nickname=profile.nickname,
                first_name=profile.first_name,
                last_name=profile.last_name,
                date_of_birth=profile.date_of_birth,
                gender=profile.gender,
                phone=profile.phone,
                primary_condition=profile.primary_condition,
                conditions=profile.conditions,
                medications=profile.medications,
                emergency_contact=profile.emergency_contact,
                privacy_level=profile.privacy_level,
                share_medical_info=profile.share_medical_info,
                accessibility_needs=profile.accessibility_needs,
                created_at=profile.created_at,
                updated_at=profile.updated_at
            )
        )
    
    def login_user(self, login_data: UserLogin) -> AuthResponse:
        """ユーザーログイン"""
        # 開発環境での認証スルー
        if DEV_AUTH_BYPASS:
            return self._dev_auth_bypass()
        
        # アカウント検索
        account = self.db.exec(select(Account).where(Account.email == login_data.email)).first()
        if not account:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # アカウントロックチェック
        if account.locked_until and account.locked_until > datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account is locked"
            )
        
        # パスワード検証
        if not self.verify_password(login_data.password, account.password_hash):
            # ログイン失敗回数を増加
            account.failed_login_attempts += 1
            if account.failed_login_attempts >= 5:
                account.locked_until = datetime.now(timezone.utc) + timedelta(minutes=30)
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # ログイン成功時のリセット
        account.failed_login_attempts = 0
        account.locked_until = None
        account.last_login_at = datetime.now(timezone.utc)
        self.db.commit()
        
        # プロフィール取得
        profile = self.db.exec(select(UserProfile).where(UserProfile.account_id == account.id)).first()
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        # トークン作成
        access_token = self.create_access_token({"sub": str(account.id)})
        refresh_token = self.create_refresh_token({"sub": str(account.id)})
        
        # セッション作成
        device_info_str = None
        if login_data.device_info:
            import json
            device_info_str = json.dumps(login_data.device_info)
        
        session = UserSession(
            account_id=account.id,
            session_token=secrets.token_urlsafe(32),
            refresh_token=refresh_token,
            device_info=device_info_str,
            expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )
        self.db.add(session)
        self.db.commit()
        
        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserProfileRead(
                account_id=profile.account_id,
                nickname=profile.nickname,
                first_name=profile.first_name,
                last_name=profile.last_name,
                date_of_birth=profile.date_of_birth,
                gender=profile.gender,
                phone=profile.phone,
                primary_condition=profile.primary_condition,
                conditions=profile.conditions,
                medications=profile.medications,
                emergency_contact=profile.emergency_contact,
                privacy_level=profile.privacy_level,
                share_medical_info=profile.share_medical_info,
                accessibility_needs=profile.accessibility_needs,
                created_at=profile.created_at,
                updated_at=profile.updated_at
            )
        )
    
    def _dev_auth_bypass(self) -> AuthResponse:
        """開発環境用認証スルー"""
        # 開発用のダミーユーザーを作成
        profile = UserProfileRead(
            account_id=DEV_USER_ID,
            nickname="Dev User",
            first_name="Development",
            last_name="User",
            primary_condition="Test Condition",
            privacy_level="private",
            share_medical_info=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        return AuthResponse(
            access_token="dev-access-token",
            refresh_token="dev-refresh-token",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=profile
        )
    
    def refresh_token(self, refresh_data: TokenRefresh) -> AuthResponse:
        """トークンリフレッシュ"""
        # 開発環境での認証スルー
        if DEV_AUTH_BYPASS:
            return self._dev_auth_bypass()
        
        # リフレッシュトークン検証
        payload = self.verify_token(refresh_data.refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # セッション検索
        session = self.db.exec(
            select(UserSession).where(UserSession.refresh_token == refresh_data.refresh_token)
        ).first()
        if not session or not session.is_active or session.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # 新しいトークン作成
        access_token = self.create_access_token({"sub": str(session.account_id)})
        new_refresh_token = self.create_refresh_token({"sub": str(session.account_id)})
        
        # セッション更新
        session.refresh_token = new_refresh_token
        session.last_activity_at = datetime.now(timezone.utc)
        self.db.commit()
        
        # プロフィール取得
        profile = self.db.exec(select(UserProfile).where(UserProfile.account_id == session.account_id)).first()
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        return AuthResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserProfileRead(
                account_id=profile.account_id,
                nickname=profile.nickname,
                first_name=profile.first_name,
                last_name=profile.last_name,
                date_of_birth=profile.date_of_birth,
                gender=profile.gender,
                phone=profile.phone,
                primary_condition=profile.primary_condition,
                conditions=profile.conditions,
                medications=profile.medications,
                emergency_contact=profile.emergency_contact,
                privacy_level=profile.privacy_level,
                share_medical_info=profile.share_medical_info,
                accessibility_needs=profile.accessibility_needs,
                created_at=profile.created_at,
                updated_at=profile.updated_at
            )
        )
    
    def get_current_user(self, token: str) -> Optional[UserProfile]:
        """現在のユーザー取得"""
        # 開発環境での認証スルー
        if DEV_AUTH_BYPASS:
            return self._get_dev_user()
        
        payload = self.verify_token(token)
        if not payload:
            return None
        
        account_id = payload.get("sub")
        if not account_id:
            return None
        
        profile = self.db.exec(select(UserProfile).where(UserProfile.account_id == int(account_id))).first()
        return profile
    
    def _get_dev_user(self) -> UserProfile:
        """開発環境用ユーザー取得"""
        return UserProfile(
            account_id=DEV_USER_ID,
            nickname="Dev User",
            first_name="Development",
            last_name="User",
            primary_condition="Test Condition",
            privacy_level="private",
            share_medical_info=False
        )
    
    def update_user_profile(self, user_id: int, profile_data: UserProfileUpdate) -> UserProfileRead:
        """ユーザープロフィール更新"""
        profile = self.db.exec(select(UserProfile).where(UserProfile.account_id == user_id)).first()
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        # プロフィール更新
        update_data = profile_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            # JSONフィールドの場合は文字列として保存
            if field in ['conditions', 'medications', 'emergency_contact', 'accessibility_needs']:
                if value is not None:
                    import json
                    setattr(profile, field, json.dumps(value))
                else:
                    setattr(profile, field, None)
            else:
                setattr(profile, field, value)
        
        profile.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(profile)
        
        return UserProfileRead(
            account_id=profile.account_id,
            nickname=profile.nickname,
            first_name=profile.first_name,
            last_name=profile.last_name,
            date_of_birth=profile.date_of_birth,
            gender=profile.gender,
            phone=profile.phone,
            primary_condition=profile.primary_condition,
            conditions=profile.conditions,
            medications=profile.medications,
            emergency_contact=profile.emergency_contact,
            privacy_level=profile.privacy_level,
            share_medical_info=profile.share_medical_info,
            accessibility_needs=profile.accessibility_needs,
            created_at=profile.created_at,
            updated_at=profile.updated_at
        )
    
    def logout_user(self, token: str) -> bool:
        """ユーザーログアウト"""
        # 開発環境での認証スルー
        if DEV_AUTH_BYPASS:
            return True
        
        payload = self.verify_token(token)
        if not payload:
            return False
        
        account_id = payload.get("sub")
        if not account_id:
            return False
        
        # セッション無効化
        sessions = self.db.exec(select(UserSession).where(UserSession.account_id == int(account_id))).all()
        for session in sessions:
            session.is_active = False
        self.db.commit()
        
        return True
