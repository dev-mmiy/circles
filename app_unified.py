"""
Unified FastAPI application for the healthcare community platform.
Integrates existing functionality with internationalization support.
"""

from __future__ import annotations

from datetime import datetime, date
from enum import Enum
from typing import List, Optional, Dict, Any

from sqlmodel import SQLModel, Field as SQLField, Relationship, create_engine, Session, select
from fastapi import FastAPI, HTTPException, Depends, Query, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os

# Import internationalization modules
from i18n_config import (
    LanguageCode, CountryCode, TimezoneCode, DateFormat, TimeFormat, 
    MeasurementUnit, CurrencyCode, TranslationNamespace, UserLocaleRead,
    get_user_locale_from_headers, format_datetime, format_number, format_currency
)
# from models_i18n import (
#     AppUser, AppUserCreate, AppUserRead, Observation, ObservationCreate, ObservationRead,
#     MedicationPlan, MedicationPlanCreate, MedicationPlanRead, Post, PostCreate, PostRead,
#     TranslationRequest, TranslationResponse, Account, Role, UserRole
# )
# from translation_service import TranslationService, LocalizationService, ContentTranslationService
# from i18n_utils import (
#     I18nUtils, LocalizationUtils, ContentUtils, ValidationUtils,
#     get_user_locale_from_request, format_content_for_user, format_datetime_for_user,
#     format_currency_for_user, validate_translation_quality
# )

# Set ORIGINS
ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "http://127.0.0.1:3000,http://localhost:3000").split(",")

# ----------------------------------------------------------------------------
# Database setup
# ----------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app_unified.db")

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})


def get_session():
    with Session(engine) as session:
        yield session


# ----------------------------------------------------------------------------
# Legacy models (for backward compatibility)
# ----------------------------------------------------------------------------

class JournalSymptom(SQLModel, table=True):
    """Legacy journal symptom model."""
    id: Optional[int] = SQLField(default=None, primary_key=True)
    journal_id: int = SQLField(foreign_key="journal.id")
    name: str
    score: int = SQLField(ge=0, le=10)
    language: LanguageCode = SQLField(default=LanguageCode.ENGLISH)
    
    journal: Optional["Journal"] = Relationship(back_populates="symptoms")


class Journal(SQLModel, table=True):
    """Legacy journal model with internationalization."""
    id: Optional[int] = SQLField(default=None, primary_key=True)
    log_date: date = SQLField(index=True, default_factory=lambda: datetime.utcnow().date())
    note: Optional[str] = None
    weight_kg: Optional[float] = SQLField(default=None, ge=0)
    systolic_bp: Optional[int] = SQLField(default=None, ge=0)
    diastolic_bp: Optional[int] = SQLField(default=None, ge=0)
    mood: Optional[int] = SQLField(default=None, ge=0, le=10)
    language: LanguageCode = SQLField(default=LanguageCode.ENGLISH)
    timezone: TimezoneCode = SQLField(default=TimezoneCode.UTC)
    
    symptoms: List[JournalSymptom] = Relationship(back_populates="journal")


class Medication(SQLModel, table=True):
    """Legacy medication model with internationalization."""
    id: Optional[int] = SQLField(default=None, primary_key=True)
    name: str
    name_localized: Optional[Dict[str, str]] = SQLField(default=None, sa_column_kwargs={"type_": "JSON"})
    dosage: Optional[str] = None
    schedule: Optional[str] = None
    language: LanguageCode = SQLField(default=LanguageCode.ENGLISH)
    
    logs: List["MedicationLog"] = Relationship(back_populates="medication")


class MedicationLog(SQLModel, table=True):
    """Legacy medication log model with internationalization."""
    id: Optional[int] = SQLField(default=None, primary_key=True)
    medication_id: int = SQLField(foreign_key="medication.id")
    taken_at: datetime = SQLField(default_factory=datetime.utcnow, index=True)
    status: str = SQLField(default="taken")
    timezone: TimezoneCode = SQLField(default=TimezoneCode.UTC)
    language: LanguageCode = SQLField(default=LanguageCode.ENGLISH)
    
    medication: Optional[Medication] = Relationship(back_populates="logs")


