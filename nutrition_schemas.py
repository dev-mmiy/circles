"""
栄養管理用のPydanticスキーマ
API リクエスト/レスポンス用
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from nutrition_models import MealType, DiseaseType, NutrientType


# ============================================================================
# メニュー関連スキーマ
# ============================================================================

class MenuNutrientCreate(BaseModel):
    """メニュー栄養素作成"""
    nutrient_type: NutrientType
    amount: Decimal = Field(gt=0, description="栄養素の量")
    unit: str = Field(default="g", description="単位")


class MenuNutrientRead(BaseModel):
    """メニュー栄養素読み取り"""
    id: int
    menu_id: int
    nutrient_type: NutrientType
    amount: Decimal
    unit: str

    class Config:
        from_attributes = True


class MenuCreate(BaseModel):
    """メニュー作成"""
    name: str = Field(max_length=255, description="メニュー名")
    description: Optional[str] = None
    serving_size: str = Field(default="1人分", description="1人分、100g等")
    nutrients: List[MenuNutrientCreate] = Field(default_factory=list, description="栄養素情報")


class MenuRead(BaseModel):
    """メニュー読み取り"""
    id: int
    name: str
    description: Optional[str]
    serving_size: str
    nutrients: List[MenuNutrientRead]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MenuUpdate(BaseModel):
    """メニュー更新"""
    name: Optional[str] = None
    description: Optional[str] = None
    serving_size: Optional[str] = None
    nutrients: Optional[List[MenuNutrientCreate]] = None


# ============================================================================
# 食事記録関連スキーマ
# ============================================================================

class MealLogCreate(BaseModel):
    """食事記録作成"""
    log_date: Optional[date] = None
    meal_type: MealType
    menu_id: int
    quantity: Decimal = Field(gt=0, default=1.0, description="摂取量")
    notes: Optional[str] = None


class MealLogRead(BaseModel):
    """食事記録読み取り"""
    id: int
    log_date: date
    meal_type: MealType
    menu_id: int
    menu_name: str
    quantity: Decimal
    notes: Optional[str]
    created_at: datetime
    # 計算された栄養素情報
    total_nutrients: Dict[str, Dict[str, Any]]

    class Config:
        from_attributes = True


# ============================================================================
# 疾患別栄養要件関連スキーマ
# ============================================================================

class DiseaseNutritionRequirementCreate(BaseModel):
    """疾患別栄養要件作成"""
    disease_type: DiseaseType
    nutrient_type: NutrientType
    daily_target_min: Optional[Decimal] = None
    daily_target_max: Optional[Decimal] = None
    unit: str = Field(default="g")
    description: Optional[str] = None
    is_critical: bool = Field(default=False)


class DiseaseNutritionRequirementRead(BaseModel):
    """疾患別栄養要件読み取り"""
    id: int
    disease_type: DiseaseType
    nutrient_type: NutrientType
    daily_target_min: Optional[Decimal]
    daily_target_max: Optional[Decimal]
    unit: str
    description: Optional[str]
    is_critical: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# ユーザー栄養プロフィール関連スキーマ
# ============================================================================

class UserNutritionProfileCreate(BaseModel):
    """ユーザー栄養プロフィール作成"""
    disease_types: List[DiseaseType] = Field(default_factory=list)
    daily_calorie_target: Optional[Decimal] = None
    weight_kg: Optional[Decimal] = Field(gt=0, description="体重(kg)")
    height_cm: Optional[Decimal] = Field(gt=0, description="身長(cm)")
    activity_level: Optional[str] = None


class UserNutritionProfileRead(BaseModel):
    """ユーザー栄養プロフィール読み取り"""
    id: int
    user_id: int
    disease_types: List[DiseaseType]
    daily_calorie_target: Optional[Decimal]
    weight_kg: Optional[Decimal]
    height_cm: Optional[Decimal]
    activity_level: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserNutritionProfileUpdate(BaseModel):
    """ユーザー栄養プロフィール更新"""
    disease_types: Optional[List[DiseaseType]] = None
    daily_calorie_target: Optional[Decimal] = None
    weight_kg: Optional[Decimal] = None
    height_cm: Optional[Decimal] = None
    activity_level: Optional[str] = None


# ============================================================================
# 栄養レポート関連スキーマ
# ============================================================================

class NutritionReportRead(BaseModel):
    """栄養レポート読み取り"""
    id: int
    user_id: int
    report_date: date
    nutrient_type: NutrientType
    total_amount: Decimal
    target_min: Optional[Decimal]
    target_max: Optional[Decimal]
    unit: str
    is_within_target: bool
    created_at: datetime

    class Config:
        from_attributes = True


class DailyNutritionSummary(BaseModel):
    """日別栄養サマリー"""
    date: date
    total_calories: Decimal
    total_protein: Decimal
    total_fat: Decimal
    total_sodium: Decimal
    total_potassium: Decimal
    total_phosphorus: Decimal
    meal_count: int
    is_within_targets: bool
    warnings: List[str] = Field(default_factory=list)


class NutritionAnalysis(BaseModel):
    """栄養分析結果"""
    date: date
    user_profile: UserNutritionProfileRead
    daily_summary: DailyNutritionSummary
    nutrient_reports: List[NutritionReportRead]
    recommendations: List[str] = Field(default_factory=list)


# ============================================================================
# 検索・フィルタリング用スキーマ
# ============================================================================

class MenuSearchParams(BaseModel):
    """メニュー検索パラメータ"""
    name: Optional[str] = None
    nutrient_type: Optional[NutrientType] = None
    min_calories: Optional[Decimal] = None
    max_calories: Optional[Decimal] = None
    limit: int = Field(default=50, le=200)
    offset: int = Field(default=0, ge=0)


class MealLogSearchParams(BaseModel):
    """食事記録検索パラメータ"""
    user_id: int
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    meal_type: Optional[MealType] = None
    limit: int = Field(default=50, le=200)
    offset: int = Field(default=0, ge=0)
