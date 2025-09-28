"""
Internationalized SQLModel models for the healthcare community platform.
Supports multiple languages, timezones, and regional settings.
"""

from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import List, Optional, Dict, Any
from sqlmodel import SQLModel, Field as SQLField, Relationship, create_engine, Session, select
from pydantic import BaseModel, Field
import json


# =====================================================================
# Enums for internationalization
# =====================================================================

class LanguageCode(str, Enum):
    """Supported language codes following ISO 639-1 standard."""
    ENGLISH = "en"
    JAPANESE = "ja"
    CHINESE_SIMPLIFIED = "zh-CN"
    CHINESE_TRADITIONAL = "zh-TW"
    KOREAN = "ko"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    ARABIC = "ar"
    HINDI = "hi"


class CountryCode(str, Enum):
    """Supported country codes following ISO 3166-1 alpha-2 standard."""
    UNITED_STATES = "US"
    JAPAN = "JP"
    CHINA = "CN"
    SOUTH_KOREA = "KR"
    UNITED_KINGDOM = "GB"
    CANADA = "CA"
    AUSTRALIA = "AU"
    GERMANY = "DE"
    FRANCE = "FR"
    SPAIN = "ES"
    ITALY = "IT"
    BRAZIL = "BR"
    INDIA = "IN"
    RUSSIA = "RU"
    SAUDI_ARABIA = "SA"


class TimezoneCode(str, Enum):
    """Common timezone codes."""
    UTC = "UTC"
    TOKYO = "Asia/Tokyo"
    NEW_YORK = "America/New_York"
    LONDON = "Europe/London"
    PARIS = "Europe/Paris"
    BEIJING = "Asia/Shanghai"
    SEOUL = "Asia/Seoul"
    SYDNEY = "Australia/Sydney"
    LOS_ANGELES = "America/Los_Angeles"
    CHICAGO = "America/Chicago"
    DENVER = "America/Denver"


class DateFormat(str, Enum):
    """Date format options."""
    ISO = "YYYY-MM-DD"
    US = "MM/DD/YYYY"
    EU = "DD/MM/YYYY"
    JAPAN = "YYYY年MM月DD日"


class TimeFormat(str, Enum):
    """Time format options."""
    HOUR_24 = "24h"
    HOUR_12 = "12h"


class MeasurementUnit(str, Enum):
    """Measurement unit systems."""
    METRIC = "metric"
    IMPERIAL = "imperial"


class CurrencyCode(str, Enum):
    """Currency codes following ISO 4217."""
    USD = "USD"
    JPY = "JPY"
    EUR = "EUR"
    GBP = "GBP"
    CNY = "CNY"
    KRW = "KRW"
    CAD = "CAD"
    AUD = "AUD"
    BRL = "BRL"
    INR = "INR"
    RUB = "RUB"
    SAR = "SAR"


class TranslationNamespace(str, Enum):
    """Translation namespaces for organizing translations."""
    UI = "ui"
    MEDICAL = "medical"
    COMMUNITY = "community"
    RESEARCH = "research"
    VALIDATION = "validation"
    ERROR = "error"


# =====================================================================
# Core models (Internationalized)
# =====================================================================

class Account(SQLModel, table=True):
    """Tenant/Account management with internationalization."""
    __tablename__ = "account"
    __table_args__ = {"schema": "core"}
    
    id: Optional[int] = SQLField(default=None, primary_key=True)
    name: str
    plan: str = SQLField(default="free")
    country: CountryCode = SQLField(default=CountryCode.UNITED_STATES)
    timezone: TimezoneCode = SQLField(default=TimezoneCode.UTC)
    is_active: bool = SQLField(default=True)
    created_at: datetime = SQLField(default_factory=datetime.utcnow)


