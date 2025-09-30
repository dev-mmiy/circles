"""
新しいデータベース構造に対応したSQLModel定義
統合されたユーザー管理システム
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum

# 列挙型の定義
class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class BloodType(str, Enum):
    A = "A"
    B = "B"
    AB = "AB"
    O = "O"

class ActivityLevel(str, Enum):
    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"

class PrivacyLevel(str, Enum):
    PRIVATE = "private"
    FRIENDS = "friends"
    PUBLIC = "public"

# 1. 統合ユーザーテーブル
class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    first_name_romaji: Optional[str] = Field(default=None, max_length=100)
    last_name_romaji: Optional[str] = Field(default=None, max_length=100)
    first_name_local: Optional[str] = Field(default=None, max_length=100)
    last_name_local: Optional[str] = Field(default=None, max_length=100)
    phone_number: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    
    # リレーションシップ
    health_profile: Optional["UserHealthProfile"] = Relationship(back_populates="user")
    sessions: List["UserSession"] = Relationship(back_populates="user")
    body_measurements: List["BodyMeasurement"] = Relationship(back_populates="user")
    privacy_settings: Optional["PrivacySettings"] = Relationship(back_populates="user")

# 2. ユーザーヘルスプロファイル
class UserHealthProfile(SQLModel, table=True):
    __tablename__ = "user_health_profiles"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    birth_date: Optional[str] = Field(default=None)  # YYYY-MM-DD format
    gender: Optional[Gender] = Field(default=None)
    blood_type: Optional[BloodType] = Field(default=None)
    region: Optional[str] = Field(default=None, max_length=100)
    height_cm: Optional[float] = Field(default=None)
    current_weight_kg: Optional[float] = Field(default=None)
    target_weight_kg: Optional[float] = Field(default=None)
    target_body_fat_percentage: Optional[float] = Field(default=None)
    activity_level: Optional[ActivityLevel] = Field(default=None)
    medical_conditions: Optional[str] = Field(default=None)
    medications: Optional[str] = Field(default=None)
    allergies: Optional[str] = Field(default=None)
    emergency_contact_name: Optional[str] = Field(default=None, max_length=100)
    emergency_contact_phone: Optional[str] = Field(default=None, max_length=20)
    doctor_name: Optional[str] = Field(default=None, max_length=100)
    doctor_phone: Optional[str] = Field(default=None, max_length=20)
    insurance_number: Optional[str] = Field(default=None, max_length=50)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # リレーションシップ
    user: User = Relationship(back_populates="health_profile")

# 3. ユーザーセッション
class UserSession(SQLModel, table=True):
    __tablename__ = "user_sessions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    session_token: str = Field(unique=True, index=True, max_length=255)
    refresh_token: Optional[str] = Field(default=None, max_length=255)
    device_info: Optional[str] = Field(default=None)
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # リレーションシップ
    user: User = Relationship(back_populates="sessions")

# 4. 体組成測定データ
class BodyMeasurement(SQLModel, table=True):
    __tablename__ = "body_measurements"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    weight_kg: Optional[float] = Field(default=None)
    body_fat_percentage: Optional[float] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    measurement_date: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # リレーションシップ
    user: User = Relationship(back_populates="body_measurements")

# 5. プライバシー設定
class PrivacySettings(SQLModel, table=True):
    __tablename__ = "privacy_settings"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    privacy_level: PrivacyLevel = Field(default=PrivacyLevel.PRIVATE)
    share_medical_info: bool = Field(default=False)
    share_contact_info: bool = Field(default=False)
    share_measurements: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # リレーションシップ
    user: User = Relationship(back_populates="privacy_settings")

# API用のレスポンスモデル
class UserRead(SQLModel):
    id: int
    email: str
    first_name_romaji: Optional[str] = None
    last_name_romaji: Optional[str] = None
    first_name_local: Optional[str] = None
    last_name_local: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool

class UserHealthProfileRead(SQLModel):
    id: int
    user_id: int
    birth_date: Optional[str] = None
    gender: Optional[Gender] = None
    blood_type: Optional[BloodType] = None
    region: Optional[str] = None
    height_cm: Optional[float] = None
    current_weight_kg: Optional[float] = None
    target_weight_kg: Optional[float] = None
    target_body_fat_percentage: Optional[float] = None
    activity_level: Optional[ActivityLevel] = None
    medical_conditions: Optional[str] = None
    medications: Optional[str] = None
    allergies: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    doctor_name: Optional[str] = None
    doctor_phone: Optional[str] = None
    insurance_number: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class BodyMeasurementRead(SQLModel):
    id: int
    user_id: int
    weight_kg: Optional[float] = None
    body_fat_percentage: Optional[float] = None
    notes: Optional[str] = None
    measurement_date: datetime
    created_at: datetime

class PrivacySettingsRead(SQLModel):
    id: int
    user_id: int
    privacy_level: PrivacyLevel
    share_medical_info: bool
    share_contact_info: bool
    share_measurements: bool
    created_at: datetime
    updated_at: datetime

# 統合プロフィールレスポンス
class IntegratedUserProfile(SQLModel):
    user: UserRead
    health_profile: Optional[UserHealthProfileRead] = None
    privacy_settings: Optional[PrivacySettingsRead] = None
    latest_measurement: Optional[BodyMeasurementRead] = None

# 更新用のモデル
class UserUpdate(SQLModel):
    first_name_romaji: Optional[str] = None
    last_name_romaji: Optional[str] = None
    first_name_local: Optional[str] = None
    last_name_local: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None

class UserHealthProfileUpdate(SQLModel):
    birth_date: Optional[str] = None
    gender: Optional[Gender] = None
    blood_type: Optional[BloodType] = None
    region: Optional[str] = None
    height_cm: Optional[float] = None
    current_weight_kg: Optional[float] = None
    target_weight_kg: Optional[float] = None
    target_body_fat_percentage: Optional[float] = None
    activity_level: Optional[ActivityLevel] = None
    medical_conditions: Optional[str] = None
    medications: Optional[str] = None
    allergies: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    doctor_name: Optional[str] = None
    doctor_phone: Optional[str] = None
    insurance_number: Optional[str] = None

class BodyMeasurementCreate(SQLModel):
    weight_kg: Optional[float] = None
    body_fat_percentage: Optional[float] = None
    notes: Optional[str] = None
    measurement_date: datetime

class PrivacySettingsUpdate(SQLModel):
    privacy_level: Optional[PrivacyLevel] = None
    share_medical_info: Optional[bool] = None
    share_contact_info: Optional[bool] = None
    share_measurements: Optional[bool] = None
