"""
Internationalization (i18n) configuration for the healthcare community platform.
Supports multiple languages, timezones, and regional settings.
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field
import json
from datetime import datetime
import pytz


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
    ISO = "YYYY-MM-DD"  # 2024-01-15
    US = "MM/DD/YYYY"    # 01/15/2024
    EU = "DD/MM/YYYY"    # 15/01/2024
    JAPAN = "YYYY年MM月DD日"  # 2024年01月15日


class TimeFormat(str, Enum):
    """Time format options."""
    HOUR_24 = "24h"      # 14:30
    HOUR_12 = "12h"       # 2:30 PM


class MeasurementUnit(str, Enum):
    """Measurement unit systems."""
    METRIC = "metric"     # kg, cm, °C
    IMPERIAL = "imperial" # lb, ft, °F


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


class LanguageInfo(BaseModel):
    """Language information model."""
    code: LanguageCode
    name: str
    native_name: str
    is_rtl: bool = False
    is_active: bool = True
    sort_order: int = 0


class CountryInfo(BaseModel):
    """Country information model."""
    code: CountryCode
    name: str
    native_name: str
    language: LanguageCode
    timezone: TimezoneCode
    currency: CurrencyCode
    date_format: DateFormat
    measurement_unit: MeasurementUnit
    is_active: bool = True


class UserLocale(BaseModel):
    """User locale preferences."""
    language: LanguageCode = LanguageCode.ENGLISH
    country: CountryCode = CountryCode.UNITED_STATES
    timezone: TimezoneCode = TimezoneCode.UTC
    date_format: DateFormat = DateFormat.ISO
    time_format: TimeFormat = TimeFormat.HOUR_24
    currency: CurrencyCode = CurrencyCode.USD
    measurement_unit: MeasurementUnit = MeasurementUnit.METRIC


class UserLocaleRead(BaseModel):
    """User locale preferences for API responses."""
    language: LanguageCode = LanguageCode.ENGLISH
    country: CountryCode = CountryCode.UNITED_STATES
    timezone: TimezoneCode = TimezoneCode.UTC
    date_format: DateFormat = DateFormat.ISO
    time_format: TimeFormat = TimeFormat.HOUR_24
    currency: CurrencyCode = CurrencyCode.USD
    measurement_unit: MeasurementUnit = MeasurementUnit.METRIC


class TranslationNamespace(str, Enum):
    """Translation namespaces for organizing translations."""
    UI = "ui"
    MEDICAL = "medical"
    COMMUNITY = "community"
    RESEARCH = "research"
    VALIDATION = "validation"
    ERROR = "error"


class TranslationKey(BaseModel):
    """Translation key model."""
    namespace: TranslationNamespace
    key: str
    context: Optional[str] = None
    is_plural: bool = False


class Translation(BaseModel):
    """Translation model."""
    namespace: TranslationNamespace
    key: str
    language: LanguageCode
    value: str
    context: Optional[str] = None
    is_plural: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Default language and country configurations
DEFAULT_LANGUAGES: List[LanguageInfo] = [
    LanguageInfo(code=LanguageCode.ENGLISH, name="English", native_name="English", sort_order=1),
    LanguageInfo(code=LanguageCode.JAPANESE, name="Japanese", native_name="日本語", sort_order=2),
    LanguageInfo(code=LanguageCode.CHINESE_SIMPLIFIED, name="Chinese (Simplified)", native_name="简体中文", sort_order=3),
    LanguageInfo(code=LanguageCode.CHINESE_TRADITIONAL, name="Chinese (Traditional)", native_name="繁體中文", sort_order=4),
    LanguageInfo(code=LanguageCode.KOREAN, name="Korean", native_name="한국어", sort_order=5),
    LanguageInfo(code=LanguageCode.SPANISH, name="Spanish", native_name="Español", sort_order=6),
    LanguageInfo(code=LanguageCode.FRENCH, name="French", native_name="Français", sort_order=7),
    LanguageInfo(code=LanguageCode.GERMAN, name="German", native_name="Deutsch", sort_order=8),
    LanguageInfo(code=LanguageCode.ITALIAN, name="Italian", native_name="Italiano", sort_order=9),
    LanguageInfo(code=LanguageCode.PORTUGUESE, name="Portuguese", native_name="Português", sort_order=10),
    LanguageInfo(code=LanguageCode.RUSSIAN, name="Russian", native_name="Русский", sort_order=11),
    LanguageInfo(code=LanguageCode.ARABIC, name="Arabic", native_name="العربية", is_rtl=True, sort_order=12),
    LanguageInfo(code=LanguageCode.HINDI, name="Hindi", native_name="हिन्दी", sort_order=13),
]

DEFAULT_COUNTRIES: List[CountryInfo] = [
    CountryInfo(
        code=CountryCode.UNITED_STATES,
        name="United States",
        native_name="United States",
        language=LanguageCode.ENGLISH,
        timezone=TimezoneCode.NEW_YORK,
        currency=CurrencyCode.USD,
        date_format=DateFormat.US,
        measurement_unit=MeasurementUnit.IMPERIAL
    ),
    CountryInfo(
        code=CountryCode.JAPAN,
        name="Japan",
        native_name="日本",
        language=LanguageCode.JAPANESE,
        timezone=TimezoneCode.TOKYO,
        currency=CurrencyCode.JPY,
        date_format=DateFormat.ISO,
        measurement_unit=MeasurementUnit.METRIC
    ),
    CountryInfo(
        code=CountryCode.CHINA,
        name="China",
        native_name="中国",
        language=LanguageCode.CHINESE_SIMPLIFIED,
        timezone=TimezoneCode.BEIJING,
        currency=CurrencyCode.CNY,
        date_format=DateFormat.ISO,
        measurement_unit=MeasurementUnit.METRIC
    ),
    CountryInfo(
        code=CountryCode.SOUTH_KOREA,
        name="South Korea",
        native_name="대한민국",
        language=LanguageCode.KOREAN,
        timezone=TimezoneCode.SEOUL,
        currency=CurrencyCode.KRW,
        date_format=DateFormat.ISO,
        measurement_unit=MeasurementUnit.METRIC
    ),
    CountryInfo(
        code=CountryCode.UNITED_KINGDOM,
        name="United Kingdom",
        native_name="United Kingdom",
        language=LanguageCode.ENGLISH,
        timezone=TimezoneCode.LONDON,
        currency=CurrencyCode.GBP,
        date_format=DateFormat.EU,
        measurement_unit=MeasurementUnit.METRIC
    ),
    CountryInfo(
        code=CountryCode.GERMANY,
        name="Germany",
        native_name="Deutschland",
        language=LanguageCode.GERMAN,
        timezone=TimezoneCode.PARIS,
        currency=CurrencyCode.EUR,
        date_format=DateFormat.EU,
        measurement_unit=MeasurementUnit.METRIC
    ),
    CountryInfo(
        code=CountryCode.FRANCE,
        name="France",
        native_name="France",
        language=LanguageCode.FRENCH,
        timezone=TimezoneCode.PARIS,
        currency=CurrencyCode.EUR,
        date_format=DateFormat.EU,
        measurement_unit=MeasurementUnit.METRIC
    ),
    CountryInfo(
        code=CountryCode.SPAIN,
        name="Spain",
        native_name="España",
        language=LanguageCode.SPANISH,
        timezone=TimezoneCode.PARIS,
        currency=CurrencyCode.EUR,
        date_format=DateFormat.EU,
        measurement_unit=MeasurementUnit.METRIC
    ),
    CountryInfo(
        code=CountryCode.ITALY,
        name="Italy",
        native_name="Italia",
        language=LanguageCode.ITALIAN,
        timezone=TimezoneCode.PARIS,
        currency=CurrencyCode.EUR,
        date_format=DateFormat.EU,
        measurement_unit=MeasurementUnit.METRIC
    ),
    CountryInfo(
        code=CountryCode.CANADA,
        name="Canada",
        native_name="Canada",
        language=LanguageCode.ENGLISH,
        timezone=TimezoneCode.CHICAGO,
        currency=CurrencyCode.CAD,
        date_format=DateFormat.ISO,
        measurement_unit=MeasurementUnit.METRIC
    ),
    CountryInfo(
        code=CountryCode.AUSTRALIA,
        name="Australia",
        native_name="Australia",
        language=LanguageCode.ENGLISH,
        timezone=TimezoneCode.SYDNEY,
        currency=CurrencyCode.AUD,
        date_format=DateFormat.ISO,
        measurement_unit=MeasurementUnit.METRIC
    ),
    CountryInfo(
        code=CountryCode.BRAZIL,
        name="Brazil",
        native_name="Brasil",
        language=LanguageCode.PORTUGUESE,
        timezone=TimezoneCode.CHICAGO,
        currency=CurrencyCode.BRL,
        date_format=DateFormat.ISO,
        measurement_unit=MeasurementUnit.METRIC
    ),
    CountryInfo(
        code=CountryCode.INDIA,
        name="India",
        native_name="भारत",
        language=LanguageCode.HINDI,
        timezone=TimezoneCode.BEIJING,
        currency=CurrencyCode.INR,
        date_format=DateFormat.ISO,
        measurement_unit=MeasurementUnit.METRIC
    ),
    CountryInfo(
        code=CountryCode.RUSSIA,
        name="Russia",
        native_name="Россия",
        language=LanguageCode.RUSSIAN,
        timezone=TimezoneCode.BEIJING,
        currency=CurrencyCode.RUB,
        date_format=DateFormat.ISO,
        measurement_unit=MeasurementUnit.METRIC
    ),
    CountryInfo(
        code=CountryCode.SAUDI_ARABIA,
        name="Saudi Arabia",
        native_name="المملكة العربية السعودية",
        language=LanguageCode.ARABIC,
        timezone=TimezoneCode.BEIJING,
        currency=CurrencyCode.SAR,
        date_format=DateFormat.ISO,
        measurement_unit=MeasurementUnit.METRIC
    ),
]

# Common translation keys
COMMON_TRANSLATION_KEYS: List[TranslationKey] = [
    # UI translations
    TranslationKey(namespace=TranslationNamespace.UI, key="welcome", context="Welcome message"),
    TranslationKey(namespace=TranslationNamespace.UI, key="login", context="Login button"),
    TranslationKey(namespace=TranslationNamespace.UI, key="logout", context="Logout button"),
    TranslationKey(namespace=TranslationNamespace.UI, key="save", context="Save button"),
    TranslationKey(namespace=TranslationNamespace.UI, key="cancel", context="Cancel button"),
    TranslationKey(namespace=TranslationNamespace.UI, key="delete", context="Delete button"),
    TranslationKey(namespace=TranslationNamespace.UI, key="edit", context="Edit button"),
    TranslationKey(namespace=TranslationNamespace.UI, key="create", context="Create button"),
    TranslationKey(namespace=TranslationNamespace.UI, key="search", context="Search placeholder"),
    TranslationKey(namespace=TranslationNamespace.UI, key="loading", context="Loading message"),
    TranslationKey(namespace=TranslationNamespace.UI, key="error", context="Error message"),
    TranslationKey(namespace=TranslationNamespace.UI, key="success", context="Success message"),
    
    # Medical translations
    TranslationKey(namespace=TranslationNamespace.MEDICAL, key="blood_pressure", context="Blood pressure measurement"),
    TranslationKey(namespace=TranslationNamespace.MEDICAL, key="weight", context="Weight measurement"),
    TranslationKey(namespace=TranslationNamespace.MEDICAL, key="height", context="Height measurement"),
    TranslationKey(namespace=TranslationNamespace.MEDICAL, key="temperature", context="Body temperature"),
    TranslationKey(namespace=TranslationNamespace.MEDICAL, key="heart_rate", context="Heart rate measurement"),
    TranslationKey(namespace=TranslationNamespace.MEDICAL, key="symptom", context="Symptom entry"),
    TranslationKey(namespace=TranslationNamespace.MEDICAL, key="medication", context="Medication management"),
    TranslationKey(namespace=TranslationNamespace.MEDICAL, key="dosage", context="Medication dosage"),
    TranslationKey(namespace=TranslationNamespace.MEDICAL, key="schedule", context="Medication schedule"),
    TranslationKey(namespace=TranslationNamespace.MEDICAL, key="side_effect", context="Medication side effect"),
    TranslationKey(namespace=TranslationNamespace.MEDICAL, key="allergy", context="Allergy information"),
    TranslationKey(namespace=TranslationNamespace.MEDICAL, key="condition", context="Medical condition"),
    TranslationKey(namespace=TranslationNamespace.MEDICAL, key="diagnosis", context="Medical diagnosis"),
    TranslationKey(namespace=TranslationNamespace.MEDICAL, key="treatment", context="Medical treatment"),
    TranslationKey(namespace=TranslationNamespace.MEDICAL, key="appointment", context="Medical appointment"),
    
    # Community translations
    TranslationKey(namespace=TranslationNamespace.COMMUNITY, key="post", context="Community post"),
    TranslationKey(namespace=TranslationNamespace.COMMUNITY, key="comment", context="Community comment"),
    TranslationKey(namespace=TranslationNamespace.COMMUNITY, key="like", context="Like button"),
    TranslationKey(namespace=TranslationNamespace.COMMUNITY, key="share", context="Share button"),
    TranslationKey(namespace=TranslationNamespace.COMMUNITY, key="follow", context="Follow button"),
    TranslationKey(namespace=TranslationNamespace.COMMUNITY, key="unfollow", context="Unfollow button"),
    TranslationKey(namespace=TranslationNamespace.COMMUNITY, key="group", context="Community group"),
    TranslationKey(namespace=TranslationNamespace.COMMUNITY, key="member", context="Group member"),
    TranslationKey(namespace=TranslationNamespace.COMMUNITY, key="moderator", context="Group moderator"),
    TranslationKey(namespace=TranslationNamespace.COMMUNITY, key="admin", context="Group administrator"),
    
    # Research translations
    TranslationKey(namespace=TranslationNamespace.RESEARCH, key="clinical_trial", context="Clinical trial"),
    TranslationKey(namespace=TranslationNamespace.RESEARCH, key="study", context="Research study"),
    TranslationKey(namespace=TranslationNamespace.RESEARCH, key="participant", context="Study participant"),
    TranslationKey(namespace=TranslationNamespace.RESEARCH, key="researcher", context="Research investigator"),
    TranslationKey(namespace=TranslationNamespace.RESEARCH, key="consent", context="Informed consent"),
    TranslationKey(namespace=TranslationNamespace.RESEARCH, key="eligibility", context="Study eligibility"),
    TranslationKey(namespace=TranslationNamespace.RESEARCH, key="exclusion", context="Exclusion criteria"),
    TranslationKey(namespace=TranslationNamespace.RESEARCH, key="inclusion", context="Inclusion criteria"),
    TranslationKey(namespace=TranslationNamespace.RESEARCH, key="phase", context="Trial phase"),
    TranslationKey(namespace=TranslationNamespace.RESEARCH, key="outcome", context="Study outcome"),
    
    # Validation translations
    TranslationKey(namespace=TranslationNamespace.VALIDATION, key="required", context="Required field validation"),
    TranslationKey(namespace=TranslationNamespace.VALIDATION, key="invalid_email", context="Invalid email validation"),
    TranslationKey(namespace=TranslationNamespace.VALIDATION, key="invalid_phone", context="Invalid phone validation"),
    TranslationKey(namespace=TranslationNamespace.VALIDATION, key="invalid_date", context="Invalid date validation"),
    TranslationKey(namespace=TranslationNamespace.VALIDATION, key="invalid_number", context="Invalid number validation"),
    TranslationKey(namespace=TranslationNamespace.VALIDATION, key="too_short", context="Too short validation"),
    TranslationKey(namespace=TranslationNamespace.VALIDATION, key="too_long", context="Too long validation"),
    TranslationKey(namespace=TranslationNamespace.VALIDATION, key="password_mismatch", context="Password mismatch validation"),
    
    # Error translations
    TranslationKey(namespace=TranslationNamespace.ERROR, key="not_found", context="Resource not found error"),
    TranslationKey(namespace=TranslationNamespace.ERROR, key="unauthorized", context="Unauthorized access error"),
    TranslationKey(namespace=TranslationNamespace.ERROR, key="forbidden", context="Forbidden access error"),
    TranslationKey(namespace=TranslationNamespace.ERROR, key="server_error", context="Internal server error"),
    TranslationKey(namespace=TranslationNamespace.ERROR, key="network_error", context="Network connection error"),
    TranslationKey(namespace=TranslationNamespace.ERROR, key="timeout", context="Request timeout error"),
    TranslationKey(namespace=TranslationNamespace.ERROR, key="validation_error", context="Data validation error"),
    TranslationKey(namespace=TranslationNamespace.ERROR, key="duplicate_error", context="Duplicate resource error"),
]


def get_supported_languages() -> List[LanguageInfo]:
    """Get list of supported languages."""
    return DEFAULT_LANGUAGES


def get_supported_countries() -> List[CountryInfo]:
    """Get list of supported countries."""
    return DEFAULT_COUNTRIES


def get_user_locale_from_headers(accept_language: str, timezone: Optional[str] = None) -> UserLocale:
    """Extract user locale preferences from HTTP headers."""
    # Parse Accept-Language header
    languages = []
    if accept_language:
        for lang in accept_language.split(','):
            lang = lang.strip().split(';')[0].split('-')[0]
            if lang in [l.code.value for l in DEFAULT_LANGUAGES]:
                languages.append(LanguageCode(lang))
    
    # Default to English if no supported language found
    if not languages:
        languages = [LanguageCode.ENGLISH]
    
    # Get country from timezone if available
    country = CountryCode.UNITED_STATES  # Default
    if timezone:
        for country_info in DEFAULT_COUNTRIES:
            if country_info.timezone.value == timezone:
                country = country_info.code
                break
    
    # Create user locale
    locale = UserLocale(
        language=languages[0],
        country=country
    )
    
    # Apply country-specific defaults
    country_info = next((c for c in DEFAULT_COUNTRIES if c.code == country), None)
    if country_info:
        locale.timezone = country_info.timezone
        locale.currency = country_info.currency
        locale.date_format = country_info.date_format
        locale.measurement_unit = country_info.measurement_unit
    
    return locale


def format_datetime(dt: datetime, locale: UserLocale) -> str:
    """Format datetime according to user locale."""
    # Convert to user timezone
    if locale.timezone != TimezoneCode.UTC:
        tz = pytz.timezone(locale.timezone.value)
        dt = dt.astimezone(tz)
    
    # Format according to locale preferences
    if locale.date_format == DateFormat.ISO:
        return dt.strftime("%Y-%m-%d %H:%M")
    elif locale.date_format == DateFormat.US:
        return dt.strftime("%m/%d/%Y %I:%M %p" if locale.time_format == TimeFormat.HOUR_12 else "%m/%d/%Y %H:%M")
    elif locale.date_format == DateFormat.EU:
        return dt.strftime("%d/%m/%Y %H:%M")
    elif locale.date_format == DateFormat.JAPAN:
        return dt.strftime("%Y年%m月%d日 %H:%M")
    else:
        return dt.strftime("%Y-%m-%d %H:%M")


def format_number(number: float, locale: UserLocale) -> str:
    """Format number according to user locale."""
    if locale.country in [CountryCode.UNITED_STATES, CountryCode.CANADA]:
        return f"{number:,.2f}"
    elif locale.country in [CountryCode.GERMANY, CountryCode.FRANCE, CountryCode.ITALY, CountryCode.SPAIN]:
        return f"{number:,.2f}".replace(",", " ").replace(".", ",")
    else:
        return f"{number:,.2f}"


def format_currency(amount: float, locale: UserLocale) -> str:
    """Format currency according to user locale."""
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
    
    symbol = currency_symbols.get(locale.currency, "$")
    formatted_number = format_number(amount, locale)
    
    if locale.currency == CurrencyCode.JPY:
        return f"{symbol}{formatted_number.split('.')[0]}"  # No decimals for JPY
    else:
        return f"{symbol}{formatted_number}"