class GroupVisibility(str, Enum):
    """Group visibility options."""
    public = "public"
    private = "private"


class Group(SQLModel, table=True):
    """Legacy group model with internationalization."""
    id: Optional[int] = SQLField(default=None, primary_key=True)
    name: str
    name_localized: Optional[Dict[str, str]] = SQLField(default=None, sa_column_kwargs={"type_": "JSON"})
    description: Optional[str] = None
    description_localized: Optional[Dict[str, str]] = Field(default=None, sa_column_kwargs={"type_": "JSON"})
    visibility: GroupVisibility = SQLField(default=GroupVisibility.public)
    is_multilingual: bool = SQLField(default=False)
    primary_language: LanguageCode = SQLField(default=LanguageCode.ENGLISH)
    
    posts: List["Post"] = Relationship(back_populates="group")


class Post(SQLModel, table=True):
    """Legacy post model with internationalization."""
    id: Optional[int] = SQLField(default=None, primary_key=True)
    group_id: int = SQLField(foreign_key="group.id")
    created_at: datetime = SQLField(default_factory=datetime.utcnow, index=True)
    title: str
    title_localized: Optional[Dict[str, str]] = Field(default=None, sa_column_kwargs={"type_": "JSON"})
    body: str
    body_localized: Optional[Dict[str, str]] = Field(default=None, sa_column_kwargs={"type_": "JSON"})
    anon: bool = SQLField(default=True)
    is_multilingual: bool = SQLField(default=False)
    primary_language: LanguageCode = SQLField(default=LanguageCode.ENGLISH)
    
    group: Optional[Group] = Relationship(back_populates="posts")


class ReportTargetType(str, Enum):
    """Report target types."""
    post = "post"


class ReportReason(str, Enum):
    """Report reasons."""
    abuse = "abuse"
    medical_misinformation = "medical_misinformation"
    spam = "spam"
    other = "other"


class Report(SQLModel, table=True):
    """Legacy report model with internationalization."""
    id: Optional[int] = SQLField(default=None, primary_key=True)
    target_type: ReportTargetType
    target_id: int
    reason: ReportReason = SQLField(default=ReportReason.other)
    detail: Optional[str] = None
    language: LanguageCode = SQLField(default=LanguageCode.ENGLISH)
    created_at: datetime = SQLField(default_factory=datetime.utcnow)
    status: str = SQLField(default="open")


# ----------------------------------------------------------------------------
# Pydantic schemas (Legacy with internationalization)
# ----------------------------------------------------------------------------

class SymptomIn(BaseModel):
    """Symptom input with internationalization."""
    name: str
    score: int = Field(ge=0, le=10)
    language: LanguageCode = LanguageCode.ENGLISH


class JournalCreate(BaseModel):
    """Journal creation with internationalization."""
    log_date: Optional[date] = None
    note: Optional[str] = None
    weight_kg: Optional[float] = Field(default=None, ge=0)
    systolic_bp: Optional[int] = Field(default=None, ge=0)
    diastolic_bp: Optional[int] = Field(default=None, ge=0)
    mood: Optional[int] = Field(default=None, ge=0, le=10)
    symptoms: List[SymptomIn] = []
    language: LanguageCode = LanguageCode.ENGLISH
    timezone: TimezoneCode = TimezoneCode.UTC


class JournalRead(BaseModel):
    """Journal reading with internationalization."""
    id: int
    log_date: date
    note: Optional[str]
    weight_kg: Optional[float]
    systolic_bp: Optional[int]
    diastolic_bp: Optional[int]
    mood: Optional[int]
    symptoms: List[SymptomIn]
    language: LanguageCode
    timezone: TimezoneCode
    
    class Config:
        from_attributes = True


