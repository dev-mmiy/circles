"""
拡張ユーザープロファイル管理のデータモデル
生年月日、性別、血液型、地域、健康データ履歴を管理
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


class Gender(str, Enum):
    """性別の列挙型"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class BloodType(str, Enum):
    """血液型の列挙型"""
    A = "A"
    B = "B"
    AB = "AB"
    O = "O"
    UNKNOWN = "unknown"


class ActivityLevel(str, Enum):
    """活動レベルの列挙型"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class UserProfileExtended(SQLModel, table=True):
    """拡張ユーザープロファイル"""
    __tablename__ = "user_profiles_extended"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="account.id", index=True)
    birth_date: Optional[date] = Field(default=None, description="生年月日")
    gender: Optional[Gender] = Field(default=None, description="性別")
    blood_type: Optional[BloodType] = Field(default=None, description="血液型")
    region: Optional[str] = Field(default=None, max_length=100, description="住んでいる地域")
    
    # 健康管理関連属性
    height_cm: Optional[float] = Field(default=None, description="身長（cm）")
    target_weight_kg: Optional[float] = Field(default=None, description="目標体重（kg）")
    target_body_fat_percentage: Optional[float] = Field(default=None, description="目標体脂肪率（%）")
    activity_level: Optional[ActivityLevel] = Field(default=None, description="活動レベル")
    
    # 医療情報
    medical_conditions: Optional[str] = Field(default=None, description="既往歴・持病")
    medications: Optional[str] = Field(default=None, description="服用薬")
    allergies: Optional[str] = Field(default=None, description="アレルギー")
    
    # 緊急連絡先・医療関係者情報
    emergency_contact_name: Optional[str] = Field(default=None, max_length=100, description="緊急連絡先氏名")
    emergency_contact_phone: Optional[str] = Field(default=None, max_length=20, description="緊急連絡先電話番号")
    doctor_name: Optional[str] = Field(default=None, max_length=100, description="主治医氏名")
    doctor_phone: Optional[str] = Field(default=None, max_length=20, description="主治医電話番号")
    insurance_number: Optional[str] = Field(default=None, max_length=50, description="保険証番号")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # リレーション
    body_measurements: List["BodyMeasurement"] = Relationship(back_populates="user_profile")
    vital_signs: List["VitalSign"] = Relationship(back_populates="user_profile")


class BodyMeasurement(SQLModel, table=True):
    """体重・体脂肪率履歴"""
    __tablename__ = "body_measurements"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="account.id", index=True)
    measurement_date: datetime = Field(description="測定日時")
    weight_kg: Optional[float] = Field(default=None, description="体重（kg）")
    body_fat_percentage: Optional[float] = Field(default=None, description="体脂肪率（%）")
    notes: Optional[str] = Field(default=None, description="メモ")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # リレーション
    user_profile: Optional[UserProfileExtended] = Relationship(back_populates="body_measurements")


class VitalSign(SQLModel, table=True):
    """血圧・心拍数履歴"""
    __tablename__ = "vital_signs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="account.id", index=True)
    measurement_date: datetime = Field(description="測定日時")
    body_temperature: Optional[float] = Field(default=None, description="体温（℃）")
    systolic_bp: Optional[int] = Field(default=None, description="収縮期血圧")
    diastolic_bp: Optional[int] = Field(default=None, description="拡張期血圧")
    heart_rate: Optional[int] = Field(default=None, description="心拍数")
    notes: Optional[str] = Field(default=None, description="メモ")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # リレーション
    user_profile: Optional[UserProfileExtended] = Relationship(back_populates="vital_signs")


# Pydanticスキーマ（API用）
class UserProfileExtendedBase(SQLModel):
    """拡張プロファイル基本スキーマ"""
    birth_date: Optional[date] = None
    gender: Optional[Gender] = None
    blood_type: Optional[BloodType] = None
    region: Optional[str] = None
    
    # 新しく追加する健康関連属性
    height_cm: Optional[float] = None
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


class UserProfileExtendedCreate(UserProfileExtendedBase):
    """拡張プロファイル作成スキーマ"""
    pass


class UserProfileExtendedRead(UserProfileExtendedBase):
    """拡張プロファイル読み取りスキーマ"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class UserProfileExtendedUpdate(UserProfileExtendedBase):
    """拡張プロファイル更新スキーマ"""
    pass


class BodyMeasurementBase(SQLModel):
    """体重測定基本スキーマ"""
    measurement_date: datetime
    weight_kg: Optional[float] = None
    body_fat_percentage: Optional[float] = None
    notes: Optional[str] = None


class BodyMeasurementCreate(BodyMeasurementBase):
    """体重測定作成スキーマ"""
    pass


class BodyMeasurementRead(BodyMeasurementBase):
    """体重測定読み取りスキーマ"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class BodyMeasurementUpdate(BodyMeasurementBase):
    """体重測定更新スキーマ"""
    pass


class VitalSignBase(SQLModel):
    """バイタルサイン基本スキーマ"""
    measurement_date: datetime
    body_temperature: Optional[float] = None
    systolic_bp: Optional[int] = None
    diastolic_bp: Optional[int] = None
    heart_rate: Optional[int] = None
    notes: Optional[str] = None


class VitalSignCreate(VitalSignBase):
    """バイタルサイン作成スキーマ"""
    pass


class VitalSignRead(VitalSignBase):
    """バイタルサイン読み取りスキーマ"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class VitalSignUpdate(VitalSignBase):
    """バイタルサイン更新スキーマ"""
    pass


# 統計用スキーマ
class HealthStats(SQLModel):
    """健康統計スキーマ"""
    latest_weight: Optional[float] = None
    latest_body_fat: Optional[float] = None
    latest_temperature: Optional[float] = None
    latest_systolic_bp: Optional[int] = None
    latest_diastolic_bp: Optional[int] = None
    latest_heart_rate: Optional[int] = None
    measurement_count: int = 0
    last_measurement_date: Optional[datetime] = None
