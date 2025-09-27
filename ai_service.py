"""
AI service for the healthcare community platform.
Provides chatbot, translation, symptom analysis, and clinical trial matching.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import asyncio
import aiohttp
from dataclasses import dataclass
from enum import Enum

# AI/ML libraries
try:
    import openai
    from openai import AsyncOpenAI
except ImportError:
    openai = None
    AsyncOpenAI = None

try:
    from langchain.llms import OpenAI
    from langchain.chat_models import ChatOpenAI
    from langchain.schema import HumanMessage, SystemMessage
    from langchain.embeddings import OpenAIEmbeddings
    from langchain.vectorstores import FAISS
    from langchain.text_splitter import RecursiveCharacterTextSplitter
except ImportError:
    OpenAI = None
    ChatOpenAI = None
    HumanMessage = None
    SystemMessage = None
    OpenAIEmbeddings = None
    FAISS = None
    RecursiveCharacterTextSplitter = None

from models_i18n import LanguageCode, AppUser, Observation, Trial
from i18n_config import get_user_locale_from_headers

logger = logging.getLogger(__name__)


class AIProvider(str, Enum):
    """AI service providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    LOCAL = "local"


@dataclass
class ChatMessage:
    """Chat message model."""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime
    language: LanguageCode
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class SymptomAnalysis:
    """Symptom analysis result."""
    symptoms: List[str]
    severity_score: float  # 0-10
    urgency_level: str  # 'low', 'medium', 'high', 'critical'
    recommendations: List[str]
    suggested_actions: List[str]
    confidence: float  # 0-1


@dataclass
class TrialMatch:
    """Clinical trial match result."""
    trial_id: str
    title: str
    match_score: float  # 0-1
    reasons: List[str]
    eligibility_criteria: List[str]
    location: str
    contact_info: str


class AIService:
    """AI service for healthcare platform."""
    
    def __init__(self, api_key: str = None, provider: AIProvider = AIProvider.OPENAI):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.provider = provider
        self.client = None
        self.embeddings = None
        self.vector_store = None
        
        if self.api_key:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize AI client."""
        try:
            if self.provider == AIProvider.OPENAI and openai:
                self.client = AsyncOpenAI(api_key=self.api_key)
                if OpenAIEmbeddings:
                    self.embeddings = OpenAIEmbeddings(openai_api_key=self.api_key)
            else:
                logger.warning(f"AI provider {self.provider} not available")
        except Exception as e:
            logger.error(f"Error initializing AI client: {e}")
    
    async def chat_completion(
        self, 
        messages: List[ChatMessage], 
        user: AppUser,
        context: Optional[Dict[str, Any]] = None
    ) -> ChatMessage:
        """
        Generate chat completion.
        
        Args:
            messages: List of chat messages
            user: User making the request
            context: Additional context
            
        Returns:
            AI response message
        """
        try:
            if not self.client:
                return self._fallback_response(messages[-1], user)
            
            # Prepare messages for API
            api_messages = []
            for msg in messages:
                api_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            # Add system context
            system_prompt = self._get_system_prompt(user, context)
            api_messages.insert(0, {
                "role": "system",
                "content": system_prompt
            })
            
            # Call AI API
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=api_messages,
                temperature=0.7,
                max_tokens=1000,
                user=str(user.id)
            )
            
            # Create response message
            response_content = response.choices[0].message.content
            return ChatMessage(
                role="assistant",
                content=response_content,
                timestamp=datetime.utcnow(),
                language=user.preferred_language,
                metadata={
                    "model": "gpt-4",
                    "tokens_used": response.usage.total_tokens,
                    "context": context
                }
            )
            
        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            return self._fallback_response(messages[-1], user)
    
    def _get_system_prompt(self, user: AppUser, context: Optional[Dict[str, Any]]) -> str:
        """Get system prompt for AI."""
        base_prompt = """You are a helpful healthcare assistant. You provide:
1. General health information and guidance
2. Symptom analysis and recommendations
3. Medication information
4. Clinical trial information
5. Community support

