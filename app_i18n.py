"""
Internationalized FastAPI application for the healthcare community platform.
Supports multiple languages, timezones, and regional settings.
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
from models_i18n import (
    AppUser, AppUserCreate, AppUserRead, Observation, ObservationCreate, ObservationRead,
    MedicationPlan, MedicationPlanCreate, MedicationPlanRead, Post, PostCreate, PostRead,
    TranslationRequest, TranslationResponse
)
from translation_service import TranslationService, LocalizationService, ContentTranslationService
from i18n_utils import (
    I18nUtils, LocalizationUtils, ContentUtils, ValidationUtils,
    get_user_locale_from_request, format_content_for_user, format_datetime_for_user,
    format_currency_for_user, validate_translation_quality
)

# Set ORIGINS
ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "http://127.0.0.1:3000,http://localhost:3000").split(",")

# ----------------------------------------------------------------------------
# Database setup
# ----------------------------------------------------------------------------
DATABASE_URL = "sqlite:///./app_i18n.db"

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})


def get_session():
    with Session(engine) as session:
        yield session


# ----------------------------------------------------------------------------
# FastAPI app with internationalization
# ----------------------------------------------------------------------------
app = FastAPI(
    title="Healthcare Community Platform (Internationalized)",
    description="Multi-language healthcare community platform with internationalization support",
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


@app.post("/i18n/translation", response_model=TranslationResponse)
def create_translation(
    request: TranslationRequest,
    value: str,
    is_approved: bool = False,
    session: Session = Depends(get_session)
):
    """Create a new translation."""
    translation_service = TranslationService(session)
    translation = translation_service.create_translation(
        request.namespace,
        request.key,
        request.language,
        value,
        request.context,
        is_approved
    )
    return TranslationResponse(
        namespace=request.namespace,
        key=request.key,
        language=request.language,
        value=value,
        context=request.context,
        is_approved=is_approved,
        created_at=translation.created_at,
        updated_at=translation.updated_at
    )


@app.get("/i18n/translation/stats/{language}")
def get_translation_stats(
    language: LanguageCode,
    session: Session = Depends(get_session)
):
    """Get translation statistics for a language."""
    translation_service = TranslationService(session)
    return translation_service.get_translation_stats(language)


@app.get("/i18n/translation/missing/{language}")
def get_missing_translations(
    language: LanguageCode,
    namespace: Optional[TranslationNamespace] = None,
    session: Session = Depends(get_session)
):
    """Get missing translations for a language."""
    translation_service = TranslationService(session)
    return translation_service.get_missing_translations(language, namespace)


# ----------------------------------------------------------------------------
# Health endpoints (Internationalized)
# ----------------------------------------------------------------------------

@app.post("/health/observations", response_model=ObservationRead)
def create_observation(
    payload: ObservationCreate,
    accept_language: str = Header(None),
    timezone: Optional[str] = Header(None),
    session: Session = Depends(get_session)
):
    """Create a new observation with internationalization."""
    # Get user locale from headers
    user_locale = get_user_locale_from_request(accept_language, timezone)
    
    # Create observation
    observation = Observation(
        account_id=1,  # Default account for demo
        user_id=1,     # Default user for demo
        type=payload.type,
        value_json=payload.value_json,
        observed_at=payload.observed_at or datetime.utcnow(),
        timezone=payload.timezone,
        language=payload.language
    )
    
    session.add(observation)
    session.commit()
    session.refresh(observation)
    
    return ObservationRead(
        id=observation.id,
        type=observation.type,
        value_json=observation.value_json,
        observed_at=observation.observed_at,
        timezone=observation.timezone,
        language=observation.language,
        created_at=observation.created_at
    )


@app.get("/health/observations", response_model=List[ObservationRead])
def list_observations(
    user_id: int = Query(1),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    session: Session = Depends(get_session)
):
    """List observations with internationalization."""
    stmt = select(Observation).where(Observation.user_id == user_id).order_by(Observation.observed_at.desc())
    
    if date_from:
        stmt = stmt.where(Observation.observed_at >= date_from)
    if date_to:
        stmt = stmt.where(Observation.observed_at <= date_to)
    
    stmt = stmt.offset(offset).limit(limit)
    observations = session.exec(stmt).all()
    
    return [
        ObservationRead(
            id=obs.id,
            type=obs.type,
            value_json=obs.value_json,
            observed_at=obs.observed_at,
            timezone=obs.timezone,
            language=obs.language,
            created_at=obs.created_at
        )
        for obs in observations
    ]


@app.post("/health/medications", response_model=MedicationPlanRead)
def create_medication_plan(
    payload: MedicationPlanCreate,
    accept_language: str = Header(None),
    timezone: Optional[str] = Header(None),
    session: Session = Depends(get_session)
):
    """Create a new medication plan with internationalization."""
    # Get user locale from headers
    user_locale = get_user_locale_from_request(accept_language, timezone)
    
    # Create medication plan
    plan = MedicationPlan(
        account_id=1,  # Default account for demo
        user_id=1,     # Default user for demo
        drug_code=payload.drug_code,
        drug_name=payload.drug_name,
        drug_name_localized=payload.drug_name_localized,
        dose=payload.dose,
        schedule_json=payload.schedule_json,
        start_date=payload.start_date,
        end_date=payload.end_date,
        notes=payload.notes,
        language=payload.language
    )
    
    session.add(plan)
    session.commit()
    session.refresh(plan)
    
    return MedicationPlanRead(
        id=plan.id,
        drug_code=plan.drug_code,
        drug_name=plan.drug_name,
        drug_name_localized=plan.drug_name_localized,
        dose=plan.dose,
        schedule_json=plan.schedule_json,
        start_date=plan.start_date,
        end_date=plan.end_date,
        notes=plan.notes,
        language=plan.language,
        created_at=plan.created_at
    )


@app.get("/health/medications", response_model=List[MedicationPlanRead])
def list_medication_plans(
    user_id: int = Query(1),
    session: Session = Depends(get_session)
):
    """List medication plans with internationalization."""
    stmt = select(MedicationPlan).where(MedicationPlan.user_id == user_id).order_by(MedicationPlan.created_at.desc())
    plans = session.exec(stmt).all()
    
    return [
        MedicationPlanRead(
            id=plan.id,
            drug_code=plan.drug_code,
            drug_name=plan.drug_name,
            drug_name_localized=plan.drug_name_localized,
            dose=plan.dose,
            schedule_json=plan.schedule_json,
            start_date=plan.start_date,
            end_date=plan.end_date,
            notes=plan.notes,
            language=plan.language,
            created_at=plan.created_at
        )
        for plan in plans
    ]


# ----------------------------------------------------------------------------
# Community endpoints (Internationalized)
# ----------------------------------------------------------------------------

@app.post("/community/posts", response_model=PostRead)
def create_post(
    payload: PostCreate,
    accept_language: str = Header(None),
    timezone: Optional[str] = Header(None),
    session: Session = Depends(get_session)
):
    """Create a new post with internationalization."""
    # Get user locale from headers
    user_locale = get_user_locale_from_request(accept_language, timezone)
    
    # Create post
    post = Post(
        room_id=payload.room_id,
        user_id=1,  # Default user for demo
        is_multilingual=payload.is_multilingual,
        primary_language=payload.primary_language,
        tags=payload.tags
    )
    
    session.add(post)
    session.commit()
    session.refresh(post)
    
    # Create post content
    for language, content in payload.content.items():
        post_content = PostContent(
            post_id=post.id,
            language=language.value,
            title=content.get("title"),
            body_md=content.get("body_md", ""),
            is_primary=(language == payload.primary_language)
        )
        session.add(post_content)
    
    session.commit()
    
    return PostRead(
        id=post.id,
        room_id=post.room_id,
        user_id=post.user_id,
        is_multilingual=post.is_multilingual,
        primary_language=post.primary_language,
        tags=post.tags,
        content=payload.content,
        created_at=post.created_at,
        updated_at=post.updated_at
    )


@app.get("/community/posts", response_model=List[PostRead])
def list_posts(
    room_id: int = Query(1),
    language: LanguageCode = Query(LanguageCode.ENGLISH),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: Session = Depends(get_session)
):
    """List posts with internationalization."""
    stmt = select(Post).where(Post.room_id == room_id).order_by(Post.created_at.desc())
    stmt = stmt.offset(offset).limit(limit)
    posts = session.exec(stmt).all()
    
    result = []
    for post in posts:
        # Get post content for requested language
        content_stmt = select(PostContent).where(
            PostContent.post_id == post.id,
            PostContent.language == language.value
        )
        content = session.exec(content_stmt).first()
        
        if content:
            post_content = {language: {"title": content.title, "body_md": content.body_md}}
        else:
            # Fallback to primary language
            primary_stmt = select(PostContent).where(
                PostContent.post_id == post.id,
                PostContent.is_primary == True
            )
            primary_content = session.exec(primary_stmt).first()
            if primary_content:
                post_content = {LanguageCode(primary_content.language): {"title": primary_content.title, "body_md": primary_content.body_md}}
            else:
                post_content = {}
        
        result.append(PostRead(
            id=post.id,
            room_id=post.room_id,
            user_id=post.user_id,
            is_multilingual=post.is_multilingual,
            primary_language=post.primary_language,
            tags=post.tags,
            content=post_content,
            created_at=post.created_at,
            updated_at=post.updated_at
        ))
    
    return result


# ----------------------------------------------------------------------------
# Utility endpoints
# ----------------------------------------------------------------------------

@app.get("/utils/format/datetime")
def format_datetime_util(
    dt: datetime,
    language: LanguageCode = LanguageCode.ENGLISH,
    country: CountryCode = CountryCode.UNITED_STATES,
    timezone: TimezoneCode = TimezoneCode.UTC,
    date_format: DateFormat = DateFormat.ISO,
    time_format: TimeFormat = TimeFormat.HOUR_24
):
    """Format datetime according to locale preferences."""
    # Create mock user for formatting
    class MockUser:
        def __init__(self):
            self.preferred_language = language
            self.country = country
            self.timezone = timezone
            self.date_format = date_format
            self.time_format = time_format
            self.currency = CurrencyCode.USD
            self.measurement_unit = MeasurementUnit.METRIC
    
    user = MockUser()
    formatted = LocalizationUtils.format_datetime_for_user(dt, user)
    
    return {
        "original": dt.isoformat(),
        "formatted": formatted,
        "language": language.value,
        "country": country.value,
        "timezone": timezone.value,
        "date_format": date_format.value,
        "time_format": time_format.value
    }


@app.get("/utils/format/currency")
def format_currency_util(
    amount: float,
    currency: CurrencyCode = CurrencyCode.USD,
    language: LanguageCode = LanguageCode.ENGLISH,
    country: CountryCode = CountryCode.UNITED_STATES
):
    """Format currency according to locale preferences."""
    # Create mock user for formatting
    class MockUser:
        def __init__(self):
            self.preferred_language = language
            self.country = country
            self.timezone = TimezoneCode.UTC
            self.date_format = DateFormat.ISO
            self.time_format = TimeFormat.HOUR_24
            self.currency = currency
            self.measurement_unit = MeasurementUnit.METRIC
    
    user = MockUser()
    formatted = LocalizationUtils.format_currency_for_user(amount, user)
    
    return {
        "amount": amount,
        "formatted": formatted,
        "currency": currency.value,
        "language": language.value,
        "country": country.value
    }


@app.post("/utils/validate/translation")
def validate_translation_util(
    original: str,
    translation: str,
    target_language: LanguageCode
):
    """Validate translation quality."""
    result = validate_translation_quality(original, translation, target_language)
    return result


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
        "features": ["internationalization", "multi-language", "regional-formatting"]
    }


# ----------------------------------------------------------------------------
# Root endpoint
# ----------------------------------------------------------------------------

@app.get("/")
def root():
    """Root endpoint with internationalization info."""
    return {
        "message": "Healthcare Community Platform (Internationalized)",
        "version": "2.0.0",
        "features": [
            "Multi-language support",
            "Regional formatting",
            "Timezone handling",
            "Currency formatting",
            "Measurement units",
            "Translation management"
        ],
        "supported_languages": len(I18nUtils.get_supported_languages()),
        "supported_countries": len(I18nUtils.get_supported_countries()),
        "docs_url": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
