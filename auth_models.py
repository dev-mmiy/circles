"""
認証関連のSQLModel定義
疾患を抱える消費者向けのユーザー認証システム
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from enum import Enum
import uuid


class UserRole(str, Enum):
    """ユーザーロール"""
    PATIENT = "patient"  # 患者
    CAREGIVER = "caregiver"  # 介護者
    MEDICAL_PROFESSIONAL = "medical_professional"  # 医療従事者
    ADMIN = "admin"  # 管理者


class AccountStatus(str, Enum):
    """アカウントステータス"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class Account(SQLModel, table=True):
    """アカウント基本情報"""
    __tablename__ = "account"

    id: int = Field(primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    status: AccountStatus = Field(default=AccountStatus.PENDING_VERIFICATION)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login_at: Optional[datetime] = None
    failed_login_attempts: int = Field(default=0)
    locked_until: Optional[datetime] = None

    # リレーションシップ
    user_profile: Optional["UserProfile"] = Relationship(back_populates="account")
    user_roles: List["UserRoleAssignment"] = Relationship(back_populates="account")
    sessions: List["UserSession"] = Relationship(back_populates="account")


class UserProfile(SQLModel, table=True):
    """ユーザープロフィール（疾患情報含む）"""
    __tablename__ = "user_profile"

    account_id: int = Field(foreign_key="account.id", primary_key=True)
    nickname: Optional[str] = Field(max_length=100)
    first_name: Optional[str] = Field(max_length=100)
    last_name: Optional[str] = Field(max_length=100)
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = Field(max_length=20)
    phone: Optional[str] = Field(max_length=20)
    timezone: str = Field(default="UTC")
    language: str = Field(default="en-US")
    country: str = Field(default="US")
    
    # 疾患関連情報
    primary_condition: Optional[str] = Field(max_length=200)  # 主な疾患
    conditions: Optional[str] = Field(default=None)  # 疾患一覧 (JSON文字列)
    medications: Optional[str] = Field(default=None)  # 服薬情報 (JSON文字列)
    emergency_contact: Optional[str] = Field(default=None)  # 緊急連絡先 (JSON文字列)
    
    # プライバシー設定
    privacy_level: str = Field(default="private")  # private, friends, public
    share_medical_info: bool = Field(default=False)
    
    # アクセシビリティ設定
    accessibility_needs: Optional[str] = Field(default=None)  # アクセシビリティ設定 (JSON文字列)
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # リレーションシップ
    account: Optional["Account"] = Relationship(back_populates="user_profile")


class UserRoleAssignment(SQLModel, table=True):
    """ユーザーロール管理"""
    __tablename__ = "user_role"

    id: int = Field(primary_key=True)
    account_id: int = Field(foreign_key="account.id")
    role: str = Field()  # Changed from UserRole enum to str
    granted_by: Optional[int] = Field(foreign_key="account.id")
    granted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None

    # リレーションシップ
    account: Optional["Account"] = Relationship(back_populates="user_roles")


class UserSession(SQLModel, table=True):
    """ユーザーセッション管理"""
    __tablename__ = "user_session"

    id: str = Field(primary_key=True, default_factory=lambda: str(uuid.uuid4()))
    account_id: int = Field(foreign_key="account.id")
    session_token: str = Field(unique=True, index=True)
    refresh_token: str = Field(unique=True, index=True)
    device_info: Optional[str] = Field(default=None)  # JSON文字列
    ip_address: Optional[str] = Field(max_length=45)
    user_agent: Optional[str] = Field(max_length=500)
    is_active: bool = Field(default=True)
    expires_at: datetime = Field()
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # リレーションシップ
    account: Optional["Account"] = Relationship(back_populates="sessions")


class MFAConfig(SQLModel, table=True):
    """多要素認証設定"""
    __tablename__ = "mfa_config"

    id: int = Field(primary_key=True)
    account_id: int = Field(foreign_key="account.id", unique=True)
    mfa_enabled: bool = Field(default=False)
    mfa_method: Optional[str] = Field(max_length=20)  # sms, email, totp
    mfa_secret: Optional[str] = Field(max_length=255)
    backup_codes: Optional[str] = Field(default=None)  # JSON文字列
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Pydantic models for API
class UserRegister(SQLModel):
    """ユーザー登録リクエスト"""
    email: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    nickname: Optional[str] = Field(max_length=100)
    first_name: Optional[str] = Field(max_length=100)
    last_name: Optional[str] = Field(max_length=100)
    primary_condition: Optional[str] = Field(max_length=200)
    language: str = Field(default="en-US")
    country: str = Field(default="US")
    timezone: str = Field(default="UTC")


class UserLogin(SQLModel):
    """ユーザーログインリクエスト"""
    email: str = Field(max_length=255)
    password: str = Field(max_length=128)
    remember_me: bool = Field(default=False)
    device_info: Optional[str] = None  # JSON文字列


class UserProfileUpdate(SQLModel):
    """ユーザープロフィール更新リクエスト"""
    nickname: Optional[str] = Field(max_length=100)
    first_name: Optional[str] = Field(max_length=100)
    last_name: Optional[str] = Field(max_length=100)
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = Field(max_length=20)
    phone: Optional[str] = Field(max_length=20)
    primary_condition: Optional[str] = Field(max_length=200)
    conditions: Optional[str] = None  # JSON文字列
    medications: Optional[str] = None  # JSON文字列
    emergency_contact: Optional[str] = None  # JSON文字列
    privacy_level: Optional[str] = None
    share_medical_info: Optional[bool] = None
    accessibility_needs: Optional[str] = None  # JSON文字列


class UserProfileRead(SQLModel):
    """ユーザープロフィール読み取りレスポンス"""
    account_id: int
    nickname: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    date_of_birth: Optional[datetime]
    gender: Optional[str]
    phone: Optional[str]
    primary_condition: Optional[str]
    conditions: Optional[str]  # JSON文字列
    medications: Optional[str]  # JSON文字列
    emergency_contact: Optional[str]  # JSON文字列
    privacy_level: str
    share_medical_info: bool
    accessibility_needs: Optional[str]  # JSON文字列
    created_at: datetime
    updated_at: datetime


class AuthResponse(SQLModel):
    """認証レスポンス"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserProfileRead


class TokenRefresh(SQLModel):
    """トークンリフレッシュリクエスト"""
    refresh_token: str


class PasswordChange(SQLModel):
    """パスワード変更リクエスト"""
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class PasswordReset(SQLModel):
    """パスワードリセットリクエスト"""
    email: str = Field(max_length=255)


class PasswordResetConfirm(SQLModel):
    """パスワードリセット確認"""
    token: str
    new_password: str = Field(min_length=8, max_length=128)