Important guidelines:
- Always recommend consulting healthcare professionals for medical advice
- Be empathetic and supportive
- Provide accurate, evidence-based information
- Respect user privacy and confidentiality
- Use appropriate medical terminology
- Consider cultural and linguistic context
"""
        
        # Add user-specific context
        if user:
            base_prompt += f"\nUser context:\n- Language: {user.preferred_language}\n- Country: {user.country}\n"
        
        # Add additional context
        if context:
            base_prompt += f"\nAdditional context: {json.dumps(context)}\n"
        
        return base_prompt
    
    def _fallback_response(self, last_message: ChatMessage, user: AppUser) -> ChatMessage:
        """Fallback response when AI is not available."""
        fallback_responses = {
            LanguageCode.ENGLISH: "I'm sorry, I'm currently unable to process your request. Please try again later or contact a healthcare professional.",
            LanguageCode.JAPANESE: "申し訳ございませんが、現在リクエストを処理できません。後でもう一度お試しいただくか、医療専門家にご相談ください。",
            LanguageCode.CHINESE_SIMPLIFIED: "抱歉，我目前无法处理您的请求。请稍后再试或联系医疗专业人士。",
            LanguageCode.KOREAN: "죄송합니다. 현재 요청을 처리할 수 없습니다. 나중에 다시 시도하거나 의료 전문가에게 문의하세요.",
        }
        
        response_text = fallback_responses.get(
            user.preferred_language, 
            fallback_responses[LanguageCode.ENGLISH]
        )
        
        return ChatMessage(
            role="assistant",
            content=response_text,
            timestamp=datetime.utcnow(),
            language=user.preferred_language,
            metadata={"fallback": True}
        )
    
    async def analyze_symptoms(
        self, 
        symptoms: List[str], 
        user: AppUser,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> SymptomAnalysis:
        """
        Analyze symptoms and provide recommendations.
        
        Args:
            symptoms: List of symptoms
            user: User reporting symptoms
            additional_context: Additional context (vitals, medications, etc.)
            
        Returns:
            Symptom analysis result
        """
        try:
            if not self.client:
                return self._fallback_symptom_analysis(symptoms, user)
            
            # Prepare symptom analysis prompt
            prompt = f"""
            Analyze the following symptoms and provide a medical assessment:
            
            Symptoms: {', '.join(symptoms)}
            User: {user.preferred_language} speaker from {user.country}
            
            Additional context: {json.dumps(additional_context or {})}
            
            Please provide:
            1. Severity score (0-10)
            2. Urgency level (low/medium/high/critical)
            3. Recommendations
            4. Suggested actions
            5. Confidence level (0-1)
            
            Format as JSON.
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            # Parse response
            result = json.loads(response.choices[0].message.content)
            
            return SymptomAnalysis(
                symptoms=symptoms,
                severity_score=result.get("severity_score", 5.0),
                urgency_level=result.get("urgency_level", "medium"),
                recommendations=result.get("recommendations", []),
                suggested_actions=result.get("suggested_actions", []),
                confidence=result.get("confidence", 0.8)
            )
            
        except Exception as e:
            logger.error(f"Error in symptom analysis: {e}")
            return self._fallback_symptom_analysis(symptoms, user)
    
    def _fallback_symptom_analysis(self, symptoms: List[str], user: AppUser) -> SymptomAnalysis:
        """Fallback symptom analysis."""
        return SymptomAnalysis(
            symptoms=symptoms,
            severity_score=5.0,
            urgency_level="medium",
            recommendations=[
                "Consult with a healthcare professional",
                "Monitor symptoms closely",
                "Keep a symptom diary"
            ],
            suggested_actions=[
                "Schedule an appointment with your doctor",
                "Contact emergency services if symptoms worsen"
            ],
            confidence=0.5
        )
    
    async def translate_text(
        self, 
        text: str, 
        target_language: LanguageCode,
        source_language: Optional[LanguageCode] = None
    ) -> str:
        """
        Translate text to target language.
        
        Args:
            text: Text to translate
            target_language: Target language
            source_language: Source language (auto-detect if None)
            
        Returns:
            Translated text
        """
        try:
            if not self.client:
                return text  # Return original text if translation not available
            
            prompt = f"""
            Translate the following text to {target_language.value}:
            
            Text: {text}
            
            Please provide only the translation, no additional text.
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error in translation: {e}")
            return text  # Return original text on error
    
    async def find_clinical_trials(
        self, 
        user: AppUser,
        condition: str,
        location: Optional[str] = None,
        age: Optional[int] = None,
        gender: Optional[str] = None
    ) -> List[TrialMatch]:
        """
        Find matching clinical trials.
        
        Args:
            user: User searching for trials
            condition: Medical condition
            location: User location
            age: User age
            gender: User gender
            
        Returns:
            List of matching trials
        """
        try:
            if not self.client:
                return self._fallback_trial_matches(condition, user)
            
            prompt = f"""
            Find clinical trials for the following criteria:
            
            Condition: {condition}
            Location: {location or 'Any'}
            Age: {age or 'Any'}
            Gender: {gender or 'Any'}
            Language: {user.preferred_language}
            Country: {user.country}
            
            Please provide:
            1. Trial title
            2. Match score (0-1)
            3. Reasons for match
            4. Eligibility criteria
            5. Location
            6. Contact information
            
            Format as JSON array.
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            
            # Parse response
            results = json.loads(response.choices[0].message.content)
            
            return [
                TrialMatch(
                    trial_id=f"trial_{i}",
                    title=result.get("title", ""),
                    match_score=result.get("match_score", 0.5),
                    reasons=result.get("reasons", []),
                    eligibility_criteria=result.get("eligibility_criteria", []),
                    location=result.get("location", ""),
                    contact_info=result.get("contact_info", "")
                )
                for i, result in enumerate(results)
            ]
            
        except Exception as e:
            logger.error(f"Error in clinical trial search: {e}")
            return self._fallback_trial_matches(condition, user)
    
    def _fallback_trial_matches(self, condition: str, user: AppUser) -> List[TrialMatch]:
        """Fallback trial matches."""
        return [
            TrialMatch(
                trial_id="fallback_1",
                title=f"Research study for {condition}",
                match_score=0.6,
                reasons=["General eligibility", "Condition match"],
                eligibility_criteria=["Age 18+", "Diagnosed condition"],
                location="Multiple locations",
                contact_info="Contact your healthcare provider"
            )
        ]
    
    async def generate_health_insights(
        self, 
        observations: List[Observation], 
        user: AppUser
    ) -> Dict[str, Any]:
        """
        Generate health insights from observations.
        
        Args:
            observations: List of health observations
            user: User for insights
            
        Returns:
            Health insights
        """
        try:
            if not self.client:
                return self._fallback_health_insights(observations, user)
            
            # Prepare observation data
            obs_data = []
            for obs in observations:
                obs_data.append({
                    "type": obs.type,
                    "value": obs.value_json,
                    "date": obs.observed_at.isoformat()
                })
            
            prompt = f"""
            Analyze the following health observations and provide insights:
            
            Observations: {json.dumps(obs_data)}
            User: {user.preferred_language} speaker from {user.country}
            
            Please provide:
            1. Key trends and patterns
            2. Health recommendations
            3. Areas of concern
            4. Positive developments
            5. Suggested actions
            
            Format as JSON.
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=800
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error in health insights generation: {e}")
            return self._fallback_health_insights(observations, user)
    
    def _fallback_health_insights(self, observations: List[Observation], user: AppUser) -> Dict[str, Any]:
        """Fallback health insights."""
        return {
            "trends": ["Continue monitoring your health"],
            "recommendations": ["Maintain regular check-ups"],
            "concerns": [],
            "positive": ["Consistent health tracking"],
            "actions": ["Keep recording your observations"]
        }


class ChatbotService:
    """Healthcare chatbot service."""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        self.conversation_history: Dict[str, List[ChatMessage]] = {}
    
    async def process_message(
        self, 
        message: str, 
        user: AppUser,
        session_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ChatMessage:
        """
        Process user message and generate response.
        
        Args:
            message: User message
            user: User sending message
            session_id: Conversation session ID
            context: Additional context
            
        Returns:
            Bot response
        """
        # Add user message to history
        user_message = ChatMessage(
            role="user",
            content=message,
            timestamp=datetime.utcnow(),
            language=user.preferred_language
        )
        
        # Get conversation history
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        
        self.conversation_history[session_id].append(user_message)
        
        # Generate response
        response = await self.ai_service.chat_completion(
            self.conversation_history[session_id],
            user,
            context
        )
        
        # Add response to history
        self.conversation_history[session_id].append(response)
        
        # Limit conversation history
        if len(self.conversation_history[session_id]) > 20:
            self.conversation_history[session_id] = self.conversation_history[session_id][-20:]
        
        return response
    
    def get_conversation_history(self, session_id: str) -> List[ChatMessage]:
        """Get conversation history for session."""
        return self.conversation_history.get(session_id, [])
    
    def clear_conversation(self, session_id: str):
        """Clear conversation history for session."""
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]


class TranslationService:
    """AI-powered translation service."""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
    
    async def translate_medical_content(
        self, 
        content: str, 
        target_language: LanguageCode,
        source_language: Optional[LanguageCode] = None
    ) -> str:
        """
        Translate medical content with context awareness.
        
        Args:
            content: Medical content to translate
            target_language: Target language
            source_language: Source language
            
        Returns:
            Translated content
        """
        try:
            if not self.ai_service.client:
                return content
            
            prompt = f"""
            Translate the following medical content to {target_language.value}:
            
            Content: {content}
            
            Important:
            - Maintain medical accuracy
            - Use appropriate medical terminology
            - Consider cultural context
            - Preserve technical terms when necessary
            
            Provide only the translation.
            """
            
            response = await self.ai_service.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=1000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error in medical translation: {e}")
            return content
    
    async def translate_symptoms(
        self, 
        symptoms: List[str], 
        target_language: LanguageCode
    ) -> List[str]:
        """
        Translate symptom list.
        
        Args:
            symptoms: List of symptoms
            target_language: Target language
            
        Returns:
            Translated symptoms
        """
        try:
            translated_symptoms = []
            for symptom in symptoms:
                translated = await self.ai_service.translate_text(
                    symptom, 
                    target_language
                )
                translated_symptoms.append(translated)
            return translated_symptoms
        except Exception as e:
            logger.error(f"Error translating symptoms: {e}")
            return symptoms


# Global AI service instance
ai_service = None
chatbot_service = None
translation_service = None

def get_ai_service() -> AIService:
    """Get global AI service instance."""
    global ai_service
    if ai_service is None:
        ai_service = AIService()
    return ai_service

def get_chatbot_service() -> ChatbotService:
    """Get global chatbot service instance."""
    global chatbot_service
    if chatbot_service is None:
        chatbot_service = ChatbotService(get_ai_service())
    return chatbot_service

def get_translation_service() -> TranslationService:
    """Get global translation service instance."""
    global translation_service
    if translation_service is None:
        translation_service = TranslationService(get_ai_service())
    return translation_service
