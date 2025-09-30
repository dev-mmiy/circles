"""
ユーザープロファイルAPIのテスト
"""

from fastapi import FastAPI, Depends
from sqlmodel import Session, create_engine, select
import os

# データベース設定
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(DATABASE_URL, echo=True)

def get_db() -> Session:
    """データベースセッション取得"""
    with Session(engine) as session:
        yield session

app = FastAPI()

@app.get("/test/extended/{user_id}")
async def test_get_extended_profile(user_id: int, db: Session = Depends(get_db)):
    """拡張プロファイル取得テスト"""
    try:
        # 直接SQLクエリを実行
        from sqlalchemy import text
        result = db.exec(text("SELECT * FROM user_profiles_extended WHERE user_id = :user_id").params(user_id=user_id)).first()
        if result:
            return {"status": "success", "data": result}
        else:
            return {"status": "not_found", "message": "Extended profile not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/test/body-measurements/{user_id}")
async def test_get_body_measurements(user_id: int, db: Session = Depends(get_db)):
    """体重測定履歴取得テスト"""
    try:
        # 直接SQLクエリを実行
        from sqlalchemy import text
        result = db.exec(text("SELECT * FROM body_measurements WHERE user_id = :user_id").params(user_id=user_id)).all()
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/test/vital-signs/{user_id}")
async def test_get_vital_signs(user_id: int, db: Session = Depends(get_db)):
    """バイタルサイン履歴取得テスト"""
    try:
        # 直接SQLクエリを実行
        from sqlalchemy import text
        result = db.exec(text("SELECT * FROM vital_signs WHERE user_id = :user_id").params(user_id=user_id)).all()
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
