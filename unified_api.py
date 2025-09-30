"""
統合されたユーザー管理API
新しいデータベース構造に対応
"""

from fastapi import FastAPI, HTTPException, Depends, status
from sqlmodel import Session, create_engine, select
from typing import Optional, List
import os
from datetime import datetime, timezone

from new_models import (
    User, UserHealthProfile, UserSession, BodyMeasurement, PrivacySettings,
    UserRead, UserHealthProfileRead, BodyMeasurementRead, PrivacySettingsRead,
    IntegratedUserProfile, UserUpdate, UserHealthProfileUpdate, 
    BodyMeasurementCreate, PrivacySettingsUpdate
)

# データベース設定
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(DATABASE_URL, echo=True)

def get_db():
    """データベースセッションの取得"""
    with Session(engine) as session:
        yield session

# FastAPIアプリケーション
app = FastAPI(title="統合ユーザー管理API", version="2.0.0")

# 1. 統合プロフィール取得
@app.get("/users/{user_id}/profile", response_model=IntegratedUserProfile)
async def get_integrated_profile(user_id: int, db: Session = Depends(get_db)):
    """統合されたユーザープロフィールの取得"""
    
    # ユーザー情報の取得
    user = db.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # ヘルスプロファイルの取得
    health_profile = db.exec(
        select(UserHealthProfile).where(UserHealthProfile.user_id == user_id)
    ).first()
    
    # プライバシー設定の取得
    privacy_settings = db.exec(
        select(PrivacySettings).where(PrivacySettings.user_id == user_id)
    ).first()
    
    # 最新の体組成測定データの取得
    latest_measurement = db.exec(
        select(BodyMeasurement)
        .where(BodyMeasurement.user_id == user_id)
        .order_by(BodyMeasurement.measurement_date.desc())
        .limit(1)
    ).first()
    
    return IntegratedUserProfile(
        user=UserRead.model_validate(user),
        health_profile=UserHealthProfileRead.model_validate(health_profile) if health_profile else None,
        privacy_settings=PrivacySettingsRead.model_validate(privacy_settings) if privacy_settings else None,
        latest_measurement=BodyMeasurementRead.model_validate(latest_measurement) if latest_measurement else None
    )

# 2. 統合プロフィール更新
@app.put("/users/{user_id}/profile")
async def update_integrated_profile(
    user_id: int,
    user_update: Optional[UserUpdate] = None,
    health_update: Optional[UserHealthProfileUpdate] = None,
    privacy_update: Optional[PrivacySettingsUpdate] = None,
    db: Session = Depends(get_db)
):
    """統合されたユーザープロフィールの更新"""
    
    # ユーザーの存在確認
    user = db.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_fields = []
    
    # ユーザー基本情報の更新
    if user_update:
        user_data = user_update.model_dump(exclude_unset=True)
        for field, value in user_data.items():
            setattr(user, field, value)
        updated_fields.append("user")
    
    # ヘルスプロファイルの更新
    if health_update:
        health_profile = db.exec(
            select(UserHealthProfile).where(UserHealthProfile.user_id == user_id)
        ).first()
        
        if not health_profile:
            # ヘルスプロファイルが存在しない場合は作成
            health_profile = UserHealthProfile(user_id=user_id)
            db.add(health_profile)
        
        health_data = health_update.model_dump(exclude_unset=True)
        for field, value in health_data.items():
            setattr(health_profile, field, value)
        health_profile.updated_at = datetime.utcnow()
        updated_fields.append("health_profile")
    
    # プライバシー設定の更新
    if privacy_update:
        privacy_settings = db.exec(
            select(PrivacySettings).where(PrivacySettings.user_id == user_id)
        ).first()
        
        if not privacy_settings:
            # プライバシー設定が存在しない場合は作成
            privacy_settings = PrivacySettings(user_id=user_id)
            db.add(privacy_settings)
        
        privacy_data = privacy_update.model_dump(exclude_unset=True)
        for field, value in privacy_data.items():
            setattr(privacy_settings, field, value)
        privacy_settings.updated_at = datetime.utcnow()
        updated_fields.append("privacy_settings")
    
    # 更新日時の設定
    user.updated_at = datetime.utcnow()
    
    # データベースに保存
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {
        "status": "success",
        "message": f"Profile updated successfully. Updated fields: {', '.join(updated_fields)}",
        "user_id": user_id
    }

