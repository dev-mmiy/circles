"""
新しいデータベース構造に対応したユーザープロファイルAPI
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, create_engine
from sqlalchemy import text
import os
from typing import Dict, Any
from datetime import datetime

# データベース設定
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(DATABASE_URL, echo=True)

def get_db() -> Session:
    """データベースセッション取得"""
    with Session(engine) as session:
        yield session

app = FastAPI(title="Updated User Profile API", version="1.0.0")

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
    return {"message": "Updated User Profile API", "version": "1.0.0"}

@app.get("/extended/{user_id}")
async def get_extended_profile(user_id: int, db: Session = Depends(get_db)):
    """拡張プロファイル取得（新しいデータベース構造対応）"""
    try:
        # ユーザー基本情報を取得
        user_result = db.exec(text("""
            SELECT id, email, first_name_romaji, last_name_romaji, 
                   first_name_local, last_name_local, phone_number, address, nickname
            FROM users WHERE id = :user_id
        """).params(user_id=user_id)).first()
        
        if not user_result:
            raise HTTPException(status_code=404, detail="User not found")
        
        # ヘルスプロファイル情報を取得
        health_result = db.exec(text("""
            SELECT height_cm, current_weight_kg, target_weight_kg, 
                   target_body_fat_percentage, activity_level, birth_date, 
                   gender, blood_type, region, medical_conditions, 
                   medications, allergies, emergency_contact_name, 
                   emergency_contact_phone, doctor_name, doctor_phone, 
                   insurance_number
            FROM user_health_profiles WHERE user_id = :user_id
        """).params(user_id=user_id)).first()
        
        # レスポンスデータを構築
        data = {
            "id": user_result[0],
            "user_id": user_result[0],
            "email": user_result[1],
            "first_name_romaji": user_result[2],
            "last_name_romaji": user_result[3],
            "first_name": user_result[4],
            "last_name": user_result[5],
            "phone_number": user_result[6],
            "address": user_result[7],
            "nickname": user_result[8],
        }
        
        # ヘルスプロファイル情報を追加
        if health_result:
            data.update({
                "height_cm": health_result[0],
                "current_weight_kg": health_result[1],
                "target_weight_kg": health_result[2],
                "target_body_fat_percentage": health_result[3],
                "activity_level": health_result[4],
                "birth_date": health_result[5],
                "gender": health_result[6],
                "blood_type": health_result[7],
                "region": health_result[8],
                "medical_conditions": health_result[9],
                "medications": health_result[10],
                "allergies": health_result[11],
                "emergency_contact_name": health_result[12],
                "emergency_contact_phone": health_result[13],
                "doctor_name": health_result[14],
                "doctor_phone": health_result[15],
                "insurance_number": health_result[16],
            })
        
        return {
            "status": "success",
            "data": data
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.put("/extended/{user_id}")
async def update_extended_profile(user_id: int, profile_data: Dict[str, Any], db: Session = Depends(get_db)):
    """拡張プロファイル更新（新しいデータベース構造対応）"""
    try:
        # ユーザー基本情報の更新
        if any(key in profile_data for key in ['first_name', 'last_name', 'phone_number', 'address', 'nickname']):
            update_fields = []
            params = {"user_id": user_id}
            
            if 'first_name' in profile_data:
                update_fields.append("first_name_local = :first_name")
                params['first_name'] = profile_data['first_name']
            
            if 'last_name' in profile_data:
                update_fields.append("last_name_local = :last_name")
                params['last_name'] = profile_data['last_name']
            
            if 'phone_number' in profile_data:
                update_fields.append("phone_number = :phone_number")
                params['phone_number'] = profile_data['phone_number']
            
            if 'address' in profile_data:
                update_fields.append("address = :address")
                params['address'] = profile_data['address']
            
            if 'nickname' in profile_data:
                update_fields.append("nickname = :nickname")
                params['nickname'] = profile_data['nickname']
            
            if update_fields:
                update_fields.append("updated_at = CURRENT_TIMESTAMP")
                query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = :user_id"
                db.exec(text(query).params(**params))
        
        # ヘルスプロファイル情報の更新
        health_fields = [
            'height_cm', 'current_weight_kg', 'target_weight_kg', 
            'target_body_fat_percentage', 'activity_level', 'birth_date',
            'gender', 'blood_type', 'region', 'medical_conditions',
            'medications', 'allergies', 'emergency_contact_name',
            'emergency_contact_phone', 'doctor_name', 'doctor_phone',
            'insurance_number'
        ]
        
        health_update_fields = []
        health_params = {"user_id": user_id}
        
        for field in health_fields:
            if field in profile_data:
                health_update_fields.append(f"{field} = :{field}")
                health_params[field] = profile_data[field]
        
        if health_update_fields:
            health_update_fields.append("updated_at = CURRENT_TIMESTAMP")
            health_query = f"UPDATE user_health_profiles SET {', '.join(health_update_fields)} WHERE user_id = :user_id"
            db.exec(text(health_query).params(**health_params))
        
        db.commit()
        
        return {
            "status": "success",
            "message": "Profile updated successfully"
        }
        
    except Exception as e:
        db.rollback()
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/health/calculations/{user_id}")
async def get_health_calculations(user_id: int, db: Session = Depends(get_db)):
    """ヘルス計算（新しいデータベース構造対応）"""
    try:
        # ユーザー情報を取得
        user_result = db.exec(text("SELECT id, email FROM users WHERE id = :user_id").params(user_id=user_id)).first()
        
        if not user_result:
            raise HTTPException(status_code=404, detail="User not found")
        
        # ヘルスプロファイル情報を取得
        health_result = db.exec(text("""
            SELECT height_cm, activity_level FROM user_health_profiles WHERE user_id = :user_id
        """).params(user_id=user_id)).first()
        
        # 最新の測定データを取得
        measurement_result = db.exec(text("""
            SELECT weight_kg, body_fat_percentage 
            FROM body_measurements 
            WHERE user_id = :user_id 
            ORDER BY measurement_date DESC 
            LIMIT 1
        """).params(user_id=user_id)).first()
        
        calculations = {}
        
        # BMI計算
        if health_result and health_result[0] and measurement_result and measurement_result[0]:
            height_m = health_result[0] / 100
            weight = measurement_result[0]
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
        
        return {
            "status": "success",
            "user_id": user_id,
            "calculations": calculations,
            "profile_data": {
                "height_cm": health_result[0] if health_result else None,
                "current_weight_kg": measurement_result[0] if measurement_result else None,
                "activity_level": health_result[1] if health_result else None
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# ==================== 体重・体脂肪率管理 ====================

@app.get("/body-measurements/{user_id}")
async def get_body_measurements(user_id: int, db: Session = Depends(get_db)):
    """体重測定履歴取得"""
    try:
        result = db.exec(text("""
            SELECT id, user_id, measurement_date, weight_kg, body_fat_percentage, notes, created_at, updated_at
            FROM body_measurements WHERE user_id = :user_id ORDER BY measurement_date DESC
        """).params(user_id=user_id)).all()
        
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

@app.post("/body-measurements/{user_id}")
@app.options("/body-measurements/{user_id}")
async def create_body_measurement(
    user_id: int,
    measurement_data: Dict[str, Any] = None,
    db: Session = Depends(get_db)
):
    """体重測定記録作成"""
    try:
        # OPTIONSリクエストの処理
        if measurement_data is None:
            return {"status": "success", "message": "CORS preflight"}
        
        # データの検証
        if not measurement_data.get('measurement_date'):
            return {"status": "error", "message": "測定日時は必須です"}
        
        # 日時の形式を検証・変換（UTC変換）
        try:
            from datetime import datetime, timezone
            parsed_date = None
            
            # 複数の日時形式に対応
            if 'T' in measurement_data['measurement_date']:
                # ISO形式の場合（ローカル時間として解釈）
                date_str = measurement_data['measurement_date'].replace('Z', '')
                # 秒がない場合は追加
                if date_str.count(':') == 1:
                    date_str += ':00'
                parsed_date = datetime.fromisoformat(date_str)
                # ローカル時間をUTCに変換
                if parsed_date.tzinfo is None:
                    parsed_date = parsed_date.replace(tzinfo=timezone.utc)
            elif '+' in measurement_data['measurement_date']:
                # タイムゾーン付きISO形式の場合
                parsed_date = datetime.fromisoformat(measurement_data['measurement_date'])
            else:
                # 標準的な形式の場合（ローカル時間として解釈）
                try:
                    parsed_date = datetime.strptime(measurement_data['measurement_date'], '%Y-%m-%d %H:%M:%S')
                    # ローカル時間をUTCに変換
                    parsed_date = parsed_date.replace(tzinfo=timezone.utc)
                except ValueError:
                    # その他の形式を試す
                    parsed_date = datetime.fromisoformat(measurement_data['measurement_date'])
            
            # 標準形式で保存（YYYY-MM-DD HH:MM:SS）
            formatted_date = parsed_date.strftime('%Y-%m-%d %H:%M:%S')
            
        except ValueError as e:
            return {"status": "error", "message": f"日時の形式が正しくありません: {measurement_data['measurement_date']}, エラー: {str(e)}"}
        
        result = db.exec(text("""
            INSERT INTO body_measurements (user_id, measurement_date, weight_kg, body_fat_percentage, notes)
            VALUES (:user_id, :measurement_date, :weight_kg, :body_fat_percentage, :notes)
        """).params(
            user_id=user_id,
            measurement_date=formatted_date,
            weight_kg=measurement_data.get('weight_kg'),
            body_fat_percentage=measurement_data.get('body_fat_percentage'),
            notes=measurement_data.get('notes')
        ))
        db.commit()
        return {"status": "success", "message": "Body measurement created"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": f"データベースエラー: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