class AppUser(SQLModel, table=True):
    """User management with internationalization."""
    __tablename__ = "app_user"
    __table_args__ = {"schema": "core"}
    
    id: Optional[int] = SQLField(default=None, primary_key=True)
    account_id: int = SQLField(foreign_key="core.account.id")
    email: str = SQLField(unique=True)
    email_verified: bool = SQLField(default=False)
    display_name: Optional[str] = None
    preferred_language: LanguageCode = SQLField(default=LanguageCode.ENGLISH)
    country: CountryCode = SQLField(default=CountryCode.UNITED_STATES)
    timezone: TimezoneCode = SQLField(default=TimezoneCode.UTC)
    date_format: DateFormat = SQLField(default=DateFormat.ISO)
    time_format: TimeFormat = SQLField(default=TimeFormat.HOUR_24)
    currency: CurrencyCode = SQLField(default=CurrencyCode.USD)
    measurement_unit: MeasurementUnit = SQLField(default=MeasurementUnit.METRIC)
    pii_minimized: bool = SQLField(default=False)
    is_active: bool = SQLField(default=True)
    created_at: datetime = SQLField(default_factory=datetime.utcnow)
    
    # Relationships
    account: Optional[Account] = Relationship(back_populates="users")
    profile: Optional["UserProfile"] = Relationship(back_populates="user")
    observations: List["Observation"] = Relationship(back_populates="user")
    medication_plans: List["MedicationPlan"] = Relationship(back_populates="user")
    posts: List["Post"] = Relationship(back_populates="user")
    comments: List["Comment"] = Relationship(back_populates="user")


class UserProfile(SQLModel, table=True):
    """User profile with internationalization."""
    __tablename__ = "user_profile"
    __table_args__ = {"schema": "core"}
    
    user_id: int = SQLField(foreign_key="core.app_user.id", primary_key=True)
    nickname: Optional[str] = None
    timezone: str = SQLField(default="UTC")
    region: Optional[str] = None
    emergency_contact: Optional[Dict[str, Any]] = SQLField(default=None, sa_column_kwargs={"type_": "JSON"})
    preferences: Dict[str, Any] = SQLField(default_factory=dict, sa_column_kwargs={"type_": "JSON"})
    updated_at: datetime = SQLField(default_factory=datetime.utcnow)
    
    # Relationships
    user: Optional[AppUser] = Relationship(back_populates="profile")


class Role(SQLModel, table=True):
    """User roles."""
    __tablename__ = "role"
    __table_args__ = {"schema": "core"}
    
    code: str = SQLField(primary_key=True)
    description: str


class UserRole(SQLModel, table=True):
    """User role assignments."""
    __tablename__ = "user_role"
    __table_args__ = {"schema": "core"}
    
    user_id: int = SQLField(foreign_key="core.app_user.id", primary_key=True)
    role_code: str = SQLField(foreign_key="core.role.code", primary_key=True)
    granted_at: datetime = SQLField(default_factory=datetime.utcnow)


# =====================================================================
# Health models (Internationalized)
# =====================================================================

class ConsentScope(SQLModel, table=True):
    """Consent scopes."""
    __tablename__ = "consent_scope"
    __table_args__ = {"schema": "health"}
    
    code: str = SQLField(primary_key=True)
    description: str


class Consent(SQLModel, table=True):
    """User consent records with internationalization."""
    __tablename__ = "consent"
    __table_args__ = {"schema": "health"}
    
    id: Optional[int] = SQLField(default=None, primary_key=True)
    user_id: int = SQLField(foreign_key="core.app_user.id")
    scope_code: str = SQLField(foreign_key="health.consent_scope.code")
    version: str
    language: LanguageCode = SQLField(default=LanguageCode.ENGLISH)
    granted: bool
    granted_at: datetime = SQLField(default_factory=datetime.utcnow)
    revoked_at: Optional[datetime] = None
    revocation_reason: Optional[str] = None
    revoked_by: Optional[int] = SQLField(foreign_key="core.app_user.id", default=None)
    expires_at: Optional[datetime] = None