class MedicationCreate(BaseModel):
    """Medication creation with internationalization."""
    name: str
    name_localized: Optional[Dict[str, str]] = None
    dosage: Optional[str] = None
    schedule: Optional[str] = None
    language: LanguageCode = LanguageCode.ENGLISH


class MedicationRead(BaseModel):
    """Medication reading with internationalization."""
    id: int
    name: str
    name_localized: Optional[Dict[str, str]]
    dosage: Optional[str]
    schedule: Optional[str]
    language: LanguageCode
    
    class Config:
        from_attributes = True


class MedicationLogCreate(BaseModel):
    """Medication log creation with internationalization."""
    status: Optional[str] = Field(default="taken")
    taken_at: Optional[datetime] = None
    timezone: TimezoneCode = TimezoneCode.UTC
    language: LanguageCode = LanguageCode.ENGLISH


class MedicationLogRead(BaseModel):
    """Medication log reading with internationalization."""
    id: int
    medication_id: int
    status: str
    taken_at: datetime
    timezone: TimezoneCode
    language: LanguageCode
    
    class Config:
        from_attributes = True


class GroupCreate(BaseModel):
    """Group creation with internationalization."""
    name: str
    name_localized: Optional[Dict[str, str]] = None
    description: Optional[str] = None
    description_localized: Optional[Dict[str, str]] = None
    visibility: GroupVisibility = GroupVisibility.public
    is_multilingual: bool = False
    primary_language: LanguageCode = LanguageCode.ENGLISH


class GroupRead(BaseModel):
    """Group reading with internationalization."""
    id: int
    name: str
    name_localized: Optional[Dict[str, str]]
    description: Optional[str]
    description_localized: Optional[Dict[str, str]]
    visibility: GroupVisibility
    is_multilingual: bool
    primary_language: LanguageCode
    
    class Config:
        from_attributes = True


class PostCreate(BaseModel):
    """Post creation with internationalization."""
    group_id: int
    title: str
    title_localized: Optional[Dict[str, str]] = None
    body: str
    body_localized: Optional[Dict[str, str]] = None
    anon: bool = True
    is_multilingual: bool = False
    primary_language: LanguageCode = LanguageCode.ENGLISH


class PostRead(BaseModel):
    """Post reading with internationalization."""
    id: int
    group_id: int
    created_at: datetime
    title: str
    title_localized: Optional[Dict[str, str]]
    body: str
    body_localized: Optional[Dict[str, str]]
    anon: bool
    is_multilingual: bool
    primary_language: LanguageCode
    
    class Config:
        from_attributes = True


class ReportCreate(BaseModel):
    """Report creation with internationalization."""
    target_type: ReportTargetType
    target_id: int
    reason: ReportReason = ReportReason.other
    detail: Optional[str] = None
    language: LanguageCode = LanguageCode.ENGLISH


class ReportRead(BaseModel):
    """Report reading with internationalization."""
    id: int
    target_type: ReportTargetType
    target_id: int
    reason: ReportReason
    detail: Optional[str]
    status: str
    language: LanguageCode
    created_at: datetime
    
    class Config:
        from_attributes = True


