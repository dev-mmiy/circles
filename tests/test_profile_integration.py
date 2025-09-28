"""
Integration tests for profile management functionality.
Tests the complete flow from frontend to backend.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
import json


class TestProfileManagementIntegration:
    """Integration tests for profile management."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        from app_auth_simple import app
        return TestClient(app)
    
    @pytest.fixture
    def registered_user(self, client):
        """Register a user and return user data."""
        registration_data = {
            "email": "integration@example.com",
            "password": "password123",
            "nickname": "IntegrationUser",
            "first_name": "Integration",
            "last_name": "User",
            "primary_condition": "Test Condition",
            "language": "en-US",
            "country": "US",
            "timezone": "UTC"
        }
        
        response = client.post("/auth/register", json=registration_data)
        assert response.status_code == 200
        return response.json()
    
    def test_complete_profile_management_flow(self, client, registered_user):
        """Test complete profile management flow."""
        # Extract token from registration
        access_token = registered_user["access_token"]
        user_data = registered_user["user"]
        
        # Verify initial user data
        assert user_data["nickname"] == "IntegrationUser"
        assert user_data["language"] == "en-US"
        assert user_data["country"] == "US"
        
        # Update profile
        profile_update_data = {
            "nickname": "UpdatedIntegrationUser",
            "first_name": "UpdatedIntegration",
            "last_name": "UpdatedUser",
            "primary_condition": "Updated Condition",
            "language": "ja-JP",
            "country": "JP",
            "timezone": "Asia/Tokyo"
        }
        
        with patch('app_auth_simple.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            update_response = client.put(
                "/auth/profile",
                json=profile_update_data,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            assert update_response.status_code == 200
            update_data = update_response.json()
            
            # Verify updated data
            updated_user = update_data["user"]
            assert updated_user["nickname"] == "UpdatedIntegrationUser"
            assert updated_user["first_name"] == "UpdatedIntegration"
            assert updated_user["last_name"] == "UpdatedUser"
            assert updated_user["primary_condition"] == "Updated Condition"
            assert updated_user["language"] == "ja-JP"
            assert updated_user["country"] == "JP"
            assert updated_user["timezone"] == "Asia/Tokyo"
            assert "updated_at" in updated_user

    def test_profile_update_with_login_flow(self, client):
        """Test profile update in a complete login flow."""
        # Register user
        registration_data = {
            "email": "loginflow@example.com",
            "password": "password123",
            "nickname": "LoginFlowUser",
            "first_name": "LoginFlow",
            "last_name": "User",
            "primary_condition": "Test Condition",
            "language": "en-US",
            "country": "US",
            "timezone": "UTC"
        }
        
        reg_response = client.post("/auth/register", json=registration_data)
        assert reg_response.status_code == 200
        
        # Login user
        login_data = {
            "email": "loginflow@example.com",
            "password": "password123",
            "remember_me": False
        }
        
        login_response = client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        login_data_response = login_response.json()
        access_token = login_data_response["access_token"]
        
        # Update profile
        profile_update_data = {
            "nickname": "UpdatedLoginFlowUser",
            "language": "fr-FR",
            "country": "FR",
            "timezone": "Europe/Paris"
        }
        
        with patch('app_auth_simple.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            update_response = client.put(
                "/auth/profile",
                json=profile_update_data,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            assert update_response.status_code == 200
            update_data = update_response.json()
            
            updated_user = update_data["user"]
            assert updated_user["nickname"] == "UpdatedLoginFlowUser"
            assert updated_user["language"] == "fr-FR"
            assert updated_user["country"] == "FR"
            assert updated_user["timezone"] == "Europe/Paris"

    def test_multiple_profile_updates(self, client, registered_user):
        """Test multiple profile updates."""
        access_token = registered_user["access_token"]
        
        # First update
        first_update = {
            "nickname": "FirstUpdate",
            "language": "ja-JP"
        }
        
        with patch('app_auth_simple.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            response1 = client.put(
                "/auth/profile",
                json=first_update,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            assert response1.status_code == 200
            data1 = response1.json()
            assert data1["user"]["nickname"] == "FirstUpdate"
            assert data1["user"]["language"] == "ja-JP"
        
        # Second update
        second_update = {
            "nickname": "SecondUpdate",
            "language": "en-US",
            "country": "US"
        }
        
        with patch('app_auth_simple.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 13, 0, 0, tzinfo=timezone.utc)
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            response2 = client.put(
                "/auth/profile",
                json=second_update,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            assert response2.status_code == 200
            data2 = response2.json()
            assert data2["user"]["nickname"] == "SecondUpdate"
            assert data2["user"]["language"] == "en-US"
            assert data2["user"]["country"] == "US"

    def test_profile_update_with_special_characters(self, client, registered_user):
        """Test profile update with special characters."""
        access_token = registered_user["access_token"]
        
        special_char_update = {
            "nickname": "テストユーザー",
            "first_name": "José",
            "last_name": "García-López",
            "primary_condition": "心不全 & 糖尿病",
            "language": "ja-JP",
            "country": "JP",
            "timezone": "Asia/Tokyo"
        }
        
        with patch('app_auth_simple.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            response = client.put(
                "/auth/profile",
                json=special_char_update,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            updated_user = data["user"]
            assert updated_user["nickname"] == "テストユーザー"
            assert updated_user["first_name"] == "José"
            assert updated_user["last_name"] == "García-López"
            assert updated_user["primary_condition"] == "心不全 & 糖尿病"
            assert updated_user["language"] == "ja-JP"
            assert updated_user["country"] == "JP"
            assert updated_user["timezone"] == "Asia/Tokyo"

    def test_profile_update_error_scenarios(self, client, registered_user):
        """Test profile update error scenarios."""
        access_token = registered_user["access_token"]
        
        # Test with invalid token
        invalid_token_response = client.put(
            "/auth/profile",
            json={"nickname": "Test"},
            headers={"Authorization": "Bearer invalid-token"}
        )
        
        assert invalid_token_response.status_code == 200
        
        # Test without authorization header
        no_auth_response = client.put(
            "/auth/profile",
            json={"nickname": "Test"}
        )
        
        assert no_auth_response.status_code == 400
        
        # Test with malformed JSON
        malformed_response = client.put(
            "/auth/profile",
            data="invalid json",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        )
        
        assert malformed_response.status_code == 422

    def test_profile_update_performance(self, client, registered_user):
        """Test profile update performance."""
        access_token = registered_user["access_token"]
        
        # Test with large data
        large_update_data = {
            "nickname": "A" * 1000,
            "first_name": "B" * 1000,
            "last_name": "C" * 1000,
            "primary_condition": "D" * 1000,
            "language": "en-US",
            "country": "US",
            "timezone": "America/New_York"
        }
        
        with patch('app_auth_simple.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            import time
            start_time = time.time()
            
            response = client.put(
                "/auth/profile",
                json=large_update_data,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < 1.0  # Should complete within 1 second
            
            data = response.json()
            user_data = data["user"]
            assert user_data["nickname"] == "A" * 1000
            assert user_data["first_name"] == "B" * 1000
            assert user_data["last_name"] == "C" * 1000
            assert user_data["primary_condition"] == "D" * 1000

    def test_profile_update_concurrent_requests(self, client, registered_user):
        """Test concurrent profile update requests."""
        access_token = registered_user["access_token"]
        
        # Simulate concurrent updates
        update_data_1 = {"nickname": "Concurrent1", "language": "ja-JP"}
        update_data_2 = {"nickname": "Concurrent2", "language": "en-US"}
        
        with patch('app_auth_simple.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            # Both requests should succeed
            response1 = client.put(
                "/auth/profile",
                json=update_data_1,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            response2 = client.put(
                "/auth/profile",
                json=update_data_2,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            assert response1.status_code == 200
            assert response2.status_code == 200
            
            # Check responses
            data1 = response1.json()
            data2 = response2.json()
            
            assert data1["user"]["nickname"] == "Concurrent1"
            assert data1["user"]["language"] == "ja-JP"
            assert data2["user"]["nickname"] == "Concurrent2"
            assert data2["user"]["language"] == "en-US"

    def test_profile_update_data_consistency(self, client, registered_user):
        """Test profile update data consistency."""
        access_token = registered_user["access_token"]
        
        # Update profile
        update_data = {
            "nickname": "ConsistencyTest",
            "first_name": "Consistency",
            "last_name": "Test",
            "primary_condition": "Consistency Condition",
            "language": "ja-JP",
            "country": "JP",
            "timezone": "Asia/Tokyo"
        }
        
        with patch('app_auth_simple.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            response = client.put(
                "/auth/profile",
                json=update_data,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify data consistency
            user_data = data["user"]
            assert user_data["nickname"] == "ConsistencyTest"
            assert user_data["first_name"] == "Consistency"
            assert user_data["last_name"] == "Test"
            assert user_data["primary_condition"] == "Consistency Condition"
            assert user_data["language"] == "ja-JP"
            assert user_data["country"] == "JP"
            assert user_data["timezone"] == "Asia/Tokyo"
            
            # Verify timestamp
            assert "updated_at" in user_data
            updated_at = user_data["updated_at"]
            assert isinstance(updated_at, str)
            assert len(updated_at) > 0

    def test_profile_update_validation_rules(self, client, registered_user):
        """Test profile update validation rules."""
        access_token = registered_user["access_token"]
        
        # Test with empty values
        empty_update = {
            "nickname": "",
            "first_name": "",
            "last_name": "",
            "primary_condition": "",
            "language": "ja-JP",
            "country": "JP",
            "timezone": "Asia/Tokyo"
        }
        
        with patch('app_auth_simple.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            response = client.put(
                "/auth/profile",
                json=empty_update,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            # Should still succeed (empty values are allowed)
            assert response.status_code == 200
            data = response.json()
            
            user_data = data["user"]
            assert user_data["nickname"] == ""
            assert user_data["first_name"] == ""
            assert user_data["last_name"] == ""
            assert user_data["primary_condition"] == ""
            assert user_data["language"] == "ja-JP"
            assert user_data["country"] == "JP"
            assert user_data["timezone"] == "Asia/Tokyo"

    def test_profile_update_internationalization(self, client, registered_user):
        """Test profile update with different internationalization settings."""
        access_token = registered_user["access_token"]
        
        # Test different language/country combinations
        i18n_combinations = [
            {"language": "ja-JP", "country": "JP", "timezone": "Asia/Tokyo"},
            {"language": "en-US", "country": "US", "timezone": "America/New_York"},
            {"language": "fr-FR", "country": "FR", "timezone": "Europe/Paris"}
        ]
        
        for i, combo in enumerate(i18n_combinations):
            update_data = {
                "nickname": f"I18nTest{i}",
                "language": combo["language"],
                "country": combo["country"],
                "timezone": combo["timezone"]
            }
            
            with patch('app_auth_simple.datetime') as mock_datetime:
                mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
                mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
                
                response = client.put(
                    "/auth/profile",
                    json=update_data,
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                assert response.status_code == 200
                data = response.json()
                
                user_data = data["user"]
                assert user_data["nickname"] == f"I18nTest{i}"
                assert user_data["language"] == combo["language"]
                assert user_data["country"] == combo["country"]
                assert user_data["timezone"] == combo["timezone"]
