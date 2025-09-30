"""
プライバシー設定機能のテスト
"""

import requests
import pytest

BASE_URL = "http://localhost:8003"

class TestPrivacySettings:
    """プライバシー設定機能のテスト"""
    
    def test_get_privacy_settings(self):
        """プライバシー設定の取得テスト"""
        response = requests.get(f"{BASE_URL}/privacy/settings/1")
        assert response.status_code == 200
        
        data = response.json()
        assert "user_id" in data
        assert "settings" in data
        assert "summary" in data
        
        settings = data["settings"]
        assert "basic_info_level" in settings
        assert "health_data_level" in settings
        assert "medical_info_level" in settings
        assert "allow_data_sharing" in settings
        
        summary = data["summary"]
        assert "total_categories" in summary
        assert "public_categories" in summary
        assert "private_categories" in summary
    
    def test_get_privacy_settings_nonexistent_user(self):
        """存在しないユーザーのプライバシー設定取得テスト"""
        response = requests.get(f"{BASE_URL}/privacy/settings/9999")
        assert response.status_code == 200
        
        data = response.json()
        assert data["user_id"] == 9999
        assert "settings" in data
    
    def test_update_privacy_settings(self):
        """プライバシー設定の更新テスト"""
        update_data = {
            "basic_info_level": "friends_only",
            "birth_date_visible": True,
            "gender_visible": True,
            "health_data_level": "friends_only",
            "height_visible": True,
            "weight_visible": True,
            "allow_data_sharing": True,
            "share_with_friends": True
        }
        
        response = requests.put(f"{BASE_URL}/privacy/settings/1", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "プライバシー設定が更新されました" in data["message"]
        
        # 更新された設定を確認
        get_response = requests.get(f"{BASE_URL}/privacy/settings/1")
        assert get_response.status_code == 200
        
        updated_settings = get_response.json()["settings"]
        assert updated_settings["basic_info_level"] == "friends_only"
        assert updated_settings["birth_date_visible"] == True
        assert updated_settings["gender_visible"] == True
        assert updated_settings["health_data_level"] == "friends_only"
        assert updated_settings["height_visible"] == True
        assert updated_settings["weight_visible"] == True
        assert updated_settings["allow_data_sharing"] == True
        assert updated_settings["share_with_friends"] == True
    
    def test_reset_privacy_settings(self):
        """プライバシー設定のリセットテスト"""
        response = requests.post(f"{BASE_URL}/privacy/settings/1/reset")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "デフォルトにリセットされました" in data["message"]
        
        # リセットされた設定を確認
        get_response = requests.get(f"{BASE_URL}/privacy/settings/1")
        assert get_response.status_code == 200
        
        reset_settings = get_response.json()["settings"]
        assert reset_settings["basic_info_level"] == "private"
        assert reset_settings["birth_date_visible"] == False
        assert reset_settings["gender_visible"] == False
        assert reset_settings["health_data_level"] == "private"
        assert reset_settings["height_visible"] == False
        assert reset_settings["weight_visible"] == False
        assert reset_settings["allow_data_sharing"] == False
        assert reset_settings["share_with_friends"] == False
    
    def test_get_privacy_summary(self):
        """プライバシー設定の要約取得テスト"""
        response = requests.get(f"{BASE_URL}/privacy/settings/1/summary")
        assert response.status_code == 200
        
        data = response.json()
        assert "user_id" in data
        assert "has_settings" in data
        assert "categories" in data
        assert "data_sharing" in data
        assert "research" in data
        
        categories = data["categories"]
        assert "basic_info" in categories
        assert "health_data" in categories
        assert "medical_info" in categories
        assert "emergency_contact" in categories
        assert "body_measurements" in categories
        assert "vital_signs" in categories
        
        # 各カテゴリの構造を確認
        for category, settings in categories.items():
            assert "level" in settings
            if "visible_fields" in settings:
                assert isinstance(settings["visible_fields"], dict)
    
    def test_create_data_access_request(self):
        """データアクセス要求の作成テスト"""
        request_data = {
            "target_user_id": 2,
            "requested_data_categories": ["health_data", "body_measurements"],
            "request_reason": "健康データの共有をお願いします。一緒に運動をしているので、進捗を共有したいです。"
        }
        
        response = requests.post(f"{BASE_URL}/privacy/data-access-request?requester_user_id=1", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "データアクセス要求が作成されました" in data["message"]
        assert "request_id" in data
    
    def test_create_data_access_request_self(self):
        """自分自身へのデータアクセス要求テスト（エラー）"""
        request_data = {
            "target_user_id": 1,
            "requested_data_categories": ["health_data"],
            "request_reason": "テスト"
        }
        
        response = requests.post(f"{BASE_URL}/privacy/data-access-request?requester_user_id=1", json=request_data)
        assert response.status_code == 400
        
        data = response.json()
        assert "自分自身へのデータアクセス要求はできません" in data["detail"]
    
    def test_get_data_access_requests(self):
        """データアクセス要求の一覧取得テスト"""
        response = requests.get(f"{BASE_URL}/privacy/data-access-requests/1")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        # 要求の構造を確認
        for request in data:
            assert "id" in request
            assert "type" in request
            assert "requester_user_id" in request
            assert "target_user_id" in request
            assert "requested_categories" in request
            assert "reason" in request
            assert "status" in request
            assert "created_at" in request
    
    def test_respond_to_data_access_request(self):
        """データアクセス要求への応答テスト"""
        # まず要求を作成
        request_data = {
            "target_user_id": 2,
            "requested_data_categories": ["basic_info"],
            "request_reason": "基本情報の共有をお願いします"
        }
        
        create_response = requests.post(f"{BASE_URL}/privacy/data-access-request?requester_user_id=1", json=request_data)
        assert create_response.status_code == 200
        request_id = create_response.json()["request_id"]
        
        # 要求に応答
        response_data = {
            "status": "approved",
            "response_message": "承認しました。"
        }
        
        response = requests.put(f"{BASE_URL}/privacy/data-access-request/{request_id}/respond", json=response_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "approvedされました" in data["message"]
    
    def test_respond_to_nonexistent_request(self):
        """存在しない要求への応答テスト（エラー）"""
        response_data = {
            "status": "approved",
            "response_message": "承認しました。"
        }
        
        response = requests.put(f"{BASE_URL}/privacy/data-access-request/9999/respond", json=response_data)
        assert response.status_code == 404
        
        data = response.json()
        assert "データアクセス要求が見つかりません" in data["detail"]
    
    def test_privacy_settings_partial_update(self):
        """プライバシー設定の部分更新テスト"""
        # 一部のフィールドのみ更新
        update_data = {
            "basic_info_level": "public",
            "allow_data_sharing": True
        }
        
        response = requests.put(f"{BASE_URL}/privacy/settings/1", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        
        # 更新された設定を確認
        get_response = requests.get(f"{BASE_URL}/privacy/settings/1")
        assert get_response.status_code == 200
        
        updated_settings = get_response.json()["settings"]
        assert updated_settings["basic_info_level"] == "public"
        assert updated_settings["allow_data_sharing"] == True
        # 他のフィールドは変更されていないことを確認
        assert updated_settings["health_data_level"] == "private"  # デフォルト値

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
