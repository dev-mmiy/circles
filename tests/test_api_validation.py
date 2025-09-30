"""
APIバリデーション機能のテスト
"""

import pytest
import requests
import json

BASE_URL = "http://localhost:8003"

class TestAPIValidation:
    """APIバリデーション機能のテスト"""
    
    def test_valid_profile_update(self):
        """有効なプロファイル更新のテスト"""
        valid_data = {
            "height_cm": 170.0,
            "activity_level": "moderate",
            "emergency_contact_name": "田中太郎",
            "emergency_contact_phone": "090-1234-5678"
        }
        
        response = requests.put(
            f"{BASE_URL}/extended/1",
            headers={"Content-Type": "application/json"},
            data=json.dumps(valid_data)
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    def test_invalid_email_validation(self):
        """無効なメールアドレスのバリデーションテスト"""
        invalid_data = {
            "email": "invalid-email-format"
        }
        
        response = requests.put(
            f"{BASE_URL}/extended/1",
            headers={"Content-Type": "application/json"},
            data=json.dumps(invalid_data)
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "validation_error"
        assert "email" in data["errors"]
    
    def test_invalid_birth_date_validation(self):
        """無効な生年月日のバリデーションテスト"""
        invalid_data = {
            "birth_date": "2030-01-01"  # 未来の日付
        }
        
        response = requests.put(
            f"{BASE_URL}/extended/1",
            headers={"Content-Type": "application/json"},
            data=json.dumps(invalid_data)
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "validation_error"
        assert "birth_date" in data["errors"]
    
    def test_invalid_gender_validation(self):
        """無効な性別のバリデーションテスト"""
        invalid_data = {
            "gender": "invalid_gender"
        }
        
        response = requests.put(
            f"{BASE_URL}/extended/1",
            headers={"Content-Type": "application/json"},
            data=json.dumps(invalid_data)
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "validation_error"
        assert "gender" in data["errors"]
    
    def test_invalid_height_validation(self):
        """無効な身長のバリデーションテスト"""
        invalid_data = {
            "height_cm": 300.0  # 身長が高すぎる
        }
        
        response = requests.put(
            f"{BASE_URL}/extended/1",
            headers={"Content-Type": "application/json"},
            data=json.dumps(invalid_data)
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "validation_error"
        assert "height_cm" in data["errors"]
    
    def test_invalid_weight_validation(self):
        """無効な体重のバリデーションテスト"""
        invalid_data = {
            "target_weight_kg": 500.0  # 体重が重すぎる
        }
        
        response = requests.put(
            f"{BASE_URL}/extended/1",
            headers={"Content-Type": "application/json"},
            data=json.dumps(invalid_data)
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "validation_error"
        assert "target_weight_kg" in data["errors"]
    
    def test_invalid_phone_validation(self):
        """無効な電話番号のバリデーションテスト"""
        invalid_data = {
            "emergency_contact_phone": "invalid-phone-number"
        }
        
        response = requests.put(
            f"{BASE_URL}/extended/1",
            headers={"Content-Type": "application/json"},
            data=json.dumps(invalid_data)
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "validation_error"
        assert "emergency_contact_phone" in data["errors"]
    
    def test_invalid_insurance_number_validation(self):
        """無効な保険証番号のバリデーションテスト"""
        invalid_data = {
            "insurance_number": "123"  # 短すぎる
        }
        
        response = requests.put(
            f"{BASE_URL}/extended/1",
            headers={"Content-Type": "application/json"},
            data=json.dumps(invalid_data)
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "validation_error"
        assert "insurance_number" in data["errors"]
    
    def test_multiple_validation_errors(self):
        """複数のバリデーションエラーのテスト"""
        invalid_data = {
            "email": "invalid-email",
            "birth_date": "2030-01-01",
            "gender": "invalid",
            "height_cm": 300.0,
            "target_weight_kg": 500.0,
            "emergency_contact_phone": "invalid-phone",
            "insurance_number": "123"
        }
        
        response = requests.put(
            f"{BASE_URL}/extended/1",
            headers={"Content-Type": "application/json"},
            data=json.dumps(invalid_data)
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "validation_error"
        assert len(data["errors"]) > 5  # 複数のエラーが含まれる
    
    def test_empty_data_validation(self):
        """空のデータのバリデーションテスト"""
        empty_data = {}
        
        response = requests.put(
            f"{BASE_URL}/extended/1",
            headers={"Content-Type": "application/json"},
            data=json.dumps(empty_data)
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert "No fields to update" in data["message"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
