"""
栄養管理用のSQLModel定義
疾患別の栄養管理システム
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum
from decimal import Decimal


class MealType(str, Enum):
    """食事の種類"""
    BREAKFAST = "breakfast"  # 朝食
    LUNCH = "lunch"  # 昼食
    DINNER = "dinner"  # 夕食
    SNACK = "snack"  # 間食
    OTHER = "other"  # その他


class DiseaseType(str, Enum):
    """疾患タイプ"""
    HEART_FAILURE = "heart_failure"  # 心不全
    DIABETES = "diabetes"  # 糖尿病
    CANCER = "cancer"  # がん
    KIDNEY_DISEASE = "kidney_disease"  # 腎疾患
    HYPERTENSION = "hypertension"  # 高血圧
    OTHER = "other"  # その他


class NutrientType(str, Enum):
    """栄養素の種類"""
    CALORIES = "calories"  # カロリー
    PROTEIN = "protein"  # タンパク質
    FAT = "fat"  # 脂質
    CARBOHYDRATE = "carbohydrate"  # 炭水化物
    SODIUM = "sodium"  # 塩分（ナトリウム）
    POTASSIUM = "potassium"  # カリウム
    PHOSPHORUS = "phosphorus"  # リン
    CALCIUM = "calcium"  # カルシウム
    IRON = "iron"  # 鉄
    FIBER = "fiber"  # 食物繊維
    SUGAR = "sugar"  # 糖質


class Menu(SQLModel, table=True):
    """メニュー（料理）マスタ"""
    __tablename__ = "menu"
    
    id: Optional[int] = Field(primary_key=True)
    name: str = Field(max_length=255, index=True)  # メニュー名
    description: Optional[str] = None  # 説明
    serving_size: str = Field(default="1人分")  # 1人分、100g等
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # リレーションシップ
    nutrients: List["MenuNutrient"] = Relationship(back_populates="menu")
    meal_logs: List["MealLog"] = Relationship(back_populates="menu")


class MenuNutrient(SQLModel, table=True):
    """メニューの栄養素情報"""
    __tablename__ = "menu_nutrient"
    
    id: Optional[int] = Field(primary_key=True)
    menu_id: int = Field(foreign_key="menu.id")
    nutrient_type: NutrientType = Field(index=True)
    amount: Decimal = Field(max_digits=10, decimal_places=3)  # 栄養素の量
    unit: str = Field(default="g")  # 単位（g, mg, kcal等）
    
    # リレーションシップ
    menu: Optional["Menu"] = Relationship(back_populates="nutrients")


class MealLog(SQLModel, table=True):
    """食事記録"""
    __tablename__ = "meal_log"
    
    id: Optional[int] = Field(primary_key=True)
    log_date: date = Field(index=True, default_factory=lambda: datetime.utcnow().date())
    meal_type: MealType = Field(index=True)
    menu_id: int = Field(foreign_key="menu.id")
    quantity: Decimal = Field(max_digits=10, decimal_places=3, default=1.0)  # 摂取量
    notes: Optional[str] = None  # メモ
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # リレーションシップ
    menu: Optional["Menu"] = Relationship(back_populates="meal_logs")


class DiseaseNutritionRequirement(SQLModel, table=True):
    """疾患別栄養要件"""
    __tablename__ = "disease_nutrition_requirement"
    
    id: Optional[int] = Field(primary_key=True)
    disease_type: DiseaseType = Field(index=True)
    nutrient_type: NutrientType = Field(index=True)
    daily_target_min: Optional[Decimal] = Field(max_digits=10, decimal_places=3)  # 1日の目標最小値
    daily_target_max: Optional[Decimal] = Field(max_digits=10, decimal_places=3)  # 1日の目標最大値
    unit: str = Field(default="g")  # 単位
    description: Optional[str] = None  # 説明
    is_critical: bool = Field(default=False)  # 重要度（必須管理項目かどうか）
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserNutritionProfile(SQLModel, table=True):
    """ユーザーの栄養管理プロフィール"""
    __tablename__ = "user_nutrition_profile"
    
    id: Optional[int] = Field(primary_key=True)
    user_id: int = Field(foreign_key="account.id")  # 認証システムとの連携
    disease_types: List[DiseaseType] = Field(default_factory=list)  # 管理対象疾患
    daily_calorie_target: Optional[Decimal] = Field(max_digits=10, decimal_places=0)  # 1日のカロリー目標
    weight_kg: Optional[Decimal] = Field(max_digits=5, decimal_places=2)  # 体重
    height_cm: Optional[Decimal] = Field(max_digits=5, decimal_places=1)  # 身長
    activity_level: Optional[str] = None  # 活動レベル
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class NutritionReport(SQLModel, table=True):
    """栄養レポート（日別集計）"""
    __tablename__ = "nutrition_report"
    
    id: Optional[int] = Field(primary_key=True)
    user_id: int = Field(foreign_key="account.id")
    report_date: date = Field(index=True)
    nutrient_type: NutrientType = Field(index=True)
    total_amount: Decimal = Field(max_digits=10, decimal_places=3)  # 1日の合計摂取量
    target_min: Optional[Decimal] = Field(max_digits=10, decimal_places=3)  # 目標最小値
    target_max: Optional[Decimal] = Field(max_digits=10, decimal_places=3)  # 目標最大値
    unit: str = Field(default="g")
    is_within_target: bool = Field(default=True)  # 目標範囲内かどうか
    created_at: datetime = Field(default_factory=datetime.utcnow)
