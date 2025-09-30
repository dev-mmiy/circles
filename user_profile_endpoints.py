"""
拡張ユーザープロファイル管理のAPIエンドポイント
生年月日、性別、血液型、地域、健康データ履歴の管理
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime, date
import os

from user_profile_models import (
    UserProfileExtended, UserProfileExtendedCreate, UserProfileExtendedRead, UserProfileExtendedUpdate,
    BodyMeasurement, BodyMeasurementCreate, BodyMeasurementRead, BodyMeasurementUpdate,
    VitalSign, VitalSignCreate, VitalSignRead, VitalSignUpdate,
    HealthStats
)

# データベース設定
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
from sqlmodel import create_engine, SQLModel

engine = create_engine(DATABASE_URL, echo=True)

def get_db() -> Session:
    """データベースセッション取得"""
    with Session(engine) as session:
        yield session

# ルーター作成
router = APIRouter(prefix="/user-profile", tags=["user-profile"])


# ==================== 拡張プロファイル管理 ====================

@router.post("/extended", response_model=UserProfileExtendedRead, status_code=status.HTTP_201_CREATED)
async def create_extended_profile(
    profile_data: UserProfileExtendedCreate,
    user_id: int,
    db: Session = Depends(get_db)
):
    """拡張プロファイル作成"""
    try:
        # 既存のプロファイルをチェック
        existing = db.exec(select(UserProfileExtended).where(UserProfileExtended.user_id == user_id)).first()
        if existing:
            raise HTTPException(status_code=400, detail="Extended profile already exists")
        
        # 新しいプロファイルを作成
        profile = UserProfileExtended(
            user_id=user_id,
            **profile_data.model_dump(exclude_unset=True)
        )
        
        db.add(profile)
        db.commit()
        db.refresh(profile)
        
        return profile
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/extended/{user_id}", response_model=UserProfileExtendedRead)
async def get_extended_profile(user_id: int, db: Session = Depends(get_db)):
    """拡張プロファイル取得"""
    profile = db.exec(select(UserProfileExtended).where(UserProfileExtended.user_id == user_id)).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Extended profile not found")
    return profile


@router.put("/extended/{user_id}", response_model=UserProfileExtendedRead)
async def update_extended_profile(
    user_id: int,
    profile_data: UserProfileExtendedUpdate,
    db: Session = Depends(get_db)
):
    """拡張プロファイル更新"""
    try:
        profile = db.exec(select(UserProfileExtended).where(UserProfileExtended.user_id == user_id)).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Extended profile not found")
        
        # 更新データを適用
        for field, value in profile_data.model_dump(exclude_unset=True).items():
            setattr(profile, field, value)
        
        profile.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(profile)
        
        return profile
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== 体重・体脂肪率管理 ====================

@router.post("/body-measurements", response_model=BodyMeasurementRead, status_code=status.HTTP_201_CREATED)
async def create_body_measurement(
    measurement_data: BodyMeasurementCreate,
    user_id: int,
    db: Session = Depends(get_db)
):
    """体重・体脂肪率記録作成"""
    try:
        measurement = BodyMeasurement(
            user_id=user_id,
            **measurement_data.model_dump()
        )
        
        db.add(measurement)
        db.commit()
        db.refresh(measurement)
        
        return measurement
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/body-measurements/{user_id}", response_model=List[BodyMeasurementRead])
async def get_body_measurements(
    user_id: int,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """体重・体脂肪率履歴取得"""
    measurements = db.exec(
        select(BodyMeasurement)
        .where(BodyMeasurement.user_id == user_id)
        .order_by(BodyMeasurement.measurement_date.desc())
        .offset(offset)
        .limit(limit)
    ).all()
    
    return measurements


@router.put("/body-measurements/{measurement_id}", response_model=BodyMeasurementRead)
async def update_body_measurement(
    measurement_id: int,
    measurement_data: BodyMeasurementUpdate,
    db: Session = Depends(get_db)
):
    """体重・体脂肪率記録更新"""
    try:
        measurement = db.get(BodyMeasurement, measurement_id)
        if not measurement:
            raise HTTPException(status_code=404, detail="Body measurement not found")
        
        # 更新データを適用
        for field, value in measurement_data.model_dump(exclude_unset=True).items():
            setattr(measurement, field, value)
        
        measurement.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(measurement)
        
        return measurement
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/body-measurements/{measurement_id}")
async def delete_body_measurement(measurement_id: int, db: Session = Depends(get_db)):
    """体重・体脂肪率記録削除"""
    measurement = db.get(BodyMeasurement, measurement_id)
    if not measurement:
        raise HTTPException(status_code=404, detail="Body measurement not found")
    
    db.delete(measurement)
    db.commit()
    
    return {"message": "Body measurement deleted successfully"}


# ==================== バイタルサイン管理 ====================

@router.post("/vital-signs", response_model=VitalSignRead, status_code=status.HTTP_201_CREATED)
async def create_vital_sign(
    vital_data: VitalSignCreate,
    user_id: int,
    db: Session = Depends(get_db)
):
    """バイタルサイン記録作成"""
    try:
        vital = VitalSign(
            user_id=user_id,
            **vital_data.model_dump()
        )
        
        db.add(vital)
        db.commit()
        db.refresh(vital)
        
        return vital
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/vital-signs/{user_id}", response_model=List[VitalSignRead])
async def get_vital_signs(
    user_id: int,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """バイタルサイン履歴取得"""
    vitals = db.exec(
        select(VitalSign)
        .where(VitalSign.user_id == user_id)
        .order_by(VitalSign.measurement_date.desc())
        .offset(offset)
        .limit(limit)
    ).all()
    
    return vitals


@router.put("/vital-signs/{vital_id}", response_model=VitalSignRead)
async def update_vital_sign(
    vital_id: int,
    vital_data: VitalSignUpdate,
    db: Session = Depends(get_db)
):
    """バイタルサイン記録更新"""
    try:
        vital = db.get(VitalSign, vital_id)
        if not vital:
            raise HTTPException(status_code=404, detail="Vital sign not found")
        
        # 更新データを適用
        for field, value in vital_data.model_dump(exclude_unset=True).items():
            setattr(vital, field, value)
        
        vital.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(vital)
        
        return vital
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/vital-signs/{vital_id}")
async def delete_vital_sign(vital_id: int, db: Session = Depends(get_db)):
    """バイタルサイン記録削除"""
    vital = db.get(VitalSign, vital_id)
    if not vital:
        raise HTTPException(status_code=404, detail="Vital sign not found")
    
    db.delete(vital)
    db.commit()
    
    return {"message": "Vital sign deleted successfully"}


# ==================== 統計・分析 ====================

@router.get("/health-stats/{user_id}", response_model=HealthStats)
async def get_health_stats(user_id: int, db: Session = Depends(get_db)):
    """健康統計取得"""
    try:
        # 最新の体重データ
        latest_weight = db.exec(
            select(BodyMeasurement.weight_kg, BodyMeasurement.body_fat_percentage, BodyMeasurement.measurement_date)
            .where(BodyMeasurement.user_id == user_id)
            .order_by(BodyMeasurement.measurement_date.desc())
        ).first()
        
        # 最新のバイタルサイン
        latest_vital = db.exec(
            select(VitalSign.body_temperature, VitalSign.systolic_bp, VitalSign.diastolic_bp, VitalSign.heart_rate, VitalSign.measurement_date)
            .where(VitalSign.user_id == user_id)
            .order_by(VitalSign.measurement_date.desc())
        ).first()
        
        # 測定回数
        weight_count = db.exec(select(BodyMeasurement).where(BodyMeasurement.user_id == user_id)).all()
        vital_count = db.exec(select(VitalSign).where(VitalSign.user_id == user_id)).all()
        
        # 統計データを構築
        stats = HealthStats(
            latest_weight=latest_weight.weight_kg if latest_weight else None,
            latest_body_fat=latest_weight.body_fat_percentage if latest_weight else None,
            latest_temperature=latest_vital.body_temperature if latest_vital else None,
            latest_systolic_bp=latest_vital.systolic_bp if latest_vital else None,
            latest_diastolic_bp=latest_vital.diastolic_bp if latest_vital else None,
            latest_heart_rate=latest_vital.heart_rate if latest_vital else None,
            measurement_count=len(weight_count) + len(vital_count),
            last_measurement_date=latest_weight.measurement_date if latest_weight else None
        )
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
