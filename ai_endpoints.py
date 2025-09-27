"""
AI endpoints for the healthcare community platform.
Provides chatbot, translation, symptom analysis, and clinical trial matching APIs.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from fastapi import APIRouter, HTTPException, Depends, Header, Request
from pydantic import BaseModel, Field
from sqlmodel import Session

from ai_service import (
    get_ai_service, get_chatbot_service, get_translation_service,
    ChatMessage, SymptomAnalysis, TrialMatch, AIService, ChatbotService, TranslationService
)
from models_i18n import AppUser, LanguageCode, Observation
from translation_service import TranslationService as I18nTranslationService
from i18n_utils import get_user_locale_from_request

# Create router
router = APIRouter(prefix="/ai", tags=["AI"])


# ----------------------------------------------------------------------------
# Pydantic models for AI endpoints
# ----------------------------------------------------------------------------

class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Chat response model."""
    message: str
    session_id: str
    timestamp: datetime
    language: LanguageCode
    metadata: Optional[Dict[str, Any]] = None


class SymptomAnalysisRequest(BaseModel):
    """Symptom analysis request model."""
    symptoms: List[str] = Field(..., min_items=1, max_items=20)
    additional_context: Optional[Dict[str, Any]] = None


class SymptomAnalysisResponse(BaseModel):
    """Symptom analysis response model."""
    symptoms: List[str]
    severity_score: float = Field(ge=0, le=10)
    urgency_level: str = Field(regex="^(low|medium|high|critical)$")
    recommendations: List[str]
    suggested_actions: List[str]
    confidence: float = Field(ge=0, le=1)


class TranslationRequest(BaseModel):
    """Translation request model."""
    text: str = Field(..., min_length=1, max_length=5000)
    target_language: LanguageCode
    source_language: Optional[LanguageCode] = None


class TranslationResponse(BaseModel):
    """Translation response model."""
    original_text: str
    translated_text: str
    source_language: LanguageCode
    target_language: LanguageCode
    confidence: Optional[float] = None


class ClinicalTrialSearchRequest(BaseModel):
    """Clinical trial search request model."""
    condition: str = Field(..., min_length=1, max_length=200)
    location: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=120)
    gender: Optional[str] = Field(None, regex="^(male|female|other|prefer_not_to_say)$")


class ClinicalTrialSearchResponse(BaseModel):
    """Clinical trial search response model."""
    trials: List[Dict[str, Any]]
    total_count: int
    search_criteria: Dict[str, Any]


class HealthInsightsRequest(BaseModel):
    """Health insights request model."""
    observation_ids: List[int] = Field(..., min_items=1, max_items=100)
    time_range_days: Optional[int] = Field(30, ge=1, le=365)


class HealthInsightsResponse(BaseModel):
    """Health insights response model."""
    insights: Dict[str, Any]
    trends: List[str]
    recommendations: List[str]
    concerns: List[str]
    positive_developments: List[str]
    suggested_actions: List[str]