# ----------------------------------------------------------------------------
# FastAPI app
# ----------------------------------------------------------------------------
app = FastAPI(
    title="Healthcare Community Platform (Unified)",
    description="Unified healthcare community platform with internationalization support",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


# ----------------------------------------------------------------------------
# Internationalization endpoints
# ----------------------------------------------------------------------------

@app.get("/i18n/languages", response_model=List[Dict[str, Any]])
def get_supported_languages():
    """Get list of supported languages."""
    return I18nUtils.get_supported_languages()


@app.get("/i18n/countries", response_model=List[Dict[str, Any]])
def get_supported_countries():
    """Get list of supported countries."""
    return I18nUtils.get_supported_countries()


@app.get("/i18n/locale", response_model=UserLocaleRead)
def get_user_locale(
    accept_language: str = Header(None),
    timezone: Optional[str] = Header(None),
    country: Optional[str] = Header(None)
):
    """Get user locale from request headers."""
    return get_user_locale_from_request(accept_language, timezone, country)


@app.get("/i18n/translation/{namespace}/{key}")
def get_translation(
    namespace: TranslationNamespace,
    key: str,
    language: LanguageCode = LanguageCode.ENGLISH,
    context: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """Get translation for a specific key."""
    translation_service = TranslationService(session)
    value = translation_service.get_translation(namespace, key, language, context)
    return {"namespace": namespace.value, "key": key, "language": language.value, "value": value}


# ----------------------------------------------------------------------------
# Legacy endpoints (with internationalization)
# ----------------------------------------------------------------------------

@app.post("/journals", response_model=JournalRead)
def create_journal(
    payload: JournalCreate, 
    session: Session = Depends(get_session),
    accept_language: str = Header(None),
    timezone: Optional[str] = Header(None)
):
    """Create a new journal entry with internationalization."""
    # Get user locale from headers
    user_locale = get_user_locale_from_request(accept_language, timezone)
    
    journal = Journal(
        log_date=payload.log_date or datetime.utcnow().date(),
        note=payload.note,
        weight_kg=payload.weight_kg,
        systolic_bp=payload.systolic_bp,
        diastolic_bp=payload.diastolic_bp,
        mood=payload.mood,
        language=payload.language,
        timezone=payload.timezone
    )
    session.add(journal)
    session.flush()

    for s in payload.symptoms:
        session.add(JournalSymptom(
            journal_id=journal.id, 
            name=s.name, 
            score=s.score,
            language=s.language
        ))

    session.commit()
    session.refresh(journal)

    return JournalRead(
        id=journal.id,
        log_date=journal.log_date,
        note=journal.note,
        weight_kg=journal.weight_kg,
        systolic_bp=journal.systolic_bp,
        diastolic_bp=journal.diastolic_bp,
        mood=journal.mood,
        symptoms=[SymptomIn(name=s.name, score=s.score, language=s.language) for s in journal.symptoms],
        language=journal.language,
        timezone=journal.timezone
    )


@app.get("/journals", response_model=List[JournalRead])
def list_journals(
    session: Session = Depends(get_session),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    language: LanguageCode = Query(LanguageCode.ENGLISH)
):
    """List journals with internationalization."""
    stmt = select(Journal).where(Journal.language == language.value).order_by(Journal.log_date.desc(), Journal.id.desc())
    if date_from:
        stmt = stmt.where(Journal.log_date >= date_from)
    if date_to:
        stmt = stmt.where(Journal.log_date <= date_to)
    stmt = stmt.offset(offset).limit(limit)

    rows = session.exec(stmt).all()
    out: List[JournalRead] = []
    for j in rows:
        out.append(
            JournalRead(
                id=j.id,
                log_date=j.log_date,
                note=j.note,
                weight_kg=j.weight_kg,
                systolic_bp=j.systolic_bp,
                diastolic_bp=j.diastolic_bp,
                mood=j.mood,
                symptoms=[SymptomIn(name=s.name, score=s.score, language=s.language) for s in j.symptoms],
                language=j.language,
                timezone=j.timezone
            )
        )
    return out


@app.get("/journals/{journal_id}", response_model=JournalRead)
def get_journal(journal_id: int, session: Session = Depends(get_session)):
    """Get a specific journal entry."""
    j = session.get(Journal, journal_id)
    if not j:
        raise HTTPException(404, "Journal not found")
    return JournalRead(
        id=j.id,
        log_date=j.log_date,
        note=j.note,
        weight_kg=j.weight_kg,
        systolic_bp=j.systolic_bp,
        diastolic_bp=j.diastolic_bp,
        mood=j.mood,
        symptoms=[SymptomIn(name=s.name, score=s.score, language=s.language) for s in j.symptoms],
        language=j.language,
        timezone=j.timezone
    )


@app.delete("/journals/{journal_id}")
def delete_journal(journal_id: int, session: Session = Depends(get_session)):
    """Delete a journal entry."""
    j = session.get(Journal, journal_id)
    if not j:
        raise HTTPException(404, "Journal not found")
    session.delete(j)
    session.commit()
    return {"deleted": journal_id}


# ----------------------------------------------------------------------------
# Medications (with internationalization)
# ----------------------------------------------------------------------------

@app.post("/medications", response_model=MedicationRead)
def create_medication(
    payload: MedicationCreate, 
    session: Session = Depends(get_session),
    accept_language: str = Header(None)
):
    """Create a new medication with internationalization."""
    user_locale = get_user_locale_from_request(accept_language)
    
    m = Medication(
        name=payload.name, 
        name_localized=payload.name_localized,
        dosage=payload.dosage, 
        schedule=payload.schedule,
        language=payload.language
    )
    session.add(m)
    session.commit()
    session.refresh(m)
    return m


@app.get("/medications", response_model=List[MedicationRead])
def list_medications(
    session: Session = Depends(get_session),
    language: LanguageCode = Query(LanguageCode.ENGLISH)
):
    """List medications with internationalization."""
    rows = session.exec(select(Medication).where(Medication.language == language.value).order_by(Medication.id.desc())).all()
    return rows


@app.post("/medications/{medication_id}/log", response_model=MedicationLogRead)
def log_medication(
    medication_id: int, 
    payload: MedicationLogCreate, 
    session: Session = Depends(get_session)
):
    """Log medication intake with internationalization."""
    m = session.get(Medication, medication_id)
    if not m:
        raise HTTPException(404, "Medication not found")
    log = MedicationLog(
        medication_id=medication_id,
        status=payload.status or "taken",
        taken_at=payload.taken_at or datetime.utcnow(),
        timezone=payload.timezone,
        language=payload.language
    )
    session.add(log)
    session.commit()
    session.refresh(log)
    return log


@app.get("/medications/{medication_id}/logs", response_model=List[MedicationLogRead])
def list_medication_logs(medication_id: int, session: Session = Depends(get_session)):
    """List medication logs with internationalization."""
    m = session.get(Medication, medication_id)
    if not m:
        raise HTTPException(404, "Medication not found")
    rows = session.exec(select(MedicationLog).where(MedicationLog.medication_id == medication_id).order_by(MedicationLog.taken_at.desc(), MedicationLog.id.desc())).all()
    return rows


# ----------------------------------------------------------------------------
# Groups & Posts (with internationalization)
# ----------------------------------------------------------------------------

@app.post("/groups", response_model=GroupRead)
def create_group(
    payload: GroupCreate, 
    session: Session = Depends(get_session),
    accept_language: str = Header(None)
):
    """Create a new group with internationalization."""
    user_locale = get_user_locale_from_request(accept_language)
    
    g = Group(
        name=payload.name, 
        name_localized=payload.name_localized,
        description=payload.description, 
        description_localized=payload.description_localized,
        visibility=payload.visibility,
        is_multilingual=payload.is_multilingual,
        primary_language=payload.primary_language
    )
    session.add(g)
    session.commit()
    session.refresh(g)
    return g


@app.get("/groups", response_model=List[GroupRead])
def list_groups(
    session: Session = Depends(get_session),
    language: LanguageCode = Query(LanguageCode.ENGLISH)
):
    """List groups with internationalization."""
    rows = session.exec(select(Group).where(Group.primary_language == language.value).order_by(Group.id.desc())).all()
    return rows


@app.post("/posts", response_model=PostRead)
def create_post(
    payload: PostCreate, 
    session: Session = Depends(get_session),
    accept_language: str = Header(None)
):
    """Create a new post with internationalization."""
    user_locale = get_user_locale_from_request(accept_language)
    
    g = session.get(Group, payload.group_id)
    if not g:
        raise HTTPException(404, "Group not found")
    
    p = Post(
        group_id=payload.group_id, 
        title=payload.title,
        title_localized=payload.title_localized,
        body=payload.body,
        body_localized=payload.body_localized,
        anon=payload.anon,
        is_multilingual=payload.is_multilingual,
        primary_language=payload.primary_language
    )
    session.add(p)
    session.commit()
    session.refresh(p)
    return p


@app.get("/groups/{group_id}/posts", response_model=List[PostRead])
def list_posts(
    group_id: int, 
    session: Session = Depends(get_session),
    language: LanguageCode = Query(LanguageCode.ENGLISH)
):
    """List posts with internationalization."""
    g = session.get(Group, group_id)
    if not g:
        raise HTTPException(404, "Group not found")
    rows = session.exec(select(Post).where(Post.group_id == group_id).order_by(Post.created_at.desc(), Post.id.desc())).all()
    return rows


# ----------------------------------------------------------------------------
# Reports (with internationalization)
# ----------------------------------------------------------------------------

@app.post("/reports", response_model=ReportRead)
def create_report(
    payload: ReportCreate, 
    session: Session = Depends(get_session),
    accept_language: str = Header(None)
):
    """Create a new report with internationalization."""
    user_locale = get_user_locale_from_request(accept_language)
    
    # Minimal validation for stub: ensure target exists for posts
    if payload.target_type == ReportTargetType.post:
        target = session.get(Post, payload.target_id)
        if not target:
            raise HTTPException(404, "Target post not found")
    
    r = Report(
        target_type=payload.target_type,
        target_id=payload.target_id,
        reason=payload.reason,
        detail=payload.detail,
        language=payload.language
    )
    session.add(r)
    session.commit()
    session.refresh(r)
    return r


@app.get("/reports", response_model=List[ReportRead])
def list_reports(
    session: Session = Depends(get_session),
    status: Optional[str] = None,
    reason: Optional[ReportReason] = None,
    language: LanguageCode = Query(LanguageCode.ENGLISH)
):
    """List reports with internationalization."""
    stmt = select(Report).where(Report.language == language.value).order_by(Report.created_at.desc(), Report.id.desc())
    if status:
        stmt = stmt.where(Report.status == status)
    if reason:
        stmt = stmt.where(Report.reason == reason)
    rows = session.exec(stmt).all()
    return rows


# ----------------------------------------------------------------------------
# Dev utilities (with internationalization)
# ----------------------------------------------------------------------------

@app.post("/dev/seed")
def dev_seed(session: Session = Depends(get_session)):
    """Create sample data for testing with internationalization."""
    # Create sample group
    g = Group(
        name="General", 
        name_localized={"en": "General", "ja": "一般"},
        description="General discussion for the community",
        description_localized={"en": "General discussion for the community", "ja": "コミュニティの一般的な議論"},
        visibility=GroupVisibility.public,
        is_multilingual=True,
        primary_language=LanguageCode.ENGLISH
    )
    session.add(g)
    session.commit()
    session.refresh(g)
    return {"group_id": g.id, "message": "Sample data created with internationalization support"}


# ----------------------------------------------------------------------------
# Health check
# ----------------------------------------------------------------------------

@app.get("/health")
def health():
    """Health check endpoint."""
    return {
        "status": "ok", 
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "features": ["internationalization", "legacy_compatibility", "multi-language"]
    }


# ----------------------------------------------------------------------------
# Root endpoint
# ----------------------------------------------------------------------------

@app.get("/")
def root():
    """Root endpoint with internationalization info."""
    return {
        "message": "Healthcare Community Platform (Unified)",
        "version": "2.0.0",
        "features": [
            "Legacy API compatibility",
            "Internationalization support",
            "Multi-language content",
            "Regional formatting",
            "Timezone handling"
        ],
        "endpoints": {
            "legacy": "/journals, /medications, /groups, /posts, /reports",
            "i18n": "/i18n/languages, /i18n/countries, /i18n/translation",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
