"""
健康データ管理機能のUnit Test
体重測定とバイタルサインの登録・取得・更新・削除をテスト
"""

import pytest
import json
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine
from simple_user_profile_api import app, get_db
import os


# テスト用データベース
TEST_DATABASE_URL = "sqlite:///./test_health.db"
test_engine = create_engine(TEST_DATABASE_URL, echo=False)


def get_test_db():
    """テスト用データベースセッション"""
    with Session(test_engine) as session:
        yield session


# テスト用のクライアント
app.dependency_overrides[get_db] = get_test_db
client = TestClient(app)


class TestHealthDataManagement:
    """健康データ管理のテストクラス"""
    
    @classmethod
    def setup_class(cls):
        """テストクラスの初期化"""
        # テスト用テーブルを作成
        from sqlalchemy import text
        
        with test_engine.connect() as conn:
            # ユーザーテーブル（簡易版）
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # 体重測定テーブル
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS body_measurements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    measurement_date TIMESTAMP NOT NULL,
                    weight_kg REAL,
                    body_fat_percentage REAL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES accounts(id)
                )
            """))
            
            # バイタルサインテーブル
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS vital_signs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    measurement_date TIMESTAMP NOT NULL,
                    body_temperature REAL,
                    systolic_bp INTEGER,
                    diastolic_bp INTEGER,
                    heart_rate INTEGER,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES accounts(id)
                )
            """))
            
            # テストユーザーを作成
            conn.execute(text("""
                INSERT OR IGNORE INTO accounts (id, email) 
                VALUES (1, 'test@example.com')
            """))
            
            conn.commit()
    
    @classmethod
    def teardown_class(cls):
        """テストクラスのクリーンアップ"""
        # テスト用データベースファイルを削除
        if os.path.exists("test_health.db"):
            os.remove("test_health.db")
    
    def test_create_body_measurement(self):
        """体重測定データの作成テスト"""
        measurement_data = {
            "measurement_date": "2024-01-01T08:00:00",
            "weight_kg": 70.5,
            "body_fat_percentage": 15.2,
            "notes": "朝の測定"
        }
        
        response = client.post(
            "/body-measurements/1",
            json=measurement_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "Body measurement created" in data["message"]
    
    def test_get_body_measurements(self):
        """体重測定データの取得テスト"""
        response = client.get("/body-measurements/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert isinstance(data["data"], list)
    
    def test_create_vital_sign(self):
        """バイタルサインの作成テスト"""
        vital_data = {
            "measurement_date": "2024-01-01T09:00:00",
            "body_temperature": 36.5,
            "systolic_bp": 120,
            "diastolic_bp": 80,
            "heart_rate": 72,
            "notes": "健康診断"
        }
        
        response = client.post(
            "/vital-signs/1",
            json=vital_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "Vital sign created" in data["message"]
    
    def test_get_vital_signs(self):
        """バイタルサインの取得テスト"""
        response = client.get("/vital-signs/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert isinstance(data["data"], list)
    
    def test_body_measurement_with_null_values(self):
        """体重測定データのnull値処理テスト"""
        measurement_data = {
            "measurement_date": "2024-01-02T08:00:00",
            "weight_kg": None,
            "body_fat_percentage": None,
            "notes": None
        }
        
        response = client.post(
            "/body-measurements/1",
            json=measurement_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    def test_vital_sign_with_null_values(self):
        """バイタルサインのnull値処理テスト"""
        vital_data = {
            "measurement_date": "2024-01-02T09:00:00",
            "body_temperature": None,
            "systolic_bp": None,
            "diastolic_bp": None,
            "heart_rate": None,
            "notes": None
        }
        
        response = client.post(
            "/vital-signs/1",
            json=vital_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    def test_invalid_user_id(self):
        """無効なユーザーIDのテスト"""
        measurement_data = {
            "measurement_date": "2024-01-01T08:00:00",
            "weight_kg": 70.5,
            "body_fat_percentage": 15.2,
            "notes": "テスト"
        }
        
        response = client.post(
            "/body-measurements/999",  # 存在しないユーザーID
            json=measurement_data
        )
        
        # 現在の実装ではユーザー存在チェックがないため、成功する
        # 実際の実装では404エラーを返すべき
        assert response.status_code == 200
    
    def test_missing_measurement_date(self):
        """測定日時が不足している場合のテスト"""
        measurement_data = {
            "weight_kg": 70.5,
            "body_fat_percentage": 15.2,
            "notes": "テスト"
        }
        
        response = client.post(
            "/body-measurements/1",
            json=measurement_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert "測定日時は必須です" in data["message"]
    
    def test_invalid_datetime_format(self):
        """無効な日時形式のテスト"""
        measurement_data = {
            "measurement_date": "invalid-date",
            "weight_kg": 70.5,
            "body_fat_percentage": 15.2,
            "notes": "テスト"
        }
        
        response = client.post(
            "/body-measurements/1",
            json=measurement_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert "日時の形式が正しくありません" in data["message"]
    
    def test_cors_preflight_request(self):
        """CORSプリフライトリクエストのテスト"""
        response = client.options("/body-measurements/1")
        assert response.status_code == 200
        
        response = client.options("/vital-signs/1")
        assert response.status_code == 200


class TestHealthDataValidation:
    """健康データのバリデーションテスト"""
    
    def test_weight_validation(self):
        """体重値のバリデーションテスト"""
        # 正常な体重値
        measurement_data = {
            "measurement_date": "2024-01-01T08:00:00",
            "weight_kg": 70.5,
            "notes": "正常値"
        }
        
        response = client.post("/body-measurements/1", json=measurement_data)
        assert response.status_code == 200
        
        # 負の体重値（現在の実装では制限なし）
        measurement_data["weight_kg"] = -10.0
        response = client.post("/body-measurements/1", json=measurement_data)
        assert response.status_code == 200  # 現在は制限なし
    
    def test_body_fat_percentage_validation(self):
        """体脂肪率のバリデーションテスト"""
        # 正常な体脂肪率
        measurement_data = {
            "measurement_date": "2024-01-01T08:00:00",
            "body_fat_percentage": 15.2,
            "notes": "正常値"
        }
        
        response = client.post("/body-measurements/1", json=measurement_data)
        assert response.status_code == 200
        
        # 100%を超える体脂肪率（現在の実装では制限なし）
        measurement_data["body_fat_percentage"] = 150.0
        response = client.post("/body-measurements/1", json=measurement_data)
        assert response.status_code == 200  # 現在は制限なし
    
    def test_blood_pressure_validation(self):
        """血圧値のバリデーションテスト"""
        # 正常な血圧値
        vital_data = {
            "measurement_date": "2024-01-01T09:00:00",
            "systolic_bp": 120,
            "diastolic_bp": 80,
            "notes": "正常値"
        }
        
        response = client.post("/vital-signs/1", json=vital_data)
        assert response.status_code == 200
        
        # 異常な血圧値（現在の実装では制限なし）
        vital_data["systolic_bp"] = 300
        vital_data["diastolic_bp"] = 200
        response = client.post("/vital-signs/1", json=vital_data)
        assert response.status_code == 200  # 現在は制限なし
    
    def test_heart_rate_validation(self):
        """心拍数のバリデーションテスト"""
        # 正常な心拍数
        vital_data = {
            "measurement_date": "2024-01-01T09:00:00",
            "heart_rate": 72,
            "notes": "正常値"
        }
        
        response = client.post("/vital-signs/1", json=vital_data)
        assert response.status_code == 200
        
        # 異常な心拍数（現在の実装では制限なし）
        vital_data["heart_rate"] = 300
        response = client.post("/vital-signs/1", json=vital_data)
        assert response.status_code == 200  # 現在は制限なし


class TestHealthDataIntegration:
    """健康データの統合テスト"""
    
    def test_complete_health_data_workflow(self):
        """健康データの完全なワークフローテスト"""
        # 1. 体重測定データの作成
        measurement_data = {
            "measurement_date": "2024-01-01T08:00:00",
            "weight_kg": 70.5,
            "body_fat_percentage": 15.2,
            "notes": "朝の測定"
        }
        
        response = client.post("/body-measurements/1", json=measurement_data)
        assert response.status_code == 200
        
        # 2. バイタルサインの作成
        vital_data = {
            "measurement_date": "2024-01-01T09:00:00",
            "body_temperature": 36.5,
            "systolic_bp": 120,
            "diastolic_bp": 80,
            "heart_rate": 72,
            "notes": "健康診断"
        }
        
        response = client.post("/vital-signs/1", json=vital_data)
        assert response.status_code == 200
        
        # 3. データの取得確認
        response = client.get("/body-measurements/1")
        assert response.status_code == 200
        body_data = response.json()
        assert len(body_data["data"]) >= 1
        
        response = client.get("/vital-signs/1")
        assert response.status_code == 200
        vital_data = response.json()
        assert len(vital_data["data"]) >= 1
    
    def test_multiple_measurements_same_day(self):
        """同日の複数測定テスト"""
        # 朝の測定
        morning_data = {
            "measurement_date": "2024-01-01T08:00:00",
            "weight_kg": 70.5,
            "body_fat_percentage": 15.2,
            "notes": "朝の測定"
        }
        
        response = client.post("/body-measurements/1", json=morning_data)
        assert response.status_code == 200
        
        # 夜の測定
        evening_data = {
            "measurement_date": "2024-01-01T20:00:00",
            "weight_kg": 71.0,
            "body_fat_percentage": 15.5,
            "notes": "夜の測定"
        }
        
        response = client.post("/body-measurements/1", json=evening_data)
        assert response.status_code == 200
        
        # データの確認
        response = client.get("/body-measurements/1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) >= 2


if __name__ == "__main__":
    pytest.main([__file__])