class ConditionMaster(SQLModel, table=True):
    """Medical condition master with internationalization."""
    __tablename__ = "condition_master"
    __table_args__ = {"schema": "health"}
    
    id: Optional[int] = SQLField(default=None, primary_key=True)
    icd10_code: Optional[str] = None
    snomed_code: Optional[str] = None
    name_localized: Dict[str, str] = SQLField(sa_column_kwargs={"type_": "JSON"})
    category: str
    severity_levels: Optional[Dict[str, Any]] = SQLField(default=None, sa_column_kwargs={"type_": "JSON"})
    is_active: bool = SQLField(default=True)
    created_at: datetime = SQLField(default_factory=datetime.utcnow)


class DrugMaster(SQLModel, table=True):
    """Drug master with internationalization."""
    __tablename__ = "drug_master"
    __table_args__ = {"schema": "health"}
    
    id: Optional[int] = SQLField(default=None, primary_key=True)
    atc_code: Optional[str] = None
    ndc_code: Optional[str] = None
    jp_code: Optional[str] = None
    eu_code: Optional[str] = None
    generic_name: str
    brand_names: Optional[Dict[str, List[str]]] = SQLField(default=None, sa_column_kwargs={"type_": "JSON"})
    active_ingredient: Optional[str] = None
    dosage_form: Optional[str] = None
    strength: Optional[str] = None
    manufacturer: Optional[str] = None
    is_active: bool = SQLField(default=True)
    created_at: datetime = SQLField(default_factory=datetime.utcnow)


class Observation(SQLModel, table=True):
    """Medical observations with internationalization."""
    __tablename__ = "observation"
    __table_args__ = {"schema": "health"}
    
    id: Optional[int] = SQLField(default=None, primary_key=True)
    account_id: int = SQLField(foreign_key="core.account.id")
    user_id: int = SQLField(foreign_key="core.app_user.id")
    type: str
    value_json: Dict[str, Any] = SQLField(sa_column_kwargs={"type_": "JSON"})
    observed_at: datetime = SQLField(default_factory=datetime.utcnow)
    timezone: TimezoneCode = SQLField(default=TimezoneCode.UTC)
    language: LanguageCode = SQLField(default=LanguageCode.ENGLISH)
    created_at: datetime = SQLField(default_factory=datetime.utcnow)
    
    # Relationships
    user: Optional[AppUser] = Relationship(back_populates="observations")


class MedicationPlan(SQLModel, table=True):
    """Medication plans with internationalization."""
    __tablename__ = "medication_plan"
    __table_args__ = {"schema": "health"}
    
    id: Optional[int] = SQLField(default=None, primary_key=True)
    account_id: int = SQLField(foreign_key="core.account.id")
    user_id: int = SQLField(foreign_key="core.app_user.id")
    drug_id: Optional[int] = SQLField(foreign_key="health.drug_master.id", default=None)
    drug_code: str
    drug_name: Optional[str] = None
    drug_name_localized: Optional[Dict[str, str]] = SQLField(default=None, sa_column_kwargs={"type_": "JSON"})
    dose: str
    schedule_json: Dict[str, Any] = SQLField(sa_column_kwargs={"type_": "JSON"})
    start_date: date
    end_date: Optional[date] = None
    notes: Optional[str] = None
    language: LanguageCode = SQLField(default=LanguageCode.ENGLISH)
    created_at: datetime = SQLField(default_factory=datetime.utcnow)
    
    # Relationships
    user: Optional[AppUser] = Relationship(back_populates="medication_plans")
    events: List["MedicationEvent"] = Relationship(back_populates="plan")


class MedicationEvent(SQLModel, table=True):
    """Medication events with internationalization."""
    __tablename__ = "medication_event"
    __table_args__ = {"schema": "health"}
    
    id: Optional[int] = SQLField(default=None, primary_key=True)
    plan_id: int = SQLField(foreign_key="health.medication_plan.id")
    taken_at: datetime = SQLField(default_factory=datetime.utcnow)
    timezone: TimezoneCode = SQLField(default=TimezoneCode.UTC)
    adherence_score: Optional[float] = None
    notes: Optional[str] = None
    language: LanguageCode = SQLField(default=LanguageCode.ENGLISH)
    
    # Relationships
    plan: Optional[MedicationPlan] = Relationship(back_populates="events")


