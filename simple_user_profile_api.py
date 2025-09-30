"""
シンプルなユーザープロファイルAPI
SQLModelを使わずに直接SQLクエリを実行
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, create_engine
from sqlalchemy import text
import os
from typing import List, Dict, Any
from datetime import datetime, timezone
from datetime_utils import to_utc_db, to_api_format
from validation_utils import validate_profile_data, format_validation_errors
from health_calculations import (
    calculate_bmi, calculate_health_progress, get_activity_level_calories,
    calculate_weight_loss_plan, calculate_age_from_birth_date
)
from privacy_endpoints import router as privacy_router

# データベース設定
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(DATABASE_URL, echo=True)

def get_db() -> Session:
    """データベースセッション取得"""
    with Session(engine) as session:
        yield session

app = FastAPI(title="Simple User Profile API", version="1.0.0")

# プライバシー設定ルーターを追加
app.include_router(privacy_router)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {"message": "Simple User Profile API", "version": "1.0.0"}

@app.get("/extended/{user_id}")
async def get_extended_profile(user_id: int, db: Session = Depends(get_db)):
    """拡張プロファイル取得（新しい属性を含む）"""
    try:
        # アカウント情報を取得（ローマ字名含む）
        account_result = db.exec(text("SELECT email, first_name_romaji, last_name_romaji FROM accounts WHERE id = :user_id").params(user_id=user_id)).first()
        
        # 基本プロフィール情報を取得（現地言語名含む）
        profile_result = db.exec(text("SELECT first_name, last_name, phone_number, address FROM user_profiles WHERE account_id = :user_id").params(user_id=user_id)).first()
        
        # 健康情報を取得
        health_result = db.exec(text("SELECT * FROM user_profiles_healthcondition WHERE user_id = :user_id").params(user_id=user_id)).first()
        
        if health_result:
            # 結果の長さを確認して安全にアクセス
            data = {
                "id": health_result[0],
                "user_id": health_result[1],
                # アカウント情報（ローマ字名含む）
                "email": account_result[0] if account_result else None,
                "first_name_romaji": account_result[1] if account_result else None,
                "last_name_romaji": account_result[2] if account_result else None,
                # 基本プロフィール情報（現地言語名含む）
                "first_name": profile_result[0] if profile_result else None,
                "last_name": profile_result[1] if profile_result else None,
                "phone_number": profile_result[2] if profile_result else None,
                "address": profile_result[3] if profile_result else None,
                # 健康情報
                "birth_date": health_result[2],
                "gender": health_result[3],
                "blood_type": health_result[4],
                "region": health_result[5],
                "created_at": health_result[18],
                "updated_at": health_result[19]
            }
            
            # 健康管理関連属性（インデックス6-9）
            if len(health_result) > 6:
                data["height_cm"] = health_result[6]
            if len(health_result) > 7:
                data["target_weight_kg"] = health_result[7]
            if len(health_result) > 8:
                data["target_body_fat_percentage"] = health_result[8]
            if len(health_result) > 9:
                data["activity_level"] = health_result[9]
            
            # 医療情報（インデックス10-12）
            if len(health_result) > 10:
                data["medical_conditions"] = health_result[10]
            if len(health_result) > 11:
                data["medications"] = health_result[11]
            if len(health_result) > 12:
                data["allergies"] = health_result[12]
            
            # 緊急連絡先・医療関係者情報（インデックス13-17）
            if len(health_result) > 13:
                data["emergency_contact_name"] = health_result[13]
            if len(health_result) > 14:
                data["emergency_contact_phone"] = health_result[14]
            if len(health_result) > 15:
                data["doctor_name"] = health_result[15]
            if len(health_result) > 16:
                data["doctor_phone"] = health_result[16]
            if len(health_result) > 17:
                data["insurance_number"] = health_result[17]
            
            return {
                "status": "success",
                "data": data
            }
        else:
            return {"status": "not_found", "message": "Extended profile not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/body-measurements/{user_id}")
async def get_body_measurements(user_id: int, db: Session = Depends(get_db)):
    """体重測定履歴取得"""
    try:
        result = db.exec(text("SELECT * FROM body_measurements WHERE user_id = :user_id ORDER BY measurement_date DESC").params(user_id=user_id)).all()
        measurements = []
        for row in result:
            measurements.append({
                "id": row[0],
                "user_id": row[1],
                "measurement_date": row[2],
                "weight_kg": row[3],
                "body_fat_percentage": row[4],
                "notes": row[5],
                "created_at": row[6],
                "updated_at": row[7]
            })
        return {"status": "success", "data": measurements}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/vital-signs/{user_id}")
async def get_vital_signs(user_id: int, db: Session = Depends(get_db)):
    """バイタルサイン履歴取得"""
    try:
        result = db.exec(text("SELECT * FROM vital_signs WHERE user_id = :user_id ORDER BY measurement_date DESC").params(user_id=user_id)).all()
        vitals = []
        for row in result:
            vitals.append({
                "id": row[0],
                "user_id": row[1],
                "measurement_date": row[2],
                "body_temperature": row[3],
                "systolic_bp": row[4],
                "diastolic_bp": row[5],
                "heart_rate": row[6],
                "notes": row[7],
                "created_at": row[8],
                "updated_at": row[9]
            })
        return {"status": "success", "data": vitals}
    except Exception as e:
        return {"status": "error", "message": str(e)}

from pydantic import BaseModel
from typing import Optional

class BodyMeasurementCreate(BaseModel):
    measurement_date: str
    weight_kg: float = None
    body_fat_percentage: float = None
    notes: str = None

class ProfileUpdate(BaseModel):
    # アカウント情報（ローマ字名）
    first_name_romaji: Optional[str] = None
    last_name_romaji: Optional[str] = None
    
    # 基本プロフィール情報（現地言語名）
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    
    # 基本属性
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    blood_type: Optional[str] = None
    region: Optional[str] = None
    
    # 健康管理関連属性
    height_cm: Optional[float] = None
    target_weight_kg: Optional[float] = None
    target_body_fat_percentage: Optional[float] = None
    activity_level: Optional[str] = None
    
    # 医療情報
    medical_conditions: Optional[str] = None
    medications: Optional[str] = None
    allergies: Optional[str] = None
    
    # 緊急連絡先・医療関係者情報
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    doctor_name: Optional[str] = None
    doctor_phone: Optional[str] = None
    insurance_number: Optional[str] = None

@app.post("/body-measurements/{user_id}")
@app.options("/body-measurements/{user_id}")
async def create_body_measurement(
    user_id: int,
    measurement_data: BodyMeasurementCreate = None,
    db: Session = Depends(get_db)
):
    """体重測定記録作成"""
    try:
        # OPTIONSリクエストの処理
        if measurement_data is None:
            return {"status": "success", "message": "CORS preflight"}
        
        # データの検証
        if not measurement_data.measurement_date:
            return {"status": "error", "message": "測定日時は必須です"}
        
        # 日時の形式を検証・変換（UTC変換）
        try:
            from datetime import datetime, timezone
            parsed_date = None
            
            # 複数の日時形式に対応
            if 'T' in measurement_data.measurement_date:
                # ISO形式の場合（ローカル時間として解釈）
                date_str = measurement_data.measurement_date.replace('Z', '')
                # 秒がない場合は追加
                if date_str.count(':') == 1:
                    date_str += ':00'
                parsed_date = datetime.fromisoformat(date_str)
                # ローカル時間をUTCに変換
                if parsed_date.tzinfo is None:
                    parsed_date = parsed_date.replace(tzinfo=timezone.utc)
            elif '+' in measurement_data.measurement_date:
                # タイムゾーン付きISO形式の場合
                parsed_date = datetime.fromisoformat(measurement_data.measurement_date)
            else:
                # 標準的な形式の場合（ローカル時間として解釈）
                try:
                    parsed_date = datetime.strptime(measurement_data.measurement_date, '%Y-%m-%d %H:%M:%S')
                    # ローカル時間をUTCに変換
                    parsed_date = parsed_date.replace(tzinfo=timezone.utc)
                except ValueError:
                    # その他の形式を試す
                    parsed_date = datetime.fromisoformat(measurement_data.measurement_date)
            
            # 標準形式で保存（YYYY-MM-DD HH:MM:SS）
            formatted_date = parsed_date.strftime('%Y-%m-%d %H:%M:%S')
            
        except ValueError as e:
            return {"status": "error", "message": f"日時の形式が正しくありません: {measurement_data.measurement_date}, エラー: {str(e)}"}
        
        result = db.exec(text("""
            INSERT INTO body_measurements (user_id, measurement_date, weight_kg, body_fat_percentage, notes)
            VALUES (:user_id, :measurement_date, :weight_kg, :body_fat_percentage, :notes)
        """).params(
            user_id=user_id,
            measurement_date=formatted_date,
            weight_kg=measurement_data.weight_kg,
            body_fat_percentage=measurement_data.body_fat_percentage,
            notes=measurement_data.notes
        ))
        db.commit()
        return {"status": "success", "message": "Body measurement created"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": f"データベースエラー: {str(e)}"}

class VitalSignCreate(BaseModel):
    measurement_date: str
    body_temperature: float = None
    systolic_bp: int = None
    diastolic_bp: int = None
    heart_rate: int = None
    notes: str = None

@app.post("/vital-signs/{user_id}")
@app.options("/vital-signs/{user_id}")
async def create_vital_sign(
    user_id: int,
    vital_data: VitalSignCreate = None,
    db: Session = Depends(get_db)
):
    """バイタルサイン記録作成"""
    try:
        # OPTIONSリクエストの処理
        if vital_data is None:
            return {"status": "success", "message": "CORS preflight"}
        
        # データの検証
        if not vital_data.measurement_date:
            return {"status": "error", "message": "測定日時は必須です"}
        
        # 日時の形式を検証・変換（UTC変換）
        try:
            from datetime import datetime, timezone
            parsed_date = None
            
            # 複数の日時形式に対応
            if 'T' in vital_data.measurement_date:
                # ISO形式の場合（ローカル時間として解釈）
                date_str = vital_data.measurement_date.replace('Z', '')
                # 秒がない場合は追加
                if date_str.count(':') == 1:
                    date_str += ':00'
                parsed_date = datetime.fromisoformat(date_str)
                # ローカル時間をUTCに変換
                if parsed_date.tzinfo is None:
                    parsed_date = parsed_date.replace(tzinfo=timezone.utc)
            elif '+' in vital_data.measurement_date:
                # タイムゾーン付きISO形式の場合
                parsed_date = datetime.fromisoformat(vital_data.measurement_date)
            else:
                # 標準的な形式の場合（ローカル時間として解釈）
                try:
                    parsed_date = datetime.strptime(vital_data.measurement_date, '%Y-%m-%d %H:%M:%S')
                    # ローカル時間をUTCに変換
                    parsed_date = parsed_date.replace(tzinfo=timezone.utc)
                except ValueError:
                    # その他の形式を試す
                    parsed_date = datetime.fromisoformat(vital_data.measurement_date)
            
            # 標準形式で保存（YYYY-MM-DD HH:MM:SS）
            formatted_date = parsed_date.strftime('%Y-%m-%d %H:%M:%S')
            
        except ValueError as e:
            return {"status": "error", "message": f"日時の形式が正しくありません: {vital_data.measurement_date}, エラー: {str(e)}"}
        
        result = db.exec(text("""
            INSERT INTO vital_signs (user_id, measurement_date, body_temperature, systolic_bp, diastolic_bp, heart_rate, notes)
            VALUES (:user_id, :measurement_date, :body_temperature, :systolic_bp, :diastolic_bp, :heart_rate, :notes)
        """).params(
            user_id=user_id,
            measurement_date=formatted_date,
            body_temperature=vital_data.body_temperature,
            systolic_bp=vital_data.systolic_bp,
            diastolic_bp=vital_data.diastolic_bp,
            heart_rate=vital_data.heart_rate,
            notes=vital_data.notes
        ))
        db.commit()
        return {"status": "success", "message": "Vital sign created"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": f"データベースエラー: {str(e)}"}

@app.put("/extended/{user_id}")
@app.options("/extended/{user_id}")
async def update_extended_profile(
    user_id: int,
    profile_data: ProfileUpdate = None,
    db: Session = Depends(get_db)
):
    """拡張プロファイル更新"""
    try:
        # OPTIONSリクエストの処理
        if profile_data is None:
            return {"status": "success", "message": "CORS preflight"}
        
        # データバリデーション
        validation_errors = validate_profile_data(profile_data.model_dump())
        if validation_errors:
            return {
                "status": "validation_error",
                "message": "入力データにエラーがあります",
                "errors": format_validation_errors(validation_errors)
            }
        
        # 既存のプロファイルを確認
        existing = db.exec(text("SELECT id FROM user_profiles_healthcondition WHERE user_id = :user_id").params(user_id=user_id)).first()
        
        if not existing:
            return {"status": "not_found", "message": "Extended profile not found"}
        
        # 更新するフィールドを動的に構築
        update_fields = []
        params = {"user_id": user_id}
        
        # アカウント情報の更新（accountsテーブル - ローマ字名）
        account_update_fields = []
        account_params = {"user_id": user_id}
        
        if hasattr(profile_data, 'first_name_romaji') and profile_data.first_name_romaji is not None:
            account_update_fields.append("first_name_romaji = :first_name_romaji")
            account_params["first_name_romaji"] = profile_data.first_name_romaji
        if hasattr(profile_data, 'last_name_romaji') and profile_data.last_name_romaji is not None:
            account_update_fields.append("last_name_romaji = :last_name_romaji")
            account_params["last_name_romaji"] = profile_data.last_name_romaji
        
        # アカウント情報を更新
        if account_update_fields:
            account_update_sql = f"UPDATE accounts SET {', '.join(account_update_fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = :user_id"
            db.exec(text(account_update_sql).params(**account_params))
        
        # 基本プロフィール情報の更新（user_profilesテーブル - 現地言語名）
        profile_update_fields = []
        profile_params = {"user_id": user_id}
        
        if hasattr(profile_data, 'first_name') and profile_data.first_name is not None:
            profile_update_fields.append("first_name = :first_name")
            profile_params["first_name"] = profile_data.first_name
        if hasattr(profile_data, 'last_name') and profile_data.last_name is not None:
            profile_update_fields.append("last_name = :last_name")
            profile_params["last_name"] = profile_data.last_name
        if hasattr(profile_data, 'phone_number') and profile_data.phone_number is not None:
            profile_update_fields.append("phone_number = :phone_number")
            profile_params["phone_number"] = profile_data.phone_number
        if hasattr(profile_data, 'address') and profile_data.address is not None:
            profile_update_fields.append("address = :address")
            profile_params["address"] = profile_data.address
        
        # 基本プロフィール情報を更新
        if profile_update_fields:
            profile_update_sql = f"UPDATE user_profiles SET {', '.join(profile_update_fields)}, updated_at = CURRENT_TIMESTAMP WHERE account_id = :user_id"
            db.exec(text(profile_update_sql).params(**profile_params))
        
        # 健康情報の更新（user_profiles_healthconditionテーブル）
        # 基本属性
        if profile_data.birth_date is not None:
            update_fields.append("birth_date = :birth_date")
            params["birth_date"] = profile_data.birth_date
        if profile_data.gender is not None:
            update_fields.append("gender = :gender")
            params["gender"] = profile_data.gender
        if profile_data.blood_type is not None:
            update_fields.append("blood_type = :blood_type")
            params["blood_type"] = profile_data.blood_type
        if profile_data.region is not None:
            update_fields.append("region = :region")
            params["region"] = profile_data.region
        
        # 健康管理関連属性
        if profile_data.height_cm is not None:
            update_fields.append("height_cm = :height_cm")
            params["height_cm"] = profile_data.height_cm
        if profile_data.target_weight_kg is not None:
            update_fields.append("target_weight_kg = :target_weight_kg")
            params["target_weight_kg"] = profile_data.target_weight_kg
        if profile_data.target_body_fat_percentage is not None:
            update_fields.append("target_body_fat_percentage = :target_body_fat_percentage")
            params["target_body_fat_percentage"] = profile_data.target_body_fat_percentage
        if profile_data.activity_level is not None:
            update_fields.append("activity_level = :activity_level")
            params["activity_level"] = profile_data.activity_level
        
        # 医療情報
        if profile_data.medical_conditions is not None:
            update_fields.append("medical_conditions = :medical_conditions")
            params["medical_conditions"] = profile_data.medical_conditions
        if profile_data.medications is not None:
            update_fields.append("medications = :medications")
            params["medications"] = profile_data.medications
        if profile_data.allergies is not None:
            update_fields.append("allergies = :allergies")
            params["allergies"] = profile_data.allergies
        
        # 緊急連絡先・医療関係者情報
        if profile_data.emergency_contact_name is not None:
            update_fields.append("emergency_contact_name = :emergency_contact_name")
            params["emergency_contact_name"] = profile_data.emergency_contact_name
        if profile_data.emergency_contact_phone is not None:
            update_fields.append("emergency_contact_phone = :emergency_contact_phone")
            params["emergency_contact_phone"] = profile_data.emergency_contact_phone
        if profile_data.doctor_name is not None:
            update_fields.append("doctor_name = :doctor_name")
            params["doctor_name"] = profile_data.doctor_name
        if profile_data.doctor_phone is not None:
            update_fields.append("doctor_phone = :doctor_phone")
            params["doctor_phone"] = profile_data.doctor_phone
        if profile_data.insurance_number is not None:
            update_fields.append("insurance_number = :insurance_number")
            params["insurance_number"] = profile_data.insurance_number
        
        if not update_fields:
            return {"status": "error", "message": "No fields to update"}
        
        # updated_atを追加
        update_fields.append("updated_at = :updated_at")
        params["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        
        # SQLクエリを実行
        query = f"UPDATE user_profiles_healthcondition SET {', '.join(update_fields)} WHERE user_id = :user_id"
        db.exec(text(query).params(**params))
        db.commit()
        
        return {"status": "success", "message": "Profile updated successfully"}
        
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": f"データベースエラー: {str(e)}"}

@app.get("/health/calculations/{user_id}")
async def get_health_calculations(user_id: int, db: Session = Depends(get_db)):
    """健康計算結果の取得"""
    try:
        # プロファイル情報を取得
        profile_result = db.exec(text("SELECT * FROM user_profiles_healthcondition WHERE user_id = :user_id").params(user_id=user_id)).first()
        if not profile_result:
            return {"status": "not_found", "message": "Profile not found"}
        
        # 最新の体重測定を取得
        latest_weight_result = db.exec(text("""
            SELECT weight_kg, body_fat_percentage, measurement_date 
            FROM body_measurements 
            WHERE user_id = :user_id 
            ORDER BY measurement_date DESC 
            LIMIT 1
        """).params(user_id=user_id)).first()
        
        # プロファイルデータの抽出
        profile_data = {
            "height_cm": profile_result[8] if len(profile_result) > 8 else None,
            "target_weight_kg": profile_result[9] if len(profile_result) > 9 else None,
            "target_body_fat_percentage": profile_result[10] if len(profile_result) > 10 else None,
            "activity_level": profile_result[11] if len(profile_result) > 11 else None,
            "birth_date": profile_result[2],
            "gender": profile_result[3]
        }
        
        # 現在の体重データ
        current_weight = latest_weight_result[0] if latest_weight_result else None
        current_body_fat = latest_weight_result[1] if latest_weight_result else None
        
        # 年齢の計算
        age = 0
        if profile_data["birth_date"]:
            age = calculate_age_from_birth_date(profile_data["birth_date"])
        
        calculations = {}
        
        # BMI計算
        if current_weight and profile_data["height_cm"]:
            try:
                bmi_result = calculate_bmi(current_weight, profile_data["height_cm"])
                calculations["current_bmi"] = {
                    "bmi": bmi_result.bmi,
                    "category": bmi_result.category,
                    "description": bmi_result.description
                }
            except ValueError as e:
                calculations["current_bmi"] = {"error": str(e)}
        
        # 目標BMI計算
        if profile_data["target_weight_kg"] and profile_data["height_cm"]:
            try:
                target_bmi_result = calculate_bmi(profile_data["target_weight_kg"], profile_data["height_cm"])
                calculations["target_bmi"] = {
                    "bmi": target_bmi_result.bmi,
                    "category": target_bmi_result.category,
                    "description": target_bmi_result.description
                }
            except ValueError as e:
                calculations["target_bmi"] = {"error": str(e)}
        
        # 健康進捗計算
        if current_weight and profile_data["target_weight_kg"] and profile_data["height_cm"]:
            progress = calculate_health_progress(
                current_weight=current_weight,
                target_weight=profile_data["target_weight_kg"],
                height_cm=profile_data["height_cm"],
                current_body_fat=current_body_fat,
                target_body_fat=profile_data["target_body_fat_percentage"]
            )
            
            calculations["progress"] = {
                "current_weight": progress.current_weight,
                "target_weight": progress.target_weight,
                "weight_difference": progress.weight_difference,
                "progress_percentage": progress.progress_percentage,
                "bmi_current": {
                    "bmi": progress.bmi_current.bmi,
                    "category": progress.bmi_current.category
                } if progress.bmi_current else None,
                "bmi_target": {
                    "bmi": progress.bmi_target.bmi,
                    "category": progress.bmi_target.category
                } if progress.bmi_target else None
            }
        
        # 必要カロリー計算
        if current_weight and profile_data["height_cm"] and age > 0 and profile_data["gender"] and profile_data["activity_level"]:
            try:
                calories_info = get_activity_level_calories(
                    current_weight, profile_data["height_cm"], age, 
                    profile_data["gender"], profile_data["activity_level"]
                )
                calculations["calories"] = calories_info
            except Exception as e:
                calculations["calories"] = {"error": str(e)}
        
        # 減量計画計算
        if (current_weight and profile_data["target_weight_kg"] and 
            profile_data["height_cm"] and age > 0 and profile_data["gender"] and profile_data["activity_level"]):
            try:
                weight_plan = calculate_weight_loss_plan(
                    current_weight=current_weight,
                    target_weight=profile_data["target_weight_kg"],
                    height_cm=profile_data["height_cm"],
                    age=age,
                    gender=profile_data["gender"],
                    activity_level=profile_data["activity_level"]
                )
                calculations["weight_plan"] = weight_plan
            except Exception as e:
                calculations["weight_plan"] = {"error": str(e)}
        
        return {
            "status": "success",
            "data": {
                "user_id": user_id,
                "profile": profile_data,
                "current_measurements": {
                    "weight_kg": current_weight,
                    "body_fat_percentage": current_body_fat,
                    "measurement_date": latest_weight_result[2] if latest_weight_result else None
                },
                "calculations": calculations
            }
        }
        
    except Exception as e:
        return {"status": "error", "message": f"計算エラー: {str(e)}"}

@app.get("/health/summary/{user_id}")
async def get_health_summary(user_id: int, db: Session = Depends(get_db)):
    """健康サマリーの取得"""
    try:
        # 健康計算結果を取得
        calculations_response = await get_health_calculations(user_id, db)
        if calculations_response["status"] != "success":
            return calculations_response
        
        calculations_data = calculations_response["data"]
        
        # サマリー情報の構築
        summary = {
            "user_id": user_id,
            "current_status": {},
            "goals": {},
            "recommendations": []
        }
        
        # 現在の状態
        if "current_bmi" in calculations_data["calculations"]:
            current_bmi = calculations_data["calculations"]["current_bmi"]
            summary["current_status"]["bmi"] = current_bmi
        
        if calculations_data["current_measurements"]["weight_kg"]:
            summary["current_status"]["weight"] = calculations_data["current_measurements"]["weight_kg"]
        
        # 目標
        if "target_bmi" in calculations_data["calculations"]:
            target_bmi = calculations_data["calculations"]["target_bmi"]
            summary["goals"]["bmi"] = target_bmi
        
        if calculations_data["profile"]["target_weight_kg"]:
            summary["goals"]["weight"] = calculations_data["profile"]["target_weight_kg"]
        
        # 進捗
        if "progress" in calculations_data["calculations"]:
            progress = calculations_data["calculations"]["progress"]
            summary["progress"] = {
                "weight_difference": progress["weight_difference"],
                "progress_percentage": progress["progress_percentage"]
            }
        
        # 推奨事項
        if "weight_plan" in calculations_data["calculations"]:
            weight_plan = calculations_data["calculations"]["weight_plan"]
            if "recommendations" in weight_plan:
                summary["recommendations"].extend(weight_plan["recommendations"])
        
        return {
            "status": "success",
            "data": summary
        }
        
    except Exception as e:
        return {"status": "error", "message": f"サマリー取得エラー: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