# 3. 体組成測定データの追加
@app.post("/users/{user_id}/measurements", response_model=BodyMeasurementRead)
async def add_body_measurement(
    user_id: int,
    measurement: BodyMeasurementCreate,
    db: Session = Depends(get_db)
):
    """体組成測定データの追加"""
    
    # ユーザーの存在確認
    user = db.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 測定データの作成
    body_measurement = BodyMeasurement(
        user_id=user_id,
        **measurement.model_dump()
    )
    
    db.add(body_measurement)
    db.commit()
    db.refresh(body_measurement)
    
    return BodyMeasurementRead.model_validate(body_measurement)

# 4. 体組成測定データの取得
@app.get("/users/{user_id}/measurements", response_model=List[BodyMeasurementRead])
async def get_body_measurements(
    user_id: int,
    limit: int = 30,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """体組成測定データの取得"""
    
    # ユーザーの存在確認
    user = db.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 測定データの取得
    measurements = db.exec(
        select(BodyMeasurement)
        .where(BodyMeasurement.user_id == user_id)
        .order_by(BodyMeasurement.measurement_date.desc())
        .offset(offset)
        .limit(limit)
    ).all()
    
    return [BodyMeasurementRead.model_validate(m) for m in measurements]

# 5. プライバシー設定の取得
@app.get("/users/{user_id}/privacy", response_model=PrivacySettingsRead)
async def get_privacy_settings(user_id: int, db: Session = Depends(get_db)):
    """プライバシー設定の取得"""
    
    # ユーザーの存在確認
    user = db.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # プライバシー設定の取得
    privacy_settings = db.exec(
        select(PrivacySettings).where(PrivacySettings.user_id == user_id)
    ).first()
    
    if not privacy_settings:
        # デフォルト設定を作成
        privacy_settings = PrivacySettings(user_id=user_id)
        db.add(privacy_settings)
        db.commit()
        db.refresh(privacy_settings)
    
    return PrivacySettingsRead.model_validate(privacy_settings)

# 6. ヘルス計算（BMI、理想体重など）
@app.get("/users/{user_id}/health/calculations")
async def get_health_calculations(user_id: int, db: Session = Depends(get_db)):
    """ヘルス計算の実行"""
    
    # ユーザーの存在確認
    user = db.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # ヘルスプロファイルの取得
    health_profile = db.exec(
        select(UserHealthProfile).where(UserHealthProfile.user_id == user_id)
    ).first()
    
    if not health_profile:
        raise HTTPException(status_code=404, detail="Health profile not found")
    
    # 最新の測定データの取得
    latest_measurement = db.exec(
        select(BodyMeasurement)
        .where(BodyMeasurement.user_id == user_id)
        .order_by(BodyMeasurement.measurement_date.desc())
        .limit(1)
    ).first()
    
    calculations = {}
    
    # 身長と体重が利用可能な場合の計算
    if health_profile.height_cm and latest_measurement and latest_measurement.weight_kg:
        height_m = health_profile.height_cm / 100
        weight = latest_measurement.weight_kg
        
        # BMI計算
        bmi = weight / (height_m ** 2)
        calculations["bmi"] = round(bmi, 1)
        
        # BMI分類
        if bmi < 18.5:
            bmi_category = "低体重"
        elif bmi < 25:
            bmi_category = "普通体重"
        elif bmi < 30:
            bmi_category = "肥満（1度）"
        elif bmi < 35:
            bmi_category = "肥満（2度）"
        else:
            bmi_category = "肥満（3度）"
        
        calculations["bmi_category"] = bmi_category
        
        # 理想体重の計算（BMI 22を基準）
        ideal_weight = 22 * (height_m ** 2)
        calculations["ideal_weight_kg"] = round(ideal_weight, 1)
        
        # 目標体重との比較
        if health_profile.target_weight_kg:
            weight_diff = latest_measurement.weight_kg - health_profile.target_weight_kg
            calculations["weight_difference_kg"] = round(weight_diff, 1)
    
    # 活動レベルに基づく推定カロリー必要量
    if health_profile.activity_level and latest_measurement and latest_measurement.weight_kg:
        weight = latest_measurement.weight_kg
        height_cm = health_profile.height_cm or 170  # デフォルト身長
        
        # 基礎代謝量の計算（ハリス・ベネディクト式）
        if health_profile.gender == "male":
            bmr = 88.362 + (13.397 * weight) + (4.799 * height_cm) - (5.677 * 30)  # 30歳と仮定
        else:
            bmr = 447.593 + (9.247 * weight) + (3.098 * height_cm) - (4.330 * 30)
        
        # 活動レベル係数
        activity_multipliers = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "high": 1.725,
            "very_high": 1.9
        }
        
        multiplier = activity_multipliers.get(health_profile.activity_level, 1.55)
        daily_calories = bmr * multiplier
        
        calculations["estimated_daily_calories"] = round(daily_calories, 0)
    
    return {
        "status": "success",
        "user_id": user_id,
        "calculations": calculations,
        "profile_data": {
            "height_cm": health_profile.height_cm,
            "current_weight_kg": latest_measurement.weight_kg if latest_measurement else None,
            "target_weight_kg": health_profile.target_weight_kg,
            "activity_level": health_profile.activity_level
        }
    }