# ----------------------------------------------------------------------------
# AI Chat endpoints
# ----------------------------------------------------------------------------

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    accept_language: str = Header(None),
    timezone: Optional[str] = Header(None),
    session: Session = Depends(lambda: None)  # Placeholder for session dependency
):
    """
    Chat with AI healthcare assistant.
    
    This endpoint provides a conversational AI assistant that can:
    - Answer health-related questions
    - Provide symptom analysis
    - Give medication information
    - Suggest clinical trials
    - Offer emotional support
    """
    try:
        # Get user locale
        user_locale = get_user_locale_from_request(accept_language, timezone)
        
        # Create mock user for demo
        class MockUser:
            def __init__(self):
                self.id = 1
                self.preferred_language = user_locale.language
                self.country = user_locale.country
        
        user = MockUser()
        
        # Get chatbot service
        chatbot_service = get_chatbot_service()
        
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Process message
        response = await chatbot_service.process_message(
            request.message,
            user,
            session_id,
            request.context
        )
        
        return ChatResponse(
            message=response.content,
            session_id=session_id,
            timestamp=response.timestamp,
            language=response.language,
            metadata=response.metadata
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in chat: {str(e)}")


@router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat conversation history."""
    try:
        chatbot_service = get_chatbot_service()
        history = chatbot_service.get_conversation_history(session_id)
        
        return {
            "session_id": session_id,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "language": msg.language.value,
                    "metadata": msg.metadata
                }
                for msg in history
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting chat history: {str(e)}")


@router.delete("/chat/history/{session_id}")
async def clear_chat_history(session_id: str):
    """Clear chat conversation history."""
    try:
        chatbot_service = get_chatbot_service()
        chatbot_service.clear_conversation(session_id)
        return {"message": "Chat history cleared", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing chat history: {str(e)}")


# ----------------------------------------------------------------------------
# Symptom Analysis endpoints
# ----------------------------------------------------------------------------

@router.post("/symptoms/analyze", response_model=SymptomAnalysisResponse)
async def analyze_symptoms(
    request: SymptomAnalysisRequest,
    accept_language: str = Header(None),
    timezone: Optional[str] = Header(None)
):
    """
    Analyze symptoms and provide recommendations.
    
    This endpoint analyzes reported symptoms and provides:
    - Severity assessment
    - Urgency level
    - Recommendations
    - Suggested actions
    """
    try:
        # Get user locale
        user_locale = get_user_locale_from_request(accept_language, timezone)
        
        # Create mock user for demo
        class MockUser:
            def __init__(self):
                self.id = 1
                self.preferred_language = user_locale.language
                self.country = user_locale.country
        
        user = MockUser()
        
        # Get AI service
        ai_service = get_ai_service()
        
        # Analyze symptoms
        analysis = await ai_service.analyze_symptoms(
            request.symptoms,
            user,
            request.additional_context
        )
        
        return SymptomAnalysisResponse(
            symptoms=analysis.symptoms,
            severity_score=analysis.severity_score,
            urgency_level=analysis.urgency_level,
            recommendations=analysis.recommendations,
            suggested_actions=analysis.suggested_actions,
            confidence=analysis.confidence
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing symptoms: {str(e)}")


# ----------------------------------------------------------------------------
# Translation endpoints
# ----------------------------------------------------------------------------

@router.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """
    Translate text using AI.
    
    This endpoint provides high-quality translation with:
    - Medical terminology awareness
    - Cultural context consideration
    - Language-specific formatting
    """
    try:
        # Get AI service
        ai_service = get_ai_service()
        
        # Translate text
        translated_text = await ai_service.translate_text(
            request.text,
            request.target_language,
            request.source_language
        )
        
        return TranslationResponse(
            original_text=request.text,
            translated_text=translated_text,
            source_language=request.source_language or LanguageCode.ENGLISH,
            target_language=request.target_language,
            confidence=0.9  # AI translation confidence
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error translating text: {str(e)}")


@router.post("/translate/medical")
async def translate_medical_content(
    request: TranslationRequest,
    session: Session = Depends(lambda: None)  # Placeholder for session dependency
):
    """
    Translate medical content with specialized terminology.
    
    This endpoint provides medical-specific translation with:
    - Medical terminology accuracy
    - Clinical context preservation
    - Regulatory compliance
    """
    try:
        # Get translation service
        translation_service = get_translation_service()
        
        # Translate medical content
        translated_text = await translation_service.translate_medical_content(
            request.text,
            request.target_language,
            request.source_language
        )
        
        return {
            "original_text": request.text,
            "translated_text": translated_text,
            "source_language": request.source_language or LanguageCode.ENGLISH,
            "target_language": request.target_language,
            "medical_terminology": True,
            "confidence": 0.95
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error translating medical content: {str(e)}")


@router.post("/translate/symptoms")
async def translate_symptoms(
    symptoms: List[str],
    target_language: LanguageCode,
    session: Session = Depends(lambda: None)  # Placeholder for session dependency
):
    """
    Translate symptom list.
    
    This endpoint translates medical symptoms with:
    - Symptom-specific terminology
    - Cultural context awareness
    - Medical accuracy
    """
    try:
        # Get translation service
        translation_service = get_translation_service()
        
        # Translate symptoms
        translated_symptoms = await translation_service.translate_symptoms(
            symptoms,
            target_language
        )
        
        return {
            "original_symptoms": symptoms,
            "translated_symptoms": translated_symptoms,
            "target_language": target_language,
            "count": len(translated_symptoms)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error translating symptoms: {str(e)}")


# ----------------------------------------------------------------------------
# Clinical Trial endpoints
# ----------------------------------------------------------------------------

@router.post("/trials/search", response_model=ClinicalTrialSearchResponse)
async def search_clinical_trials(
    request: ClinicalTrialSearchRequest,
    accept_language: str = Header(None),
    timezone: Optional[str] = Header(None)
):
    """
    Search for matching clinical trials.
    
    This endpoint finds clinical trials based on:
    - Medical condition
    - Location preferences
    - Age and gender
    - Eligibility criteria
    """
    try:
        # Get user locale
        user_locale = get_user_locale_from_request(accept_language, timezone)
        
        # Create mock user for demo
        class MockUser:
            def __init__(self):
                self.id = 1
                self.preferred_language = user_locale.language
                self.country = user_locale.country
        
        user = MockUser()
        
        # Get AI service
        ai_service = get_ai_service()
        
        # Search for trials
        trials = await ai_service.find_clinical_trials(
            user,
            request.condition,
            request.location,
            request.age,
            request.gender
        )
        
        # Convert to response format
        trial_data = []
        for trial in trials:
            trial_data.append({
                "trial_id": trial.trial_id,
                "title": trial.title,
                "match_score": trial.match_score,
                "reasons": trial.reasons,
                "eligibility_criteria": trial.eligibility_criteria,
                "location": trial.location,
                "contact_info": trial.contact_info
            })
        
        return ClinicalTrialSearchResponse(
            trials=trial_data,
            total_count=len(trial_data),
            search_criteria={
                "condition": request.condition,
                "location": request.location,
                "age": request.age,
                "gender": request.gender
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching clinical trials: {str(e)}")


# ----------------------------------------------------------------------------
# Health Insights endpoints
# ----------------------------------------------------------------------------

@router.post("/insights/health", response_model=HealthInsightsResponse)
async def generate_health_insights(
    request: HealthInsightsRequest,
    accept_language: str = Header(None),
    timezone: Optional[str] = Header(None),
    session: Session = Depends(lambda: None)  # Placeholder for session dependency
):
    """
    Generate health insights from observations.
    
    This endpoint analyzes health data and provides:
    - Trend analysis
    - Health recommendations
    - Areas of concern
    - Positive developments
    - Suggested actions
    """
    try:
        # Get user locale
        user_locale = get_user_locale_from_request(accept_language, timezone)
        
        # Create mock user for demo
        class MockUser:
            def __init__(self):
                self.id = 1
                self.preferred_language = user_locale.language
                self.country = user_locale.country
        
        user = MockUser()
        
        # Get AI service
        ai_service = get_ai_service()
        
        # Create mock observations for demo
        observations = []
        for i in range(min(10, len(request.observation_ids))):
            obs = Observation(
                id=request.observation_ids[i],
                type="blood_pressure",
                value_json={"systolic": 120, "diastolic": 80},
                observed_at=datetime.utcnow(),
                timezone=user_locale.timezone,
                language=user_locale.language
            )
            observations.append(obs)
        
        # Generate insights
        insights = await ai_service.generate_health_insights(observations, user)
        
        return HealthInsightsResponse(
            insights=insights,
            trends=insights.get("trends", []),
            recommendations=insights.get("recommendations", []),
            concerns=insights.get("concerns", []),
            positive_developments=insights.get("positive", []),
            suggested_actions=insights.get("actions", [])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating health insights: {str(e)}")


# ----------------------------------------------------------------------------
# AI Status endpoints
# ----------------------------------------------------------------------------

@router.get("/status")
async def get_ai_status():
    """Get AI service status."""
    try:
        ai_service = get_ai_service()
        
        return {
            "status": "operational" if ai_service.client else "limited",
            "provider": ai_service.provider.value,
            "features": {
                "chat": ai_service.client is not None,
                "translation": ai_service.client is not None,
                "symptom_analysis": ai_service.client is not None,
                "clinical_trials": ai_service.client is not None,
                "health_insights": ai_service.client is not None
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/capabilities")
async def get_ai_capabilities():
    """Get AI service capabilities."""
    return {
        "languages": [lang.value for lang in LanguageCode],
        "features": [
            "Chat with healthcare assistant",
            "Symptom analysis and recommendations",
            "Medical content translation",
            "Clinical trial matching",
            "Health insights generation",
            "Multi-language support",
            "Cultural context awareness"
        ],
        "limitations": [
            "Not a substitute for medical advice",
            "Requires healthcare professional consultation",
            "AI responses may not be 100% accurate",
            "Emergency situations require immediate medical attention"
        ]
    }
