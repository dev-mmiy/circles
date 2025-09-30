"""
シンプルな統合API（デバッグ用）
"""

from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Session, create_engine, select
from sqlalchemy import text
import os
from datetime import datetime

# データベース設定
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(DATABASE_URL, echo=False)

def get_db():
    """データベースセッションの取得"""
    with Session(engine) as session:
        yield session

# FastAPIアプリケーション
app = FastAPI(title="シンプル統合API", version="1.0.0")

# ヘルスチェック
@app.get("/health")
async def health_check():
    """APIヘルスチェック"""
    return {"status": "healthy", "message": "シンプル統合API is running"}

# ユーザー一覧取得
@app.get("/users")
async def get_users(db: Session = Depends(get_db)):
    """ユーザー一覧の取得"""
    try:
        # 直接SQLクエリを実行
        result = db.exec(text("SELECT id, email, first_name_local, last_name_local FROM users ORDER BY id"))
        users = []
        for row in result:
            users.append({
                "id": row[0],
                "email": row[1],
                "name": f"{row[2] or ''} {row[3] or ''}".strip()
            })
        return {"status": "success", "users": users}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ユーザー詳細取得
@app.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """ユーザー詳細の取得"""
    try:
        # ユーザー情報の取得
        result = db.exec(text(f"SELECT id, email, first_name_local, last_name_local, phone_number, address FROM users WHERE id = {user_id}"))
        user_row = result.first()
        
        if not user_row:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = {
            "id": user_row[0],
            "email": user_row[1],
            "name": f"{user_row[2] or ''} {user_row[3] or ''}".strip(),
            "phone_number": user_row[4],
            "address": user_row[5]
        }
        
        # ヘルスプロファイルの取得
        health_result = db.exec(text(f"SELECT height_cm, current_weight_kg, activity_level FROM user_health_profiles WHERE user_id = {user_id}"))
        health_row = health_result.first()
        
        health_profile = None
        if health_row:
            health_profile = {
                "height_cm": health_row[0],
                "current_weight_kg": health_row[1],
                "activity_level": health_row[2]
            }
        
        return {
            "status": "success",
            "user": user,
            "health_profile": health_profile
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 体組成測定データの取得
@app.get("/users/{user_id}/measurements")
async def get_measurements(user_id: int, db: Session = Depends(get_db)):
    """体組成測定データの取得"""
    try:
        result = db.exec(text(f"""
            SELECT weight_kg, body_fat_percentage, measurement_date, notes 
            FROM body_measurements 
            WHERE user_id = {user_id} 
            ORDER BY measurement_date DESC 
            LIMIT 10
        """))
        
        measurements = []
        for row in result:
            measurements.append({
                "weight_kg": row[0],
                "body_fat_percentage": row[1],
                "measurement_date": row[2],
                "notes": row[3]
            })
        
        return {
            "status": "success",
            "user_id": user_id,
            "measurements": measurements
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ヘルス計算
@app.get("/users/{user_id}/health/calculations")
async def get_health_calculations(user_id: int, db: Session = Depends(get_db)):
    """ヘルス計算の実行"""
    try:
        # ユーザー情報の取得
        user_result = db.exec(text(f"SELECT id, email FROM users WHERE id = {user_id}"))
        user_row = user_result.first()
        
        if not user_row:
            raise HTTPException(status_code=404, detail="User not found")
        
        # ヘルスプロファイルの取得
        health_result = db.exec(text(f"SELECT height_cm, activity_level FROM user_health_profiles WHERE user_id = {user_id}"))
        health_row = health_result.first()
        
        # 最新の測定データの取得
        measurement_result = db.exec(text(f"""
            SELECT weight_kg, body_fat_percentage 
            FROM body_measurements 
            WHERE user_id = {user_id} 
            ORDER BY measurement_date DESC 
            LIMIT 1
        """))
        measurement_row = measurement_result.first()
        
        calculations = {}
        
        # BMI計算
        if health_row and health_row[0] and measurement_row and measurement_row[0]:
            height_m = health_row[0] / 100
            weight = measurement_row[0]
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
                "height_cm": health_row[0] if health_row else None,
                "current_weight_kg": measurement_row[0] if measurement_row else None,
                "activity_level": health_row[1] if health_row else None
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
