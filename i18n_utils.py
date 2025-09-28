"""
Internationalization utilities for the healthcare community platform.
Provides helper functions for multi-language support, localization, and regional formatting.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date, time
import pytz
import locale
import re
from decimal import Decimal
from models_i18n import (
    LanguageCode, CountryCode, TimezoneCode, DateFormat, TimeFormat, 
    MeasurementUnit, CurrencyCode, AppUser, UserLocaleRead
)
from i18n_config import (
    get_user_locale_from_headers, format_datetime, format_number, format_currency,
    DEFAULT_LANGUAGES, DEFAULT_COUNTRIES
)


class I18nUtils:
    """Utility class for internationalization operations."""
    
    @staticmethod
    def get_supported_languages() -> List[Dict[str, Any]]:
        """Get list of supported languages with metadata."""
        return [
            {
                "code": lang.code.value,
                "name": lang.name,
                "native_name": lang.native_name,
                "is_rtl": lang.is_rtl,
                "is_active": lang.is_active,
                "sort_order": lang.sort_order
            }
            for lang in DEFAULT_LANGUAGES
        ]
    
    @staticmethod
    def get_supported_countries() -> List[Dict[str, Any]]:
        """Get list of supported countries with metadata."""
        return [
            {
                "code": country.code.value,
                "name": country.name,
                "native_name": country.native_name,
                "language": country.language.value,
                "timezone": country.timezone.value,
                "currency": country.currency.value,
                "date_format": country.date_format.value,
                "time_format": country.time_format.value,
                "measurement_unit": country.measurement_unit.value,
                "is_active": country.is_active
            }
            for country in DEFAULT_COUNTRIES
        ]
    
    @staticmethod
    def detect_language_from_text(text: str) -> Optional[LanguageCode]:
        """
        Detect language from text content.
        
        Args:
            text: Text to analyze
            
        Returns:
            Detected language code or None if detection fails
        """
        if not text:
            return None
        
        # Simple language detection based on character patterns
        text_lower = text.lower()
        
        # Japanese detection (Hiragana, Katakana, Kanji)
        if re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', text):
            return LanguageCode.JAPANESE
        
        # Chinese detection (Simplified vs Traditional)
        if re.search(r'[\u4E00-\u9FAF]', text):
            # Simple heuristic: if text contains traditional characters, it's Traditional Chinese
            traditional_chars = re.search(r'[\u4E00-\u9FAF]', text)
            if traditional_chars:
                # This is a simplified check - in practice, you'd use a more sophisticated method
                return LanguageCode.CHINESE_SIMPLIFIED
        
        # Korean detection (Hangul)
        if re.search(r'[\uAC00-\uD7AF]', text):
            return LanguageCode.KOREAN
        
        # Arabic detection
        if re.search(r'[\u0600-\u06FF]', text):
            return LanguageCode.ARABIC
        
        # Hindi detection
        if re.search(r'[\u0900-\u097F]', text):
            return LanguageCode.HINDI
        
        # Cyrillic detection (Russian)
        if re.search(r'[\u0400-\u04FF]', text):
            return LanguageCode.RUSSIAN
        
        # Default to English for Latin script
        return LanguageCode.ENGLISH
    
    @staticmethod
    def get_language_direction(language: LanguageCode) -> str:
        """
        Get text direction for a language.
        
        Args:
            language: Language code
            
        Returns:
            'ltr' for left-to-right, 'rtl' for right-to-left
        """
        rtl_languages = {LanguageCode.ARABIC, LanguageCode.HINDI}
        return 'rtl' if language in rtl_languages else 'ltr'
    
    @staticmethod
    def get_language_name(language: LanguageCode, target_language: LanguageCode = LanguageCode.ENGLISH) -> str:
        """
        Get language name in target language.
        
        Args:
            language: Language to get name for
            target_language: Language to return name in
            
        Returns:
            Language name in target language
        """
        language_names = {
            LanguageCode.ENGLISH: {
                LanguageCode.ENGLISH: "English",
                LanguageCode.JAPANESE: "英語",
                LanguageCode.CHINESE_SIMPLIFIED: "英语",
                LanguageCode.KOREAN: "영어",
                LanguageCode.SPANISH: "Inglés",
                LanguageCode.FRENCH: "Anglais",
                LanguageCode.GERMAN: "Englisch",
                LanguageCode.ITALIAN: "Inglese",
                LanguageCode.PORTUGUESE: "Inglês",
                LanguageCode.RUSSIAN: "Английский",
                LanguageCode.ARABIC: "الإنجليزية",
                LanguageCode.HINDI: "अंग्रेजी"
            },
            LanguageCode.JAPANESE: {
                LanguageCode.ENGLISH: "Japanese",
                LanguageCode.JAPANESE: "日本語",
                LanguageCode.CHINESE_SIMPLIFIED: "日语",
                LanguageCode.KOREAN: "일본어",
                LanguageCode.SPANISH: "Japonés",
                LanguageCode.FRENCH: "Japonais",
                LanguageCode.GERMAN: "Japanisch",
                LanguageCode.ITALIAN: "Giapponese",
                LanguageCode.PORTUGUESE: "Japonês",
                LanguageCode.RUSSIAN: "Японский",
                LanguageCode.ARABIC: "اليابانية",
                LanguageCode.HINDI: "जापानी"
            }
        }
        
        if language in language_names and target_language in language_names[language]:
            return language_names[language][target_language]
        
        # Fallback to English name
        return language.value.title()


class LocalizationUtils:
    """Utility class for localization operations."""
    
    @staticmethod
    def format_datetime_for_user(dt: datetime, user: AppUser) -> str:
        """
        Format datetime according to user's preferences.
        
        Args:
            dt: Datetime to format
            user: User with locale preferences
            
        Returns:
            Formatted datetime string
        """
        # Convert to user's timezone
        if user.timezone != TimezoneCode.UTC:
            tz = pytz.timezone(user.timezone.value)
            dt = dt.astimezone(tz)
        
        # Format according to user preferences
        if user.date_format == DateFormat.ISO:
            if user.time_format == TimeFormat.HOUR_12:
                return dt.strftime("%Y-%m-%d %I:%M %p")
            else:
                return dt.strftime("%Y-%m-%d %H:%M")
        elif user.date_format == DateFormat.US:
            if user.time_format == TimeFormat.HOUR_12:
                return dt.strftime("%m/%d/%Y %I:%M %p")
            else:
                return dt.strftime("%m/%d/%Y %H:%M")
        elif user.date_format == DateFormat.EU:
            if user.time_format == TimeFormat.HOUR_12:
                return dt.strftime("%d/%m/%Y %I:%M %p")
            else:
                return dt.strftime("%d/%m/%Y %H:%M")
        else:
            return dt.strftime("%Y-%m-%d %H:%M")
    
    @staticmethod
    def format_date_for_user(d: date, user: AppUser) -> str:
        """
        Format date according to user's preferences.
        
        Args:
            d: Date to format
            user: User with locale preferences
            
        Returns:
            Formatted date string
        """
        if user.date_format == DateFormat.ISO:
            return d.strftime("%Y-%m-%d")
        elif user.date_format == DateFormat.US:
            return d.strftime("%m/%d/%Y")
        elif user.date_format == DateFormat.EU:
            return d.strftime("%d/%m/%Y")
        else:
            return d.strftime("%Y-%m-%d")
    
    @staticmethod
    def format_time_for_user(t: time, user: AppUser) -> str:
        """
        Format time according to user's preferences.
        
        Args:
            t: Time to format
            user: User with locale preferences
            
        Returns:
            Formatted time string
        """
        if user.time_format == TimeFormat.HOUR_12:
            return t.strftime("%I:%M %p")
        else:
            return t.strftime("%H:%M")
    
    @staticmethod
    def format_number_for_user(number: Union[int, float, Decimal], user: AppUser) -> str:
        """
        Format number according to user's regional preferences.
        
        Args:
            number: Number to format
            user: User with locale preferences
            
        Returns:
            Formatted number string
        """
        # Convert to float for formatting
        num = float(number)
        
        # Format based on user's country
        if user.country in [CountryCode.UNITED_STATES, CountryCode.CANADA]:
            return f"{num:,.2f}"
        elif user.country in [CountryCode.GERMANY, CountryCode.FRANCE, CountryCode.ITALY, CountryCode.SPAIN]:
            return f"{num:,.2f}".replace(",", " ").replace(".", ",")
        else:
            return f"{num:,.2f}"
    
    @staticmethod
    def format_currency_for_user(amount: Union[int, float, Decimal], user: AppUser) -> str:
        """
        Format currency according to user's preferences.
        
        Args:
            amount: Amount to format
            user: User with locale preferences
            
        Returns:
            Formatted currency string
        """
        # Currency symbols
        currency_symbols = {
            CurrencyCode.USD: "$",
            CurrencyCode.JPY: "¥",
            CurrencyCode.EUR: "€",
            CurrencyCode.GBP: "£",
            CurrencyCode.CNY: "¥",
            CurrencyCode.KRW: "₩",
            CurrencyCode.CAD: "C$",
            CurrencyCode.AUD: "A$",
            CurrencyCode.BRL: "R$",
            CurrencyCode.INR: "₹",
            CurrencyCode.RUB: "₽",
            CurrencyCode.SAR: "﷼",
        }
        
        symbol = currency_symbols.get(user.currency, "$")
        formatted_number = LocalizationUtils.format_number_for_user(amount, user)
        
        # Special handling for JPY (no decimals)
        if user.currency == CurrencyCode.JPY:
            return f"{symbol}{formatted_number.split('.')[0]}"
        else:
            return f"{symbol}{formatted_number}"
    
    @staticmethod
    def format_weight_for_user(weight: float, user: AppUser) -> str:
        """
        Format weight according to user's measurement unit.
        
        Args:
            weight: Weight in kg
            user: User with locale preferences
            
        Returns:
            Formatted weight string
        """
        if user.measurement_unit == MeasurementUnit.IMPERIAL:
            # Convert kg to lbs
            weight_lbs = weight * 2.20462
            return f"{weight_lbs:.1f} lbs"
        else:
            return f"{weight:.1f} kg"
    
    @staticmethod
    def format_height_for_user(height: float, user: AppUser) -> str:
        """
        Format height according to user's measurement unit.
        
        Args:
            height: Height in cm
            user: User with locale preferences
            
        Returns:
            Formatted height string
        """
        if user.measurement_unit == MeasurementUnit.IMPERIAL:
            # Convert cm to feet and inches
            total_inches = height / 2.54
            feet = int(total_inches // 12)
            inches = int(total_inches % 12)
            return f"{feet}'{inches}\""
        else:
            return f"{height:.1f} cm"
    
    @staticmethod
    def format_temperature_for_user(temp: float, user: AppUser) -> str:
        """
        Format temperature according to user's measurement unit.
        
        Args:
            temp: Temperature in Celsius
            user: User with locale preferences
            
        Returns:
            Formatted temperature string
        """
        if user.measurement_unit == MeasurementUnit.IMPERIAL:
            # Convert Celsius to Fahrenheit
            temp_f = (temp * 9/5) + 32
            return f"{temp_f:.1f}°F"
        else:
            return f"{temp:.1f}°C"


class ContentUtils:
    """Utility class for content internationalization."""
    
    @staticmethod
    def get_localized_content(
        content: Dict[LanguageCode, str], 
        user: AppUser,
        fallback_language: LanguageCode = LanguageCode.ENGLISH
    ) -> str:
        """
        Get localized content for a user.
        
        Args:
            content: Dictionary mapping languages to content
            user: User with language preferences
            fallback_language: Fallback language if user's language not available
            
        Returns:
            Localized content string
        """
        # Try user's preferred language first
        if user.preferred_language in content:
            return content[user.preferred_language]
        
        # Try fallback language
        if fallback_language in content:
            return content[fallback_language]
        
        # Try English as final fallback
        if LanguageCode.ENGLISH in content:
            return content[LanguageCode.ENGLISH]
        
        # Return first available content
        if content:
            return list(content.values())[0]
        
        return ""
    
    @staticmethod
    def get_multilingual_content(
        content: Dict[LanguageCode, str], 
        requested_languages: List[LanguageCode],
        fallback_language: LanguageCode = LanguageCode.ENGLISH
    ) -> Dict[LanguageCode, str]:
        """
        Get multilingual content for requested languages.
        
        Args:
            content: Dictionary mapping languages to content
            requested_languages: List of requested languages
            fallback_language: Fallback language for missing translations
            
        Returns:
            Dictionary with content for requested languages
        """
        result = {}
        
        for language in requested_languages:
            if language in content:
                result[language] = content[language]
            elif fallback_language in content:
                result[language] = content[fallback_language]
            elif LanguageCode.ENGLISH in content:
                result[language] = content[LanguageCode.ENGLISH]
            else:
                result[language] = ""
        
        return result
    
    @staticmethod
    def extract_language_from_content(content: str) -> Optional[LanguageCode]:
        """
        Extract language from content.
        
        Args:
            content: Content to analyze
            
        Returns:
            Detected language code or None
        """
        return I18nUtils.detect_language_from_text(content)
    
    @staticmethod
    def is_content_multilingual(content: Dict[LanguageCode, str]) -> bool:
        """
        Check if content is multilingual.
        
        Args:
            content: Dictionary mapping languages to content
            
        Returns:
            True if content has multiple languages, False otherwise
        """
        return len(content) > 1
    
    @staticmethod
    def get_primary_language(content: Dict[LanguageCode, str]) -> Optional[LanguageCode]:
        """
        Get primary language from multilingual content.
        
        Args:
            content: Dictionary mapping languages to content
            
        Returns:
            Primary language code or None
        """
        if not content:
            return None
        
        # Return first language (assuming it's primary)
        return list(content.keys())[0]
    
    @staticmethod
    def validate_content_translation(
        original: str, 
        translation: str, 
        language: LanguageCode
    ) -> Dict[str, Any]:
        """
        Validate content translation.
        
        Args:
            original: Original content
            translation: Translated content
            language: Target language
            
        Returns:
            Validation result dictionary
        """
        result = {
            "is_valid": True,
            "issues": [],
            "suggestions": []
        }
        
        # Check for empty translation
        if not translation.strip():
            result["is_valid"] = False
            result["issues"].append("Translation is empty")
            return result
        
        # Check for length differences (basic quality check)
        length_ratio = len(translation) / len(original) if original else 1
        if length_ratio < 0.1:
            result["issues"].append("Translation is too short")
            result["suggestions"].append("Check if translation is complete")
        elif length_ratio > 10:
            result["issues"].append("Translation is too long")
            result["suggestions"].append("Check if translation is too verbose")
        
        # Check for language consistency
        detected_language = I18nUtils.detect_language_from_text(translation)
        if detected_language != language:
            result["issues"].append(f"Translation language mismatch: expected {language.value}, got {detected_language.value if detected_language else 'unknown'}")
        
        return result


class ValidationUtils:
    """Utility class for internationalization validation."""
    
    @staticmethod
    def validate_language_code(language: str) -> bool:
        """
        Validate language code.
        
        Args:
            language: Language code to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            LanguageCode(language)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_country_code(country: str) -> bool:
        """
        Validate country code.
        
        Args:
            country: Country code to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            CountryCode(country)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_timezone(timezone: str) -> bool:
        """
        Validate timezone.
        
        Args:
            timezone: Timezone to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            pytz.timezone(timezone)
            return True
        except pytz.exceptions.UnknownTimeZoneError:
            return False
    
    @staticmethod
    def validate_locale_preferences(preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate user locale preferences.
        
        Args:
            preferences: User locale preferences
            
        Returns:
            Validation result dictionary
        """
        result = {
            "is_valid": True,
            "issues": [],
            "suggestions": []
        }
        
        # Validate language
        if "language" in preferences:
            if not ValidationUtils.validate_language_code(preferences["language"]):
                result["is_valid"] = False
                result["issues"].append("Invalid language code")
        
        # Validate country
        if "country" in preferences:
            if not ValidationUtils.validate_country_code(preferences["country"]):
                result["is_valid"] = False
                result["issues"].append("Invalid country code")
        
        # Validate timezone
        if "timezone" in preferences:
            if not ValidationUtils.validate_timezone(preferences["timezone"]):
                result["is_valid"] = False
                result["issues"].append("Invalid timezone")
        
        # Validate date format
        if "date_format" in preferences:
            try:
                DateFormat(preferences["date_format"])
            except ValueError:
                result["is_valid"] = False
                result["issues"].append("Invalid date format")
        
        # Validate time format
        if "time_format" in preferences:
            try:
                TimeFormat(preferences["time_format"])
            except ValueError:
                result["is_valid"] = False
                result["issues"].append("Invalid time format")
        
        # Validate currency
        if "currency" in preferences:
            try:
                CurrencyCode(preferences["currency"])
            except ValueError:
                result["is_valid"] = False
                result["issues"].append("Invalid currency code")
        
        # Validate measurement unit
        if "measurement_unit" in preferences:
            try:
                MeasurementUnit(preferences["measurement_unit"])
            except ValueError:
                result["is_valid"] = False
                result["issues"].append("Invalid measurement unit")
        
        return result


# =====================================================================
# Main utility functions
# =====================================================================

def get_user_locale_from_request(
    accept_language: str,
    timezone: Optional[str] = None,
    country: Optional[str] = None
) -> UserLocaleRead:
    """
    Get user locale from HTTP request headers.
    
    Args:
        accept_language: Accept-Language header value
        timezone: Timezone header value
        country: Country header value
        
    Returns:
        User locale preferences
    """
    return get_user_locale_from_headers(accept_language, timezone)


def format_content_for_user(
    content: Dict[LanguageCode, str],
    user: AppUser,
    fallback_language: LanguageCode = LanguageCode.ENGLISH
) -> str:
    """
    Format content for a specific user.
    
    Args:
        content: Multilingual content
        user: User with preferences
        fallback_language: Fallback language
        
    Returns:
        Localized content string
    """
    return ContentUtils.get_localized_content(content, user, fallback_language)


def format_datetime_for_user(dt: datetime, user: AppUser) -> str:
    """
    Format datetime for a specific user.
    
    Args:
        dt: Datetime to format
        user: User with preferences
        
    Returns:
        Formatted datetime string
    """
    return LocalizationUtils.format_datetime_for_user(dt, user)


def format_currency_for_user(amount: Union[int, float, Decimal], user: AppUser) -> str:
    """
    Format currency for a specific user.
    
    Args:
        amount: Amount to format
        user: User with preferences
        
    Returns:
        Formatted currency string
    """
    return LocalizationUtils.format_currency_for_user(amount, user)


def validate_translation_quality(
    original: str,
    translation: str,
    target_language: LanguageCode
) -> Dict[str, Any]:
    """
    Validate translation quality.
    
    Args:
        original: Original content
        translation: Translated content
        target_language: Target language
        
    Returns:
        Quality assessment dictionary
    """
    return ContentUtils.validate_content_translation(original, translation, target_language)
