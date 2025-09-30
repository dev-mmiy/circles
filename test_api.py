"""
テスト用のシンプルなAPIサーバー
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, create_engine
from sqlalchemy import text
import os

# データベース設定
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(DATABASE_URL, echo=False)

def get_db() -> Session:
    """データベースセッション取得"""
    with Session(engine) as session:
        yield session

app = FastAPI(title="Test API", version="1.0.0")

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
    return {"message": "Test API is running", "version": "1.0.0"}

@app.get("/extended/{user_id}")
async def get_extended_profile(user_id: int, db: Session = Depends(get_db)):
    """拡張プロファイル取得"""
    try:
        # ユーザー情報を取得
        result = db.exec(text("""
            SELECT id, email, first_name_local, last_name_local, 
                   phone_number, address, height_cm, current_weight_kg,
                   activity_level, birth_date, gender, blood_type
            FROM users u
            LEFT JOIN user_health_profiles h ON u.id = h.user_id
            WHERE u.id = :user_id
        """).params(user_id=user_id)).first()
        
        if not result:
            return {"status": "error", "message": "User not found"}
        
        data = {
            "id": result[0],
            "email": result[1],
            "first_name": result[2],
            "last_name": result[3],
            "phone_number": result[4],
            "address": result[5],
            "height_cm": result[6],
            "current_weight_kg": result[7],
            "activity_level": result[8],
            "birth_date": result[9],
            "gender": result[10],
            "blood_type": result[11],
        }
        
        return {
            "status": "success",
            "data": data
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)

