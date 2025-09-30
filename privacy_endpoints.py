"""
プライバシー設定のAPIエンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from privacy_models import (
    UserPrivacySettings, PrivacySettingsUpdate, PrivacySettingsResponse,
    DataAccessRequest, DataAccessRequestCreate, DataAccessRequestResponse,
    PrivacyLevel, DataCategory
)
import json

# データベース依存関係（既存のものを使用）
def get_db():
    from sqlalchemy import create_engine
    import os
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    engine = create_engine(DATABASE_URL)
    with Session(engine) as session:
        yield session

router = APIRouter(prefix="/privacy", tags=["privacy"])

@router.get("/settings/{user_id}", response_model=PrivacySettingsResponse)
async def get_privacy_settings(user_id: int, db: Session = Depends(get_db)):
    """プライバシー設定の取得"""
    try:
        # 既存の設定を取得
        statement = select(UserPrivacySettings).where(UserPrivacySettings.user_id == user_id)
        settings = db.exec(statement).first()
        
        if not settings:
            # デフォルト設定を作成
            settings = UserPrivacySettings(user_id=user_id)
            db.add(settings)
            db.commit()
            db.refresh(settings)
        
        # 設定の要約を作成
        summary = {
            "total_categories": 6,
            "public_categories": 0,
            "private_categories": 0,
            "data_sharing_enabled": settings.allow_data_sharing,
            "research_participation": settings.allow_research_participation
        }
        
        # 各カテゴリの設定をカウント
        categories = [
            ("basic_info", settings.basic_info_level),
            ("health_data", settings.health_data_level),
            ("medical_info", settings.medical_info_level),
            ("emergency_contact", settings.emergency_contact_level),
            ("body_measurements", settings.body_measurements_level),
            ("vital_signs", settings.vital_signs_level)
        ]
        
        for category, level in categories:
            if level == PrivacyLevel.PUBLIC:
                summary["public_categories"] += 1
            elif level == PrivacyLevel.PRIVATE:
                summary["private_categories"] += 1
        
        return PrivacySettingsResponse(
            user_id=user_id,
            settings=settings,
            summary=summary
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"プライバシー設定の取得に失敗しました: {str(e)}")

@router.put("/settings/{user_id}", response_model=dict)
async def update_privacy_settings(
    user_id: int, 
    settings_update: PrivacySettingsUpdate, 
    db: Session = Depends(get_db)
):
    """プライバシー設定の更新"""
    try:
        # 既存の設定を取得
        statement = select(UserPrivacySettings).where(UserPrivacySettings.user_id == user_id)
        settings = db.exec(statement).first()
        
        if not settings:
            # 新規作成
            settings = UserPrivacySettings(user_id=user_id)
            db.add(settings)
        
        # 更新可能なフィールドを更新
        update_data = settings_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(settings, field):
                setattr(settings, field, value)
        
        settings.updated_at = datetime.utcnow()
        
        db.add(settings)
        db.commit()
        db.refresh(settings)
        
        return {
            "status": "success",
            "message": "プライバシー設定が更新されました",
            "user_id": user_id
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"プライバシー設定の更新に失敗しました: {str(e)}")

@router.post("/settings/{user_id}/reset", response_model=dict)
async def reset_privacy_settings(user_id: int, db: Session = Depends(get_db)):
    """プライバシー設定のリセット（デフォルト値に戻す）"""
    try:
        # 既存の設定を取得
        statement = select(UserPrivacySettings).where(UserPrivacySettings.user_id == user_id)
        settings = db.exec(statement).first()
        
        if not settings:
            settings = UserPrivacySettings(user_id=user_id)
            db.add(settings)
        else:
            # デフォルト値にリセット
            settings.basic_info_level = PrivacyLevel.PRIVATE
            settings.birth_date_visible = False
            settings.gender_visible = False
            settings.blood_type_visible = False
            settings.region_visible = False
            
            settings.health_data_level = PrivacyLevel.PRIVATE
            settings.height_visible = False
            settings.weight_visible = False
            settings.body_fat_visible = False
            settings.activity_level_visible = False
            
            settings.medical_info_level = PrivacyLevel.PRIVATE
            settings.medical_conditions_visible = False
            settings.medications_visible = False
            settings.allergies_visible = False
            settings.doctor_info_visible = False
            settings.insurance_visible = False
            
            settings.emergency_contact_level = PrivacyLevel.FAMILY_ONLY
            settings.emergency_contact_visible = True
            
            settings.body_measurements_level = PrivacyLevel.PRIVATE
            settings.body_measurements_visible = False
            
            settings.vital_signs_level = PrivacyLevel.PRIVATE
            settings.vital_signs_visible = False
            
            settings.allow_data_sharing = False
            settings.share_with_healthcare_providers = False
            settings.share_with_family = False
            settings.share_with_friends = False
            
            settings.allow_research_participation = False
            settings.allow_anonymous_statistics = False
            
            settings.updated_at = datetime.utcnow()
        
        db.add(settings)
        db.commit()
        
        return {
            "status": "success",
            "message": "プライバシー設定がデフォルトにリセットされました",
            "user_id": user_id
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"プライバシー設定のリセットに失敗しました: {str(e)}")

@router.get("/settings/{user_id}/summary", response_model=dict)
async def get_privacy_summary(user_id: int, db: Session = Depends(get_db)):
    """プライバシー設定の要約取得"""
    try:
        statement = select(UserPrivacySettings).where(UserPrivacySettings.user_id == user_id)
        settings = db.exec(statement).first()
        
        if not settings:
            return {
                "user_id": user_id,
                "has_settings": False,
                "message": "プライバシー設定がありません"
            }
        
        # 設定の詳細要約
        summary = {
            "user_id": user_id,
            "has_settings": True,
            "categories": {
                "basic_info": {
                    "level": settings.basic_info_level,
                    "visible_fields": {
                        "birth_date": settings.birth_date_visible,
                        "gender": settings.gender_visible,
                        "blood_type": settings.blood_type_visible,
                        "region": settings.region_visible
                    }
                },
                "health_data": {
                    "level": settings.health_data_level,
                    "visible_fields": {
                        "height": settings.height_visible,
                        "weight": settings.weight_visible,
                        "body_fat": settings.body_fat_visible,
                        "activity_level": settings.activity_level_visible
                    }
                },
                "medical_info": {
                    "level": settings.medical_info_level,
                    "visible_fields": {
                        "medical_conditions": settings.medical_conditions_visible,
                        "medications": settings.medications_visible,
                        "allergies": settings.allergies_visible,
                        "doctor_info": settings.doctor_info_visible,
                        "insurance": settings.insurance_visible
                    }
                },
                "emergency_contact": {
                    "level": settings.emergency_contact_level,
                    "visible": settings.emergency_contact_visible
                },
                "body_measurements": {
                    "level": settings.body_measurements_level,
                    "visible": settings.body_measurements_visible
                },
                "vital_signs": {
                    "level": settings.vital_signs_level,
                    "visible": settings.vital_signs_visible
                }
            },
            "data_sharing": {
                "enabled": settings.allow_data_sharing,
                "healthcare_providers": settings.share_with_healthcare_providers,
                "family": settings.share_with_family,
                "friends": settings.share_with_friends
            },
            "research": {
                "participation": settings.allow_research_participation,
                "anonymous_statistics": settings.allow_anonymous_statistics
            },
            "last_updated": settings.updated_at
        }
        
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"プライバシー設定の要約取得に失敗しました: {str(e)}")

@router.post("/data-access-request", response_model=dict)
async def create_data_access_request(
    request: DataAccessRequestCreate,
    requester_user_id: int,
    db: Session = Depends(get_db)
):
    """データアクセス要求の作成"""
    try:
        # 自分自身への要求は禁止
        if requester_user_id == request.target_user_id:
            raise HTTPException(status_code=400, detail="自分自身へのデータアクセス要求はできません")
        
        # 新しい要求を作成
        data_request = DataAccessRequest(
            requester_user_id=requester_user_id,
            target_user_id=request.target_user_id,
            requested_data_categories=json.dumps([cat.value for cat in request.requested_data_categories]),
            request_reason=request.request_reason
        )
        
        db.add(data_request)
        db.commit()
        db.refresh(data_request)
        
        return {
            "status": "success",
            "message": "データアクセス要求が作成されました",
            "request_id": data_request.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"データアクセス要求の作成に失敗しました: {str(e)}")

@router.get("/data-access-requests/{user_id}", response_model=List[dict])
async def get_data_access_requests(user_id: int, db: Session = Depends(get_db)):
    """データアクセス要求の一覧取得"""
    try:
        # 自分が受けた要求と送った要求を取得
        received_requests = db.exec(
            select(DataAccessRequest).where(DataAccessRequest.target_user_id == user_id)
        ).all()
        
        sent_requests = db.exec(
            select(DataAccessRequest).where(DataAccessRequest.requester_user_id == user_id)
        ).all()
        
        requests = []
        
        # 受けた要求
        for req in received_requests:
            requests.append({
                "id": req.id,
                "type": "received",
                "requester_user_id": req.requester_user_id,
                "target_user_id": req.target_user_id,
                "requested_categories": json.loads(req.requested_data_categories),
                "reason": req.request_reason,
                "status": req.status,
                "created_at": req.created_at,
                "responded_at": req.responded_at
            })
        
        # 送った要求
        for req in sent_requests:
            requests.append({
                "id": req.id,
                "type": "sent",
                "requester_user_id": req.requester_user_id,
                "target_user_id": req.target_user_id,
                "requested_categories": json.loads(req.requested_data_categories),
                "reason": req.request_reason,
                "status": req.status,
                "created_at": req.created_at,
                "responded_at": req.responded_at
            })
        
        return requests
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"データアクセス要求の取得に失敗しました: {str(e)}")

@router.put("/data-access-request/{request_id}/respond", response_model=dict)
async def respond_to_data_access_request(
    request_id: int,
    response: DataAccessRequestResponse,
    db: Session = Depends(get_db)
):
    """データアクセス要求への応答"""
    try:
        # 要求を取得
        statement = select(DataAccessRequest).where(DataAccessRequest.id == request_id)
        data_request = db.exec(statement).first()
        
        if not data_request:
            raise HTTPException(status_code=404, detail="データアクセス要求が見つかりません")
        
        if data_request.status != "pending":
            raise HTTPException(status_code=400, detail="既に応答済みの要求です")
        
        # 応答を更新
        data_request.status = response.status
        data_request.response_message = response.response_message
        data_request.responded_at = datetime.utcnow()
        
        db.add(data_request)
        db.commit()
        
        return {
            "status": "success",
            "message": f"データアクセス要求が{response.status}されました",
            "request_id": request_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"データアクセス要求への応答に失敗しました: {str(e)}")