# 7. ヘルスサマリー
@app.get("/users/{user_id}/health/summary")
async def get_health_summary(user_id: int, db: Session = Depends(get_db)):
    """ヘルスサマリーの取得"""
    
    # ユーザーの存在確認
    user = db.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # ヘルスプロファイルの取得
    health_profile = db.exec(
        select(UserHealthProfile).where(UserHealthProfile.user_id == user_id)
    ).first()
    
    # 最新の測定データの取得
    latest_measurement = db.exec(
        select(BodyMeasurement)
        .where(BodyMeasurement.user_id == user_id)
        .order_by(BodyMeasurement.measurement_date.desc())
        .limit(1)
    ).first()
    
    # 過去30日間の測定データの取得
    thirty_days_ago = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    recent_measurements = db.exec(
        select(BodyMeasurement)
        .where(
            BodyMeasurement.user_id == user_id,
            BodyMeasurement.measurement_date >= thirty_days_ago
        )
        .order_by(BodyMeasurement.measurement_date.desc())
    ).all()
    
    summary = {
        "user_info": {
            "name": f"{user.first_name_local or ''} {user.last_name_local or ''}".strip(),
            "email": user.email
        },
        "current_status": {
            "height_cm": health_profile.height_cm if health_profile else None,
            "current_weight_kg": latest_measurement.weight_kg if latest_measurement else None,
            "body_fat_percentage": latest_measurement.body_fat_percentage if latest_measurement else None,
            "last_measurement_date": latest_measurement.measurement_date if latest_measurement else None
        },
        "targets": {
            "target_weight_kg": health_profile.target_weight_kg if health_profile else None,
            "target_body_fat_percentage": health_profile.target_body_fat_percentage if health_profile else None,
            "activity_level": health_profile.activity_level if health_profile else None
        },
        "recent_trends": {
            "measurement_count_30days": len(recent_measurements),
            "weight_trend": None,
            "body_fat_trend": None
        }
    }
    
    # 体重と体脂肪率のトレンド計算
    if len(recent_measurements) >= 2:
        weights = [m.weight_kg for m in recent_measurements if m.weight_kg is not None]
        body_fats = [m.body_fat_percentage for m in recent_measurements if m.body_fat_percentage is not None]
        
        if len(weights) >= 2:
            weight_change = weights[0] - weights[-1]  # 最新 - 最古
            summary["recent_trends"]["weight_trend"] = round(weight_change, 1)
        
        if len(body_fats) >= 2:
            body_fat_change = body_fats[0] - body_fats[-1]  # 最新 - 最古
            summary["recent_trends"]["body_fat_trend"] = round(body_fat_change, 1)
    
    return {
        "status": "success",
        "user_id": user_id,
        "summary": summary
    }

# ヘルスチェック
@app.get("/health")
async def health_check():
    """APIヘルスチェック"""
    return {"status": "healthy", "message": "統合ユーザー管理API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
