"""
Translation service for the healthcare community platform.
Handles multi-language content management and translation retrieval.
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
import logging
from sqlmodel import Session, select, and_
from models_i18n import (
    LanguageCode, TranslationNamespace, TranslationRequest, TranslationResponse,
    AppUser, UserLocaleRead
)
from i18n_config import get_user_locale_from_headers, format_datetime, format_number, format_currency

logger = logging.getLogger(__name__)


class TranslationService:
    """Service for managing translations and internationalization."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_translation(
        self, 
        namespace: TranslationNamespace, 
        key: str, 
        language: LanguageCode,
        context: Optional[str] = None,
        fallback_to_english: bool = True
    ) -> str:
        """
        Get translation for a given namespace, key, and language.
        
        Args:
            namespace: Translation namespace (ui, medical, community, etc.)
            key: Translation key
            language: Target language
            context: Optional context for the translation
            fallback_to_english: Whether to fallback to English if translation not found
            
        Returns:
            Translated text or the key if translation not found
        """
        try:
            # First, try to get the translation key
            key_stmt = select(TranslationKey).where(
                and_(
                    TranslationKey.namespace == namespace.value,
                    TranslationKey.key == key
                )
            )
            translation_key = self.session.exec(key_stmt).first()
            
            if not translation_key:
                logger.warning(f"Translation key not found: {namespace.value}.{key}")
                return key
            
            # Get the translation
            translation_stmt = select(Translation).where(
                and_(
                    Translation.key_id == translation_key.id,
                    Translation.language == language.value,
                    Translation.is_approved == True
                )
            )
            
            if context:
                translation_stmt = translation_stmt.where(Translation.context == context)
            
            translation = self.session.exec(translation_stmt).first()
            
            if translation:
                return translation.value
            
            # Fallback to English if requested and not already English
            if fallback_to_english and language != LanguageCode.ENGLISH:
                english_stmt = select(Translation).where(
                    and_(
                        Translation.key_id == translation_key.id,
                        Translation.language == LanguageCode.ENGLISH.value,
                        Translation.is_approved == True
                    )
                )
                
                if context:
                    english_stmt = english_stmt.where(Translation.context == context)
                
                english_translation = self.session.exec(english_stmt).first()
                if english_translation:
                    return english_translation.value
            
            # Return the key if no translation found
            logger.warning(f"Translation not found for {namespace.value}.{key} in {language.value}")
            return key
            
        except Exception as e:
            logger.error(f"Error getting translation: {e}")
            return key
    
    def get_translations_batch(
        self, 
        requests: List[TranslationRequest],
        fallback_to_english: bool = True
    ) -> Dict[str, str]:
        """
        Get multiple translations in batch.
        
        Args:
            requests: List of translation requests
            fallback_to_english: Whether to fallback to English if translation not found
            
        Returns:
            Dictionary mapping "namespace.key" to translated text
        """
        results = {}
        
        for request in requests:
            key = f"{request.namespace.value}.{request.key}"
            translation = self.get_translation(
                request.namespace,
                request.key,
                request.language,
                request.context,
                fallback_to_english
            )
            results[key] = translation
        
        return results
    
    def get_user_translations(
        self, 
        user: AppUser, 
        namespace: TranslationNamespace,
        keys: List[str],
        context: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Get translations for a specific user's language preferences.
        
        Args:
            user: User object with language preferences
            namespace: Translation namespace
            keys: List of translation keys
            context: Optional context for translations
            
        Returns:
            Dictionary mapping keys to translated text
        """
        requests = [
            TranslationRequest(
                namespace=namespace,
                key=key,
                language=user.preferred_language,
                context=context
            )
            for key in keys
        ]
        
        return self.get_translations_batch(requests)
    
    def create_translation(
        self,
        namespace: TranslationNamespace,
        key: str,
        language: LanguageCode,
        value: str,
        context: Optional[str] = None,
        is_approved: bool = False
    ) -> Translation:
        """
        Create a new translation.
        
        Args:
            namespace: Translation namespace
            key: Translation key
            language: Target language
            value: Translated text
            context: Optional context
            is_approved: Whether the translation is approved
            
        Returns:
            Created translation object
        """
        # Get or create translation key
        key_stmt = select(TranslationKey).where(
            and_(
                TranslationKey.namespace == namespace.value,
                TranslationKey.key == key
            )
        )
        translation_key = self.session.exec(key_stmt).first()
        
        if not translation_key:
            translation_key = TranslationKey(
                namespace=namespace.value,
                key=key,
                context=context
            )
            self.session.add(translation_key)
            self.session.commit()
            self.session.refresh(translation_key)
        
        # Create or update translation
        translation_stmt = select(Translation).where(
            and_(
                Translation.key_id == translation_key.id,
                Translation.language == language.value
            )
        )
        
        if context:
            translation_stmt = translation_stmt.where(Translation.context == context)
        
        existing_translation = self.session.exec(translation_stmt).first()
        
        if existing_translation:
            existing_translation.value = value
            existing_translation.is_approved = is_approved
            existing_translation.updated_at = datetime.utcnow()
            self.session.add(existing_translation)
            self.session.commit()
            return existing_translation
        else:
            new_translation = Translation(
                key_id=translation_key.id,
                language=language.value,
                value=value,
                context=context,
                is_approved=is_approved
            )
            self.session.add(new_translation)
            self.session.commit()
            self.session.refresh(new_translation)
            return new_translation
    
    def approve_translation(self, translation_id: int) -> bool:
        """
        Approve a translation.
        
        Args:
            translation_id: ID of the translation to approve
            
        Returns:
            True if successful, False otherwise
        """
        try:
            translation = self.session.get(Translation, translation_id)
            if translation:
                translation.is_approved = True
                translation.updated_at = datetime.utcnow()
                self.session.add(translation)
                self.session.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error approving translation: {e}")
            return False
    
    def get_translation_stats(self, language: LanguageCode) -> Dict[str, Any]:
        """
        Get translation statistics for a language.
        
        Args:
            language: Target language
            
        Returns:
            Dictionary with translation statistics
        """
        try:
            # Total translations
            total_stmt = select(Translation).where(Translation.language == language.value)
            total_translations = len(self.session.exec(total_stmt).all())
            
            # Approved translations
            approved_stmt = select(Translation).where(
                and_(
                    Translation.language == language.value,
                    Translation.is_approved == True
                )
            )
            approved_translations = len(self.session.exec(approved_stmt).all())
            
            # Pending translations
            pending_translations = total_translations - approved_translations
            
            # Coverage by namespace
            namespace_stats = {}
            for namespace in TranslationNamespace:
                namespace_stmt = select(Translation).where(
                    and_(
                        Translation.language == language.value,
                        Translation.key_id.in_(
                            select(TranslationKey.id).where(
                                TranslationKey.namespace == namespace.value
                            )
                        )
                    )
                )
                namespace_translations = len(self.session.exec(namespace_stmt).all())
                namespace_stats[namespace.value] = namespace_translations
            
            return {
                "language": language.value,
                "total_translations": total_translations,
                "approved_translations": approved_translations,
                "pending_translations": pending_translations,
                "approval_rate": approved_translations / total_translations if total_translations > 0 else 0,
                "namespace_stats": namespace_stats
            }
        except Exception as e:
            logger.error(f"Error getting translation stats: {e}")
            return {}
    
    def get_missing_translations(
        self, 
        language: LanguageCode,
        namespace: Optional[TranslationNamespace] = None
    ) -> List[Dict[str, str]]:
        """
        Get missing translations for a language.
        
        Args:
            language: Target language
            namespace: Optional namespace filter
            
        Returns:
            List of missing translation keys
        """
        try:
            # Get all translation keys
            keys_stmt = select(TranslationKey)
            if namespace:
                keys_stmt = keys_stmt.where(TranslationKey.namespace == namespace.value)
            
            all_keys = self.session.exec(keys_stmt).all()
            
            # Get existing translations for the language
            existing_stmt = select(Translation).where(Translation.language == language.value)
            existing_translations = self.session.exec(existing_stmt).all()
            existing_key_ids = {t.key_id for t in existing_translations}
            
            # Find missing translations
            missing = []
            for key in all_keys:
                if key.id not in existing_key_ids:
                    missing.append({
                        "namespace": key.namespace,
                        "key": key.key,
                        "context": key.context
                    })
            
            return missing
        except Exception as e:
            logger.error(f"Error getting missing translations: {e}")
            return []


class LocalizationService:
    """Service for handling localization and regional formatting."""
    
    def __init__(self, session: Session):
        self.session = session
        self.translation_service = TranslationService(session)
    
    def get_user_locale(self, user: AppUser) -> UserLocaleRead:
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
    
    def format_datetime_for_user(self, dt: datetime, user: AppUser) -> str:
        """Format datetime according to user's preferences."""
        locale = self.get_user_locale(user)
        return format_datetime(dt, locale)
    
    def format_number_for_user(self, number: float, user: AppUser) -> str:
        """Format number according to user's regional preferences."""
        locale = self.get_user_locale(user)
        return format_number(number, locale)
    
    def format_currency_for_user(self, amount: float, user: AppUser) -> str:
        """Format currency according to user's preferences."""
        locale = self.get_user_locale(user)
        return format_currency(amount, locale)
    
    def get_localized_content(
        self, 
        content: Dict[LanguageCode, str], 
        user: AppUser
    ) -> str:
        """
        Get localized content for a user.
        
        Args:
            content: Dictionary mapping languages to content
            user: User object with language preferences
            
        Returns:
            Localized content in user's preferred language
        """
        # Try user's preferred language first
        if user.preferred_language in content:
            return content[user.preferred_language]
        
        # Fallback to English
        if LanguageCode.ENGLISH in content:
            return content[LanguageCode.ENGLISH]
        
        # Fallback to first available language
        if content:
            return list(content.values())[0]
        
        return ""
    
    def get_multilingual_content(
        self, 
        content: Dict[LanguageCode, str], 
        requested_languages: List[LanguageCode]
    ) -> Dict[LanguageCode, str]:
        """
        Get multilingual content for requested languages.
        
        Args:
            content: Dictionary mapping languages to content
            requested_languages: List of requested languages
            
        Returns:
            Dictionary with content for requested languages
        """
        result = {}
        
        for language in requested_languages:
            if language in content:
                result[language] = content[language]
            elif LanguageCode.ENGLISH in content:
                result[language] = content[LanguageCode.ENGLISH]
            else:
                result[language] = ""
        
        return result


class ContentTranslationService:
    """Service for translating user-generated content."""
    
    def __init__(self, session: Session):
        self.session = session
        self.translation_service = TranslationService(session)
        self.localization_service = LocalizationService(session)
    
    def translate_post_content(
        self, 
        post_id: int, 
        target_language: LanguageCode,
        translator_id: Optional[int] = None
    ) -> bool:
        """
        Translate post content to a target language.
        
        Args:
            post_id: ID of the post to translate
            target_language: Target language for translation
            translator_id: Optional translator user ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the post
            post_stmt = select(Post).where(Post.id == post_id)
            post = self.session.exec(post_stmt).first()
            
            if not post:
                return False
            
            # Get existing content in primary language
            primary_content_stmt = select(PostContent).where(
                and_(
                    PostContent.post_id == post_id,
                    PostContent.is_primary == True
                )
            )
            primary_content = self.session.exec(primary_content_stmt).first()
            
            if not primary_content:
                return False
            
            # Check if translation already exists
            existing_stmt = select(PostContent).where(
                and_(
                    PostContent.post_id == post_id,
                    PostContent.language == target_language.value
                )
            )
            existing_translation = self.session.exec(existing_stmt).first()
            
            if existing_translation:
                # Update existing translation
                existing_translation.title = primary_content.title
                existing_translation.body_md = primary_content.body_md
                existing_translation.updated_at = datetime.utcnow()
                self.session.add(existing_translation)
            else:
                # Create new translation
                new_translation = PostContent(
                    post_id=post_id,
                    language=target_language.value,
                    title=primary_content.title,
                    body_md=primary_content.body_md,
                    is_primary=False
                )
                self.session.add(new_translation)
            
            self.session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error translating post content: {e}")
            return False
    
    def translate_room_content(
        self, 
        room_id: int, 
        target_language: LanguageCode
    ) -> bool:
        """
        Translate room content to a target language.
        
        Args:
            room_id: ID of the room to translate
            target_language: Target language for translation
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the room
            room_stmt = select(Room).where(Room.id == room_id)
            room = self.session.exec(room_stmt).first()
            
            if not room:
                return False
            
            # Get existing content in primary language
            primary_content_stmt = select(RoomContent).where(
                and_(
                    RoomContent.room_id == room_id,
                    RoomContent.is_primary == True
                )
            )
            primary_content = self.session.exec(primary_content_stmt).first()
            
            if not primary_content:
                return False
            
            # Check if translation already exists
            existing_stmt = select(RoomContent).where(
                and_(
                    RoomContent.room_id == room_id,
                    RoomContent.language == target_language.value
                )
            )
            existing_translation = self.session.exec(existing_stmt).first()
            
            if existing_translation:
                # Update existing translation
                existing_translation.title = primary_content.title
                existing_translation.description = primary_content.description
                existing_translation.updated_at = datetime.utcnow()
                self.session.add(existing_translation)
            else:
                # Create new translation
                new_translation = RoomContent(
                    room_id=room_id,
                    language=target_language.value,
                    title=primary_content.title,
                    description=primary_content.description,
                    is_primary=False
                )
                self.session.add(new_translation)
            
            self.session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error translating room content: {e}")
            return False
    
    def translate_trial_content(
        self, 
        trial_id: int, 
        target_language: LanguageCode
    ) -> bool:
        """
        Translate trial content to a target language.
        
        Args:
            trial_id: ID of the trial to translate
            target_language: Target language for translation
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the trial
            trial_stmt = select(Trial).where(Trial.id == trial_id)
            trial = self.session.exec(trial_stmt).first()
            
            if not trial:
                return False
            
            # Get existing content in primary language
            primary_content_stmt = select(TrialContent).where(
                and_(
                    TrialContent.trial_id == trial_id,
                    TrialContent.is_primary == True
                )
            )
            primary_content = self.session.exec(primary_content_stmt).first()
            
            if not primary_content:
                return False
            
            # Check if translation already exists
            existing_stmt = select(TrialContent).where(
                and_(
                    TrialContent.trial_id == trial_id,
                    TrialContent.language == target_language.value
                )
            )
            existing_translation = self.session.exec(existing_stmt).first()
            
            if existing_translation:
                # Update existing translation
                existing_translation.title = primary_content.title
                existing_translation.summary = primary_content.summary
                existing_translation.description = primary_content.description
                existing_translation.updated_at = datetime.utcnow()
                self.session.add(existing_translation)
            else:
                # Create new translation
                new_translation = TrialContent(
                    trial_id=trial_id,
                    language=target_language.value,
                    title=primary_content.title,
                    summary=primary_content.summary,
                    description=primary_content.description,
                    is_primary=False
                )
                self.session.add(new_translation)
            
            self.session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error translating trial content: {e}")
            return False


# =====================================================================
# Utility functions for internationalization
# =====================================================================

def get_user_language_from_headers(accept_language: str) -> LanguageCode:
    """Extract user's preferred language from Accept-Language header."""
    if not accept_language:
        return LanguageCode.ENGLISH
    
    # Parse Accept-Language header
    languages = []
    for lang in accept_language.split(','):
        lang = lang.strip().split(';')[0].split('-')[0]
        try:
            languages.append(LanguageCode(lang))
        except ValueError:
            continue
    
    # Return first supported language or English as fallback
    return languages[0] if languages else LanguageCode.ENGLISH


def get_user_timezone_from_headers(timezone: Optional[str]) -> TimezoneCode:
    """Extract user's timezone from headers."""
    if not timezone:
        return TimezoneCode.UTC
    
    try:
        return TimezoneCode(timezone)
    except ValueError:
        return TimezoneCode.UTC


def create_user_locale_from_headers(
    accept_language: str, 
    timezone: Optional[str] = None
) -> UserLocaleRead:
    """Create user locale from HTTP headers."""
    language = get_user_language_from_headers(accept_language)
    timezone_code = get_user_timezone_from_headers(timezone)
    
    # Default to US settings for now
    return UserLocaleRead(
        language=language,
        country=CountryCode.UNITED_STATES,
        timezone=timezone_code,
        date_format=DateFormat.ISO,
        time_format=TimeFormat.HOUR_24,
        currency=CurrencyCode.USD,
        measurement_unit=MeasurementUnit.METRIC
    )