class ProReport(SQLModel, table=True):
    """Patient-reported outcomes with internationalization."""
    __tablename__ = "pro_report"
    __table_args__ = {"schema": "health"}
    
    id: Optional[int] = SQLField(default=None, primary_key=True)
    account_id: int = SQLField(foreign_key="core.account.id")
    user_id: int = SQLField(foreign_key="core.app_user.id")
    questionnaire: str
    answers_json: Dict[str, Any] = SQLField(sa_column_kwargs={"type_": "JSON"})
    reported_at: datetime = SQLField(default_factory=datetime.utcnow)
    language: LanguageCode = SQLField(default=LanguageCode.ENGLISH)
    created_at: datetime = SQLField(default_factory=datetime.utcnow)


# =====================================================================
# Community models (Internationalized)
# =====================================================================

class Room(SQLModel, table=True):
    """Community rooms with internationalization."""
    __tablename__ = "room"
    __table_args__ = {"schema": "community"}
    
    id: Optional[int] = SQLField(default=None, primary_key=True)
    account_id: int = SQLField(foreign_key="core.account.id")
    slug: str = SQLField(unique=True)
    is_multilingual: bool = SQLField(default=False)
    primary_language: LanguageCode = SQLField(default=LanguageCode.ENGLISH)
    created_at: datetime = SQLField(default_factory=datetime.utcnow)
    
    # Relationships
    content: List["RoomContent"] = Relationship(back_populates="room")
    posts: List["Post"] = Relationship(back_populates="room")


class RoomContent(SQLModel, table=True):
    """Room content in multiple languages."""
    __tablename__ = "room_content"
    __table_args__ = {"schema": "community"}
    
    room_id: int = SQLField(foreign_key="community.room.id", primary_key=True)
    language: LanguageCode = SQLField(primary_key=True)
    title: str
    description: Optional[str] = None
    is_primary: bool = SQLField(default=False)
    created_at: datetime = SQLField(default_factory=datetime.utcnow)
    updated_at: datetime = SQLField(default_factory=datetime.utcnow)
    
    # Relationships
    room: Optional[Room] = Relationship(back_populates="content")


class RoomMember(SQLModel, table=True):
    """Room membership."""
    __tablename__ = "room_member"
    __table_args__ = {"schema": "community"}
    
    room_id: int = SQLField(foreign_key="community.room.id", primary_key=True)
    user_id: int = SQLField(foreign_key="core.app_user.id", primary_key=True)
    role: str = SQLField(default="member")
    joined_at: datetime = SQLField(default_factory=datetime.utcnow)


