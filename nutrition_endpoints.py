"""
栄養管理用のAPIエンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal

from nutrition_models import (
    Menu, MenuNutrient, MealLog, DiseaseNutritionRequirement,
    UserNutritionProfile, NutritionReport, MealType, NutrientType, DiseaseType
)
from nutrition_schemas import (
    MenuCreate, MenuRead, MenuUpdate, MenuNutrientCreate, MenuNutrientRead,
    MealLogCreate, MealLogRead, DiseaseNutritionRequirementCreate, DiseaseNutritionRequirementRead,
    UserNutritionProfileCreate, UserNutritionProfileRead, UserNutritionProfileUpdate,
    NutritionReportRead, DailyNutritionSummary, NutritionAnalysis,
    MenuSearchParams, MealLogSearchParams
)

# ルーター作成
nutrition_router = APIRouter(prefix="/nutrition", tags=["nutrition"])


# ============================================================================
# メニュー管理エンドポイント
# ============================================================================

@nutrition_router.post("/menus", response_model=MenuRead)
def create_menu(menu_data: MenuCreate, session: Session = Depends(get_session)):
    """メニューを作成"""
    # メニュー作成
    menu = Menu(
        name=menu_data.name,
        description=menu_data.description,
        serving_size=menu_data.serving_size
    )
    session.add(menu)
    session.flush()  # IDを取得するため
    
    # 栄養素情報を追加
    for nutrient_data in menu_data.nutrients:
        nutrient = MenuNutrient(
            menu_id=menu.id,
            nutrient_type=nutrient_data.nutrient_type,
            amount=nutrient_data.amount,
            unit=nutrient_data.unit
        )
        session.add(nutrient)
    
    session.commit()
    session.refresh(menu)
    return menu


@nutrition_router.get("/menus", response_model=List[MenuRead])
def list_menus(
    name: Optional[str] = Query(None, description="メニュー名で検索"),
    nutrient_type: Optional[NutrientType] = Query(None, description="栄養素タイプでフィルタ"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session)
):
    """メニュー一覧を取得"""
    stmt = select(Menu)
    
    if name:
        stmt = stmt.where(Menu.name.contains(name))
    
    if nutrient_type:
        stmt = stmt.join(MenuNutrient).where(MenuNutrient.nutrient_type == nutrient_type)
    
    stmt = stmt.offset(offset).limit(limit).order_by(Menu.name)
    
    menus = session.exec(stmt).all()
    return menus


@nutrition_router.get("/menus/{menu_id}", response_model=MenuRead)
def get_menu(menu_id: int, session: Session = Depends(get_session)):
    """メニュー詳細を取得"""
    menu = session.get(Menu, menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    return menu


@nutrition_router.put("/menus/{menu_id}", response_model=MenuRead)
def update_menu(menu_id: int, menu_data: MenuUpdate, session: Session = Depends(get_session)):
    """メニューを更新"""
    menu = session.get(Menu, menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    # 基本情報を更新
    if menu_data.name is not None:
        menu.name = menu_data.name
    if menu_data.description is not None:
        menu.description = menu_data.description
    if menu_data.serving_size is not None:
        menu.serving_size = menu_data.serving_size
    
    menu.updated_at = datetime.utcnow()
    
    # 栄養素情報を更新
    if menu_data.nutrients is not None:
        # 既存の栄養素を削除
        session.query(MenuNutrient).filter(MenuNutrient.menu_id == menu_id).delete()
        
        # 新しい栄養素を追加
        for nutrient_data in menu_data.nutrients:
            nutrient = MenuNutrient(
                menu_id=menu_id,
                nutrient_type=nutrient_data.nutrient_type,
                amount=nutrient_data.amount,
                unit=nutrient_data.unit
            )
            session.add(nutrient)
    
    session.commit()
    session.refresh(menu)
    return menu


@nutrition_router.delete("/menus/{menu_id}")
def delete_menu(menu_id: int, session: Session = Depends(get_session)):
    """メニューを削除"""
    menu = session.get(Menu, menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    session.delete(menu)
    session.commit()
    return {"message": "Menu deleted successfully"}


# ============================================================================
# 食事記録エンドポイント
# ============================================================================

@nutrition_router.post("/meal-logs", response_model=MealLogRead)
def create_meal_log(meal_data: MealLogCreate, session: Session = Depends(get_session)):
    """食事記録を作成"""
    # メニューの存在確認
    menu = session.get(Menu, meal_data.menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    # 食事記録作成
    meal_log = MealLog(
        log_date=meal_data.log_date or date.today(),
        meal_type=meal_data.meal_type,
        menu_id=meal_data.menu_id,
        quantity=meal_data.quantity,
        notes=meal_data.notes
    )
    
    session.add(meal_log)
    session.commit()
    session.refresh(meal_log)
    
    # レスポンス用に栄養素情報を計算
    total_nutrients = {}
    for nutrient in menu.nutrients:
        total_amount = nutrient.amount * meal_data.quantity
        total_nutrients[nutrient.nutrient_type.value] = {
            "amount": float(total_amount),
            "unit": nutrient.unit
        }
    
    return MealLogRead(
        id=meal_log.id,
        log_date=meal_log.log_date,
        meal_type=meal_log.meal_type,
        menu_id=meal_log.menu_id,
        menu_name=menu.name,
        quantity=meal_log.quantity,
        notes=meal_log.notes,
        created_at=meal_log.created_at,
        total_nutrients=total_nutrients
    )


@nutrition_router.get("/meal-logs", response_model=List[MealLogRead])
def list_meal_logs(
    user_id: int = Query(..., description="ユーザーID"),
    date_from: Optional[date] = Query(None, description="開始日"),
    date_to: Optional[date] = Query(None, description="終了日"),
    meal_type: Optional[MealType] = Query(None, description="食事タイプ"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session)
):
    """食事記録一覧を取得"""
    stmt = select(MealLog).join(Menu)
    
    if date_from:
        stmt = stmt.where(MealLog.log_date >= date_from)
    if date_to:
        stmt = stmt.where(MealLog.log_date <= date_to)
    if meal_type:
        stmt = stmt.where(MealLog.meal_type == meal_type)
    
    stmt = stmt.offset(offset).limit(limit).order_by(MealLog.log_date.desc(), MealLog.created_at.desc())
    
    meal_logs = session.exec(stmt).all()
    
    # レスポンス用に栄養素情報を計算
    result = []
    for meal_log in meal_logs:
        total_nutrients = {}
        for nutrient in meal_log.menu.nutrients:
            total_amount = nutrient.amount * meal_log.quantity
            total_nutrients[nutrient.nutrient_type.value] = {
                "amount": float(total_amount),
                "unit": nutrient.unit
            }
        
        result.append(MealLogRead(
            id=meal_log.id,
            log_date=meal_log.log_date,
            meal_type=meal_log.meal_type,
            menu_id=meal_log.menu_id,
            menu_name=meal_log.menu.name,
            quantity=meal_log.quantity,
            notes=meal_log.notes,
            created_at=meal_log.created_at,
            total_nutrients=total_nutrients
        ))
    
    return result


@nutrition_router.delete("/meal-logs/{meal_log_id}")
def delete_meal_log(meal_log_id: int, session: Session = Depends(get_session)):
    """食事記録を削除"""
    meal_log = session.get(MealLog, meal_log_id)
    if not meal_log:
        raise HTTPException(status_code=404, detail="Meal log not found")
    
    session.delete(meal_log)
    session.commit()
    return {"message": "Meal log deleted successfully"}


# ============================================================================
# 疾患別栄養要件エンドポイント
# ============================================================================

@nutrition_router.post("/disease-requirements", response_model=DiseaseNutritionRequirementRead)
def create_disease_requirement(
    requirement_data: DiseaseNutritionRequirementCreate,
    session: Session = Depends(get_session)
):
    """疾患別栄養要件を作成"""
    requirement = DiseaseNutritionRequirement(**requirement_data.dict())
    session.add(requirement)
    session.commit()
    session.refresh(requirement)
    return requirement


@nutrition_router.get("/disease-requirements", response_model=List[DiseaseNutritionRequirementRead])
def list_disease_requirements(
    disease_type: Optional[DiseaseType] = Query(None, description="疾患タイプでフィルタ"),
    session: Session = Depends(get_session)
):
    """疾患別栄養要件一覧を取得"""
    stmt = select(DiseaseNutritionRequirement)
    
    if disease_type:
        stmt = stmt.where(DiseaseNutritionRequirement.disease_type == disease_type)
    
    stmt = stmt.order_by(DiseaseNutritionRequirement.disease_type, DiseaseNutritionRequirement.nutrient_type)
    
    requirements = session.exec(stmt).all()
    return requirements


# ============================================================================
# ユーザー栄養プロフィールエンドポイント
# ============================================================================

@nutrition_router.post("/user-profiles", response_model=UserNutritionProfileRead)
def create_user_profile(
    profile_data: UserNutritionProfileCreate,
    session: Session = Depends(get_session)
):
    """ユーザー栄養プロフィールを作成"""
    profile = UserNutritionProfile(**profile_data.dict())
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


@nutrition_router.get("/user-profiles/{user_id}", response_model=UserNutritionProfileRead)
def get_user_profile(user_id: int, session: Session = Depends(get_session)):
    """ユーザー栄養プロフィールを取得"""
    profile = session.get(UserNutritionProfile, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User nutrition profile not found")
    return profile


@nutrition_router.put("/user-profiles/{user_id}", response_model=UserNutritionProfileRead)
def update_user_profile(
    user_id: int,
    profile_data: UserNutritionProfileUpdate,
    session: Session = Depends(get_session)
):
    """ユーザー栄養プロフィールを更新"""
    profile = session.get(UserNutritionProfile, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User nutrition profile not found")
    
    # 更新
    for field, value in profile_data.dict(exclude_unset=True).items():
        setattr(profile, field, value)
    
    profile.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(profile)
    return profile


# ============================================================================
# 栄養分析・レポートエンドポイント
# ============================================================================

@nutrition_router.get("/daily-summary/{user_id}/{target_date}", response_model=DailyNutritionSummary)
def get_daily_nutrition_summary(
    user_id: int,
    target_date: date,
    session: Session = Depends(get_session)
):
    """日別栄養サマリーを取得"""
    # その日の食事記録を取得
    meal_logs = session.exec(
        select(MealLog)
        .join(Menu)
        .where(and_(
            MealLog.log_date == target_date
        ))
    ).all()
    
    # 栄養素別に合計を計算
    nutrient_totals = {}
    meal_count = len(meal_logs)
    
    for meal_log in meal_logs:
        for nutrient in meal_log.menu.nutrients:
            key = nutrient.nutrient_type.value
            if key not in nutrient_totals:
                nutrient_totals[key] = Decimal('0')
            nutrient_totals[key] += nutrient.amount * meal_log.quantity
    
    # デフォルト値でサマリーを作成
    summary = DailyNutritionSummary(
        date=target_date,
        total_calories=nutrient_totals.get('calories', Decimal('0')),
        total_protein=nutrient_totals.get('protein', Decimal('0')),
        total_fat=nutrient_totals.get('fat', Decimal('0')),
        total_sodium=nutrient_totals.get('sodium', Decimal('0')),
        total_potassium=nutrient_totals.get('potassium', Decimal('0')),
        total_phosphorus=nutrient_totals.get('phosphorus', Decimal('0')),
        meal_count=meal_count,
        is_within_targets=True,  # 簡易実装
        warnings=[]
    )
    
    return summary


@nutrition_router.get("/nutrition-analysis/{user_id}/{target_date}", response_model=NutritionAnalysis)
def get_nutrition_analysis(
    user_id: int,
    target_date: date,
    session: Session = Depends(get_session)
):
    """栄養分析結果を取得"""
    # ユーザープロフィールを取得
    profile = session.get(UserNutritionProfile, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User nutrition profile not found")
    
    # 日別サマリーを取得
    daily_summary = get_daily_nutrition_summary(user_id, target_date, session)
    
    # 簡易的な推奨事項を生成
    recommendations = []
    if daily_summary.total_calories < 1000:
        recommendations.append("カロリー摂取量が少なすぎます。医師に相談してください。")
    if daily_summary.total_sodium > 6:  # 6g = 6000mg
        recommendations.append("塩分摂取量が多すぎます。減塩を心がけてください。")
    
    return NutritionAnalysis(
        date=target_date,
        user_profile=profile,
        daily_summary=daily_summary,
        nutrient_reports=[],  # 簡易実装
        recommendations=recommendations
    )


# ============================================================================
# ユーティリティエンドポイント
# ============================================================================

@nutrition_router.get("/nutrient-types")
def get_nutrient_types():
    """利用可能な栄養素タイプ一覧を取得"""
    return [{"value": nt.value, "label": nt.value} for nt in NutrientType]


@nutrition_router.get("/meal-types")
def get_meal_types():
    """利用可能な食事タイプ一覧を取得"""
    return [{"value": mt.value, "label": mt.value} for mt in MealType]


@nutrition_router.get("/disease-types")
def get_disease_types():
    """利用可能な疾患タイプ一覧を取得"""
    return [{"value": dt.value, "label": dt.value} for dt in DiseaseType]
