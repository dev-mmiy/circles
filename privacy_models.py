"""
プライバシー設定のデータモデル
"""

from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, JSON

class PrivacyLevel(str, Enum):
    """プライバシーレベル"""
    PRIVATE = "private"          # 完全非公開
    FRIENDS_ONLY = "friends_only"  # 友達のみ
    FAMILY_ONLY = "family_only"    # 家族のみ
    PUBLIC = "public"            # 公開

class DataCategory(str, Enum):
    """データカテゴリ"""
    BASIC_INFO = "basic_info"           # 基本情報
    HEALTH_DATA = "health_data"         # 健康データ
    MEDICAL_INFO = "medical_info"       # 医療情報
    EMERGENCY_CONTACT = "emergency_contact"  # 緊急連絡先
    BODY_MEASUREMENTS = "body_measurements"  # 身体測定
    VITAL_SIGNS = "vital_signs"         # バイタルサイン

class UserPrivacySettings(SQLModel, table=True):
    """ユーザープライバシー設定"""
    __tablename__ = "user_privacy_settings"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="accounts.id")
    
    # 基本情報のプライバシー設定
    basic_info_level: PrivacyLevel = Field(default=PrivacyLevel.PRIVATE)
    birth_date_visible: bool = Field(default=False)
    gender_visible: bool = Field(default=False)
    blood_type_visible: bool = Field(default=False)
    region_visible: bool = Field(default=False)
    
    # 健康データのプライバシー設定
    health_data_level: PrivacyLevel = Field(default=PrivacyLevel.PRIVATE)
    height_visible: bool = Field(default=False)
    weight_visible: bool = Field(default=False)
    body_fat_visible: bool = Field(default=False)
    activity_level_visible: bool = Field(default=False)
    
    # 医療情報のプライバシー設定
    medical_info_level: PrivacyLevel = Field(default=PrivacyLevel.PRIVATE)
    medical_conditions_visible: bool = Field(default=False)
    medications_visible: bool = Field(default=False)
    allergies_visible: bool = Field(default=False)
    doctor_info_visible: bool = Field(default=False)
    insurance_visible: bool = Field(default=False)
    
    # 緊急連絡先のプライバシー設定
    emergency_contact_level: PrivacyLevel = Field(default=PrivacyLevel.FAMILY_ONLY)
    emergency_contact_visible: bool = Field(default=True)
    
    # 身体測定データのプライバシー設定
    body_measurements_level: PrivacyLevel = Field(default=PrivacyLevel.PRIVATE)
    body_measurements_visible: bool = Field(default=False)
    
    # バイタルサインのプライバシー設定
    vital_signs_level: PrivacyLevel = Field(default=PrivacyLevel.PRIVATE)
    vital_signs_visible: bool = Field(default=False)
    
    # データ共有設定
    allow_data_sharing: bool = Field(default=False)
    share_with_healthcare_providers: bool = Field(default=False)
    share_with_family: bool = Field(default=False)
    share_with_friends: bool = Field(default=False)
    
    # 研究・統計目的でのデータ利用
    allow_research_participation: bool = Field(default=False)
    allow_anonymous_statistics: bool = Field(default=False)
    
    # タイムスタンプ
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PrivacySettingsUpdate(SQLModel):
    """プライバシー設定更新用スキーマ"""
    # 基本情報
    basic_info_level: Optional[PrivacyLevel] = None
    birth_date_visible: Optional[bool] = None
    gender_visible: Optional[bool] = None
    blood_type_visible: Optional[bool] = None
    region_visible: Optional[bool] = None
    
    # 健康データ
    health_data_level: Optional[PrivacyLevel] = None
    height_visible: Optional[bool] = None
    weight_visible: Optional[bool] = None
    body_fat_visible: Optional[bool] = None
    activity_level_visible: Optional[bool] = None
    
    # 医療情報
    medical_info_level: Optional[PrivacyLevel] = None
    medical_conditions_visible: Optional[bool] = None
    medications_visible: Optional[bool] = None
    allergies_visible: Optional[bool] = None
    doctor_info_visible: Optional[bool] = None
    insurance_visible: Optional[bool] = None
    
    # 緊急連絡先
    emergency_contact_level: Optional[PrivacyLevel] = None
    emergency_contact_visible: Optional[bool] = None
    
    # 身体測定
    body_measurements_level: Optional[PrivacyLevel] = None
    body_measurements_visible: Optional[bool] = None
    
    # バイタルサイン
    vital_signs_level: Optional[PrivacyLevel] = None
    vital_signs_visible: Optional[bool] = None
    
    # データ共有
    allow_data_sharing: Optional[bool] = None
    share_with_healthcare_providers: Optional[bool] = None
    share_with_family: Optional[bool] = None
    share_with_friends: Optional[bool] = None
    
    # 研究参加
    allow_research_participation: Optional[bool] = None
    allow_anonymous_statistics: Optional[bool] = None

class PrivacySettingsResponse(SQLModel):
    """プライバシー設定レスポンス"""
    user_id: int
    settings: UserPrivacySettings
    summary: dict  # 設定の要約

class DataAccessRequest(SQLModel, table=True):
    """データアクセス要求"""
    __tablename__ = "data_access_requests"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    requester_user_id: int = Field(foreign_key="accounts.id")
    target_user_id: int = Field(foreign_key="accounts.id")
    requested_data_categories: str = Field(default="[]")  # JSON文字列として保存
    request_reason: str = Field(max_length=500)
    status: str = Field(default="pending")  # pending, approved, denied
    created_at: datetime = Field(default_factory=datetime.utcnow)
    responded_at: Optional[datetime] = None
    response_message: Optional[str] = None

class DataAccessRequestCreate(SQLModel):
    """データアクセス要求作成用スキーマ"""
    target_user_id: int
    requested_data_categories: List[DataCategory]
    request_reason: str

class DataAccessRequestResponse(SQLModel):
    """データアクセス要求応答用スキーマ"""
    request_id: int
    status: str
    response_message: Optional[str] = None