class Post(SQLModel, table=True):
    """Community posts with internationalization."""
    __tablename__ = "post"
    __table_args__ = {"schema": "community"}
    
    id: Optional[int] = SQLField(default=None, primary_key=True)
    room_id: int = SQLField(foreign_key="community.room.id")
    user_id: int = SQLField(foreign_key="core.app_user.id")
    is_multilingual: bool = SQLField(default=False)
    primary_language: LanguageCode = SQLField(default=LanguageCode.ENGLISH)
    tags: List[str] = SQLField(default_factory=list, sa_column_kwargs={"type_": "ARRAY"})
    created_at: datetime = SQLField(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Relationships
    room: Optional[Room] = Relationship(back_populates="posts")
    user: Optional[AppUser] = Relationship(back_populates="posts")
    content: List["PostContent"] = Relationship(back_populates="post")
    comments: List["Comment"] = Relationship(back_populates="post")


class PostContent(SQLModel, table=True):
    """Post content in multiple languages."""
    __tablename__ = "post_content"
    __table_args__ = {"schema": "community"}
    
    post_id: int = SQLField(foreign_key="community.post.id", primary_key=True)
    language: LanguageCode = SQLField(primary_key=True)
    title: Optional[str] = None
    body_md: str
    is_primary: bool = SQLField(default=False)
    created_at: datetime = SQLField(default_factory=datetime.utcnow)
    updated_at: datetime = SQLField(default_factory=datetime.utcnow)
    
    # Relationships
    post: Optional[Post] = Relationship(back_populates="content")


class Comment(SQLModel, table=True):
    """Comments with internationalization."""
    __tablename__ = "comment"
    __table_args__ = {"schema": "community"}
    
    id: Optional[int] = SQLField(default=None, primary_key=True)
    post_id: int = SQLField(foreign_key="community.post.id")
    user_id: int = SQLField(foreign_key="core.app_user.id")
    language: LanguageCode = SQLField(default=LanguageCode.ENGLISH)
    body_md: str
    created_at: datetime = SQLField(default_factory=datetime.utcnow)
    
    # Relationships
    post: Optional[Post] = Relationship(back_populates="comments")
    user: Optional[AppUser] = Relationship(back_populates="comments")


class Report(SQLModel, table=True):
    """Reports with internationalization."""
    __tablename__ = "report"
    __table_args__ = {"schema": "community"}
    
    id: Optional[int] = SQLField(default=None, primary_key=True)
    reporter_id: int = SQLField(foreign_key="core.app_user.id")
    target_type: str = SQLField(constraint="CHECK (target_type IN ('post','comment','user'))")
    target_id: int
    reason: Optional[str] = None
    language: LanguageCode = SQLField(default=LanguageCode.ENGLISH)
    created_at: datetime = SQLField(default_factory=datetime.utcnow)


class ModerationAction(SQLModel, table=True):
    """Moderation actions with internationalization."""
    __tablename__ = "moderation_action"
    __table_args__ = {"schema": "community"}
    
    id: Optional[int] = SQLField(default=None, primary_key=True)
    moderator_id: int = SQLField(foreign_key="core.app_user.id")
    target_type: str = SQLField(constraint="CHECK (target_type IN ('post','comment','user'))")
    target_id: int
    action: str
    reason: Optional[str] = None
    language: LanguageCode = SQLField(default=LanguageCode.ENGLISH)
    created_at: datetime = SQLField(default_factory=datetime.utcnow)


# =====================================================================
# Research models (Internationalized)
# =====================================================================

class Trial(SQLModel, table=True):
    """Clinical trials with internationalization."""
    __tablename__ = "trial"
    __table_args__ = {"schema": "research"}
    
    id: Optional[int] = SQLField(default=None, primary_key=True)
    registry_id: Optional[str] = None
    is_multilingual: bool = SQLField(default=False)
    primary_language: LanguageCode = SQLField(default=LanguageCode.ENGLISH)
    condition: List[str] = SQLField(default_factory=list, sa_column_kwargs={"type_": "ARRAY"})
    phase: Optional[str] = None
    criteria_json: Dict[str, Any] = SQLField(sa_column_kwargs={"type_": "JSON"})
    locations_json: Optional[Dict[str, Any]] = SQLField(default=None, sa_column_kwargs={"type_": "JSON"})
    start_date: Optional[date] = None
    completion_date: Optional[date] = None
    source_url: Optional[str] = None
    imported_at: datetime = SQLField(default_factory=datetime.utcnow)
    
    # Relationships
    content: List["TrialContent"] = Relationship(back_populates="trial")
    sites: List["TrialSite"] = Relationship(back_populates="trial")


class TrialContent(SQLModel, table=True):
    """Trial content in multiple languages."""
    __tablename__ = "trial_content"
    __table_args__ = {"schema": "research"}
    
    trial_id: int = SQLField(foreign_key="research.trial.id", primary_key=True)
    language: LanguageCode = SQLField(primary_key=True)
    title: str
    summary: Optional[str] = None
    description: Optional[str] = None
    is_primary: bool = SQLField(default=False)
    created_at: datetime = SQLField(default_factory=datetime.utcnow)
    updated_at: datetime = SQLField(default_factory=datetime.utcnow)
    
    # Relationships
    trial: Optional[Trial] = Relationship(back_populates="content")


class TrialSite(SQLModel, table=True):
    """Trial sites with internationalization."""
    __tablename__ = "trial_site"
    __table_args__ = {"schema": "research"}
    
    id: Optional[int] = SQLField(default=None, primary_key=True)
    trial_id: int = SQLField(foreign_key="research.trial.id")
    name: Optional[str] = None
    address: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    country: Optional[CountryCode] = None
    language: Optional[LanguageCode] = None
    
    # Relationships
    trial: Optional[Trial] = Relationship(back_populates="sites")
    content: List["TrialSiteContent"] = Relationship(back_populates="site")


class TrialSiteContent(SQLModel, table=True):
    """Trial site content in multiple languages."""
    __tablename__ = "trial_site_content"
    __table_args__ = {"schema": "research"}
    
    site_id: int = SQLField(foreign_key="research.trial_site.id", primary_key=True)
    language: LanguageCode = SQLField(primary_key=True)
    name: str
    address: Optional[str] = None
    contact_info: Optional[Dict[str, Any]] = SQLField(default=None, sa_column_kwargs={"type_": "JSON"})
    
    # Relationships
    site: Optional[TrialSite] = Relationship(back_populates="content")


class TrialMatch(SQLModel, table=True):
    """Trial matches with internationalization."""
    __tablename__ = "trial_match"
    __table_args__ = {"schema": "research"}
    
    id: Optional[int] = SQLField(default=None, primary_key=True)
    user_id: int = SQLField(foreign_key="core.app_user.id")
    trial_id: int = SQLField(foreign_key="research.trial.id")
    score: float
    reasons: Optional[Dict[str, Any]] = SQLField(default=None, sa_column_kwargs={"type_": "JSON"})
    matched_at: datetime = SQLField(default_factory=datetime.utcnow)
    status: str = SQLField(default="suggested", constraint="CHECK (status IN ('suggested', 'contact_requested', 'referred', 'declined', 'expired'))")
    expires_at: Optional[datetime] = None
    language: LanguageCode = SQLField(default=LanguageCode.ENGLISH)


class TrialReferral(SQLModel, table=True):
    """Trial referrals with internationalization."""
    __tablename__ = "trial_referral"
    __table_args__ = {"schema": "research"}
    
    id: Optional[int] = SQLField(default=None, primary_key=True)
    match_id: int = SQLField(foreign_key="research.trial_match.id")
    coordinator_id: Optional[int] = SQLField(foreign_key="core.app_user.id", default=None)
    contact_method: Optional[str] = None
    consent_confirmed: bool = SQLField(default=False)
    note: Optional[str] = None
    language: LanguageCode = SQLField(default=LanguageCode.ENGLISH)
    created_at: datetime = SQLField(default_factory=datetime.utcnow)


# =====================================================================
# Pydantic schemas for API (Internationalized)
# =====================================================================

class UserLocaleCreate(BaseModel):
    """User locale preferences for creation."""
    language: LanguageCode = LanguageCode.ENGLISH
    country: CountryCode = CountryCode.UNITED_STATES
    timezone: TimezoneCode = TimezoneCode.UTC
    date_format: DateFormat = DateFormat.ISO
    time_format: TimeFormat = TimeFormat.HOUR_24
    currency: CurrencyCode = CurrencyCode.USD
    measurement_unit: MeasurementUnit = MeasurementUnit.METRIC


class UserLocaleRead(BaseModel):
    """User locale preferences for reading."""
    language: LanguageCode
    country: CountryCode
    timezone: TimezoneCode
    date_format: DateFormat
    time_format: TimeFormat
    currency: CurrencyCode
    measurement_unit: MeasurementUnit
    
    class Config:
        from_attributes = True


class AppUserCreate(BaseModel):
    """User creation with internationalization."""
    email: str
    display_name: Optional[str] = None
    preferred_language: LanguageCode = LanguageCode.ENGLISH
    country: CountryCode = CountryCode.UNITED_STATES
    timezone: TimezoneCode = TimezoneCode.UTC
    date_format: DateFormat = DateFormat.ISO
    time_format: TimeFormat = TimeFormat.HOUR_24
    currency: CurrencyCode = CurrencyCode.USD
    measurement_unit: MeasurementUnit = MeasurementUnit.METRIC


class AppUserRead(BaseModel):
    """User reading with internationalization."""
    id: int
    email: str
    display_name: Optional[str]
    preferred_language: LanguageCode
    country: CountryCode
    timezone: TimezoneCode
    date_format: DateFormat
    time_format: TimeFormat
    currency: CurrencyCode
    measurement_unit: MeasurementUnit
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ObservationCreate(BaseModel):
    """Observation creation with internationalization."""
    type: str
    value_json: Dict[str, Any]
    observed_at: Optional[datetime] = None
    timezone: TimezoneCode = TimezoneCode.UTC
    language: LanguageCode = LanguageCode.ENGLISH


class ObservationRead(BaseModel):
    """Observation reading with internationalization."""
    id: int
    type: str
    value_json: Dict[str, Any]
    observed_at: datetime
    timezone: TimezoneCode
    language: LanguageCode
    created_at: datetime
    
    class Config:
        from_attributes = True


class MedicationPlanCreate(BaseModel):
    """Medication plan creation with internationalization."""
    drug_code: str
    drug_name: Optional[str] = None
    drug_name_localized: Optional[Dict[str, str]] = None
    dose: str
    schedule_json: Dict[str, Any]
    start_date: date
    end_date: Optional[date] = None
    notes: Optional[str] = None
    language: LanguageCode = LanguageCode.ENGLISH


class MedicationPlanRead(BaseModel):
    """Medication plan reading with internationalization."""
    id: int
    drug_code: str
    drug_name: Optional[str]
    drug_name_localized: Optional[Dict[str, str]]
    dose: str
    schedule_json: Dict[str, Any]
    start_date: date
    end_date: Optional[date]
    notes: Optional[str]
    language: LanguageCode
    created_at: datetime
    
    class Config:
        from_attributes = True


class PostCreate(BaseModel):
    """Post creation with internationalization."""
    room_id: int
    is_multilingual: bool = False
    primary_language: LanguageCode = LanguageCode.ENGLISH
    tags: List[str] = []
    content: Dict[LanguageCode, Dict[str, str]]  # {language: {title, body_md}}


class PostRead(BaseModel):
    """Post reading with internationalization."""
    id: int
    room_id: int
    user_id: int
    is_multilingual: bool
    primary_language: LanguageCode
    tags: List[str]
    content: Dict[LanguageCode, Dict[str, str]]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class TranslationRequest(BaseModel):
    """Translation request."""
    namespace: TranslationNamespace
    key: str
    language: LanguageCode
    context: Optional[str] = None


class TranslationResponse(BaseModel):
    """Translation response."""
    namespace: TranslationNamespace
    key: str
    language: LanguageCode
    value: str
    context: Optional[str]
    is_approved: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# =====================================================================
# Utility functions for internationalization
# =====================================================================

def get_user_locale(user: AppUser) -> UserLocaleRead:
    """Get user's locale preferences."""
    return UserLocaleRead(
        language=user.preferred_language,
        country=user.country,
        timezone=user.timezone,
        date_format=user.date_format,
        time_format=user.time_format,
        currency=user.currency,
        measurement_unit=user.measurement_unit
    )


def format_datetime_for_user(dt: datetime, user: AppUser) -> str:
    """Format datetime according to user's preferences."""
    # This would be implemented with proper timezone conversion
    # and formatting based on user preferences
    return dt.isoformat()


def format_number_for_user(number: float, user: AppUser) -> str:
    """Format number according to user's regional preferences."""
    # This would be implemented with proper number formatting
    # based on user's country and language
    return f"{number:,.2f}"


def format_currency_for_user(amount: float, user: AppUser) -> str:
    """Format currency according to user's preferences."""
    # This would be implemented with proper currency formatting
    # based on user's currency and regional preferences
    currency_symbols = {
        CurrencyCode.USD: "$",
        CurrencyCode.JPY: "¥",
        CurrencyCode.EUR: "€",
        CurrencyCode.GBP: "£",
        CurrencyCode.CNY: "¥",
        CurrencyCode.KRW: "₩",
    }
    symbol = currency_symbols.get(user.currency, "$")
    formatted_number = format_number_for_user(amount, user)
    return f"{symbol}{formatted_number}"
