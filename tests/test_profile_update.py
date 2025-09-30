"""
プロファイル更新APIのテスト
"""

import pytest
import requests
import json
from datetime import datetime, timezone

BASE_URL = "http://localhost:8003"

class TestProfileUpdate:
    """プロファイル更新のテスト"""
    
    def test_get_extended_profile(self):
        """拡張プロファイル取得テスト"""
        response = requests.get(f"{BASE_URL}/extended/1")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        
        profile = data["data"]
        # 基本属性の確認
        assert "birth_date" in profile
        assert "gender" in profile
        assert "blood_type" in profile
        assert "region" in profile
        
        # 健康管理関連属性の確認
        assert "height_cm" in profile
        assert "target_weight_kg" in profile
        assert "target_body_fat_percentage" in profile
        assert "activity_level" in profile
        
        # 医療情報の確認
        assert "medical_conditions" in profile
        assert "medications" in profile
        assert "allergies" in profile
        
        # 緊急連絡先・医療関係者情報の確認
        assert "emergency_contact_name" in profile
        assert "emergency_contact_phone" in profile
        assert "doctor_name" in profile
        assert "doctor_phone" in profile
        assert "insurance_number" in profile
    
    def test_update_basic_attributes(self):
        """基本属性の更新テスト"""
        update_data = {
            "birth_date": "1990-01-01",
            "gender": "male",
            "blood_type": "A",
            "region": "東京都"
        }
        
        response = requests.put(
            f"{BASE_URL}/extended/1",
            headers={"Content-Type": "application/json"},
            data=json.dumps(update_data)
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "Profile updated successfully" in data["message"]
    
    def test_update_health_attributes(self):
        """健康管理関連属性の更新テスト"""
        update_data = {
            "height_cm": 170.0,
            "target_weight_kg": 65.0,
            "target_body_fat_percentage": 18.0,
            "activity_level": "moderate"
        }
        
        response = requests.put(
            f"{BASE_URL}/extended/1",
            headers={"Content-Type": "application/json"},
            data=json.dumps(update_data)
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    def test_update_medical_info(self):
        """医療情報の更新テスト"""
        update_data = {
            "medical_conditions": "高血圧",
            "medications": "降圧剤",
            "allergies": "花粉症"
        }
        
        response = requests.put(
            f"{BASE_URL}/extended/1",
            headers={"Content-Type": "application/json"},
            data=json.dumps(update_data)
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    def test_update_emergency_contact(self):
        """緊急連絡先・医療関係者情報の更新テスト"""
        update_data = {
            "emergency_contact_name": "田中太郎",
            "emergency_contact_phone": "090-1234-5678",
            "doctor_name": "佐藤医師",
            "doctor_phone": "03-9876-5432",
            "insurance_number": "1234567890"
        }
        
        response = requests.put(
            f"{BASE_URL}/extended/1",
            headers={"Content-Type": "application/json"},
            data=json.dumps(update_data)
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    def test_update_partial_fields(self):
        """部分的なフィールド更新テスト"""
        update_data = {
            "height_cm": 175.0,
            "activity_level": "high"
        }
        
        response = requests.put(
            f"{BASE_URL}/extended/1",
            headers={"Content-Type": "application/json"},
            data=json.dumps(update_data)
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    def test_update_empty_data(self):
        """空のデータでの更新テスト"""
        update_data = {}
        
        response = requests.put(
            f"{BASE_URL}/extended/1",
            headers={"Content-Type": "application/json"},
            data=json.dumps(update_data)
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert "No fields to update" in data["message"]
    
    def test_update_nonexistent_user(self):
        """存在しないユーザーの更新テスト"""
        update_data = {
            "height_cm": 170.0
        }
        
        response = requests.put(
            f"{BASE_URL}/extended/999",
            headers={"Content-Type": "application/json"},
            data=json.dumps(update_data)
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "not_found"
        assert "Extended profile not found" in data["message"]
    
    def test_cors_preflight(self):
        """CORS preflightリクエストのテスト"""
        response = requests.options(f"{BASE_URL}/extended/1")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "CORS preflight" in data["message"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
