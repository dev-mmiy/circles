"""
Unit tests for profile management functionality.
Tests the profile update API endpoints and related functionality.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
import json


class TestProfileManagement:
    """Test class for profile management functionality."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        from app_auth_simple import app
        return TestClient(app)
    
    @pytest.fixture
    def sample_user_data(self):
        """Sample user data for testing."""
        return {
            "id": 1,
            "email": "test@example.com",
            "nickname": "TestUser",
            "first_name": "Test",
            "last_name": "User",
            "primary_condition": "Test Condition",
            "language": "ja-JP",
            "country": "JP",
            "timezone": "Asia/Tokyo",
            "created_at": "2024-01-01T00:00:00Z"
        }
    
    @pytest.fixture
    def sample_profile_update_data(self):
        """Sample profile update data for testing."""
        return {
            "nickname": "UpdatedNickname",
            "first_name": "UpdatedFirst",
            "last_name": "UpdatedLast",
            "primary_condition": "Updated Condition",
            "language": "en-US",
            "country": "US",
            "timezone": "America/New_York"
        }
    
    @pytest.fixture
    def partial_profile_update_data(self):
        """Partial profile update data for testing."""
        return {
            "nickname": "PartialUpdate",
            "language": "fr-FR"
        }
    
    @pytest.fixture
    def invalid_profile_update_data(self):
        """Invalid profile update data for testing."""
        return {
            "email": "new@example.com",  # Email should not be updatable
            "invalid_field": "invalid_value"
        }

    def test_profile_update_success(self, client, sample_profile_update_data):
        """Test successful profile update."""
        with patch('app_auth_simple.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            response = client.put(
                "/auth/profile",
                json=sample_profile_update_data,
                headers={"Authorization": "Bearer test-token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert "message" in data
            assert data["message"] == "Profile updated successfully"
            assert "user" in data
            
            user_data = data["user"]
            assert user_data["nickname"] == "UpdatedNickname"
            assert user_data["first_name"] == "UpdatedFirst"
            assert user_data["last_name"] == "UpdatedLast"
            assert user_data["primary_condition"] == "Updated Condition"
            assert user_data["language"] == "en-US"
            assert user_data["country"] == "US"
            assert user_data["timezone"] == "America/New_York"
            assert "updated_at" in user_data

    def test_profile_update_partial(self, client, partial_profile_update_data):
        """Test partial profile update."""
        with patch('app_auth_simple.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            response = client.put(
                "/auth/profile",
                json=partial_profile_update_data,
                headers={"Authorization": "Bearer test-token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            user_data = data["user"]
            # Updated fields
            assert user_data["nickname"] == "PartialUpdate"
            assert user_data["language"] == "fr-FR"
            
            # Unchanged fields should remain default
            assert user_data["first_name"] == "Test"
            assert user_data["last_name"] == "User"
            assert user_data["primary_condition"] == "Test Condition"
            assert user_data["country"] == "US"
            assert user_data["timezone"] == "UTC"

    def test_profile_update_no_authorization(self, client, sample_profile_update_data):
        """Test profile update without authorization header."""
        response = client.put(
            "/auth/profile",
            json=sample_profile_update_data
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_profile_update_invalid_authorization(self, client, sample_profile_update_data):
        """Test profile update with invalid authorization header."""
        response = client.put(
            "/auth/profile",
            json=sample_profile_update_data,
            headers={"Authorization": "Invalid token"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_profile_update_empty_data(self, client):
        """Test profile update with empty data."""
        with patch('app_auth_simple.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            response = client.put(
                "/auth/profile",
                json={},
                headers={"Authorization": "Bearer test-token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Should return original user data without changes
            user_data = data["user"]
            assert user_data["nickname"] == "User"
            assert user_data["first_name"] == "Test"
            assert user_data["last_name"] == "User"

    def test_profile_update_none_values(self, client):
        """Test profile update with None values."""
        with patch('app_auth_simple.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            update_data = {
                "nickname": None,
                "first_name": None,
                "language": "en-US"
            }
            
            response = client.put(
                "/auth/profile",
                json=update_data,
                headers={"Authorization": "Bearer test-token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            user_data = data["user"]
            # None values should not be updated
            assert user_data["nickname"] == "User"  # Original value
            assert user_data["first_name"] == "Test"  # Original value
            assert user_data["language"] == "en-US"  # Updated value

    def test_profile_update_malformed_json(self, client):
        """Test profile update with malformed JSON."""
        response = client.put(
            "/auth/profile",
            data="invalid json",
            headers={
                "Authorization": "Bearer test-token",
                "Content-Type": "application/json"
            }
        )
        
        assert response.status_code == 422

    def test_profile_update_large_data(self, client):
        """Test profile update with large data."""
        large_data = {
            "nickname": "A" * 1000,  # Very long nickname
            "first_name": "B" * 1000,  # Very long first name
            "last_name": "C" * 1000,  # Very long last name
            "primary_condition": "D" * 1000,  # Very long condition
            "language": "en-US",
            "country": "US",
            "timezone": "America/New_York"
        }
        
        with patch('app_auth_simple.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            response = client.put(
                "/auth/profile",
                json=large_data,
                headers={"Authorization": "Bearer test-token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            user_data = data["user"]
            assert user_data["nickname"] == "A" * 1000
            assert user_data["first_name"] == "B" * 1000
            assert user_data["last_name"] == "C" * 1000
            assert user_data["primary_condition"] == "D" * 1000

    def test_profile_update_special_characters(self, client):
        """Test profile update with special characters."""
        special_data = {
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
                json=special_data,
                headers={"Authorization": "Bearer test-token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            user_data = data["user"]
            assert user_data["nickname"] == "テストユーザー"
            assert user_data["first_name"] == "José"
            assert user_data["last_name"] == "García-López"
            assert user_data["primary_condition"] == "心不全 & 糖尿病"

    def test_profile_update_timezone_validation(self, client):
        """Test profile update with different timezone values."""
        timezone_data = {
            "timezone": "Europe/London"
        }
        
        with patch('app_auth_simple.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            response = client.put(
                "/auth/profile",
                json=timezone_data,
                headers={"Authorization": "Bearer test-token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            user_data = data["user"]
            assert user_data["timezone"] == "Europe/London"

    def test_profile_update_language_validation(self, client):
        """Test profile update with different language values."""
        language_data = {
            "language": "fr-FR"
        }
        
        with patch('app_auth_simple.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            response = client.put(
                "/auth/profile",
                json=language_data,
                headers={"Authorization": "Bearer test-token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            user_data = data["user"]
            assert user_data["language"] == "fr-FR"

    def test_profile_update_country_validation(self, client):
        """Test profile update with different country values."""
        country_data = {
            "country": "FR"
        }
        
        with patch('app_auth_simple.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            response = client.put(
                "/auth/profile",
                json=country_data,
                headers={"Authorization": "Bearer test-token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            user_data = data["user"]
            assert user_data["country"] == "FR"

    def test_profile_update_response_structure(self, client, sample_profile_update_data):
        """Test that profile update response has correct structure."""
        with patch('app_auth_simple.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            response = client.put(
                "/auth/profile",
                json=sample_profile_update_data,
                headers={"Authorization": "Bearer test-token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Check response structure
            assert isinstance(data, dict)
            assert "message" in data
            assert "user" in data
            
            # Check message
            assert isinstance(data["message"], str)
            assert data["message"] == "Profile updated successfully"
            
            # Check user data structure
            user_data = data["user"]
            required_fields = [
                "id", "email", "nickname", "first_name", "last_name",
                "primary_condition", "language", "country", "timezone",
                "created_at", "updated_at"
            ]
            
            for field in required_fields:
                assert field in user_data, f"Missing field: {field}"
            
            # Check data types
            assert isinstance(user_data["id"], int)
            assert isinstance(user_data["email"], str)
            assert isinstance(user_data["nickname"], str)
            assert isinstance(user_data["first_name"], str)
            assert isinstance(user_data["last_name"], str)
            assert isinstance(user_data["primary_condition"], str)
            assert isinstance(user_data["language"], str)
            assert isinstance(user_data["country"], str)
            assert isinstance(user_data["timezone"], str)
            assert isinstance(user_data["created_at"], str)
            assert isinstance(user_data["updated_at"], str)

    def test_profile_update_updated_at_timestamp(self, client, sample_profile_update_data):
        """Test that updated_at timestamp is correctly set."""
        with patch('app_auth_simple.datetime') as mock_datetime:
            fixed_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = fixed_time
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            response = client.put(
                "/auth/profile",
                json=sample_profile_update_data,
                headers={"Authorization": "Bearer test-token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            user_data = data["user"]
            updated_at = user_data["updated_at"]
            
            # Check that updated_at is a valid ISO format timestamp
            assert isinstance(updated_at, str)
            # Should be able to parse as ISO format
            parsed_time = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            assert parsed_time == fixed_time

    def test_profile_update_concurrent_updates(self, client):
        """Test handling of concurrent profile updates."""
        update_data_1 = {"nickname": "User1"}
        update_data_2 = {"nickname": "User2"}
        
        with patch('app_auth_simple.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            # Simulate concurrent updates
            response1 = client.put(
                "/auth/profile",
                json=update_data_1,
                headers={"Authorization": "Bearer test-token"}
            )
            
            response2 = client.put(
                "/auth/profile",
                json=update_data_2,
                headers={"Authorization": "Bearer test-token"}
            )
            
            # Both should succeed
            assert response1.status_code == 200
            assert response2.status_code == 200
            
            # Check that the last update is reflected
            data1 = response1.json()
            data2 = response2.json()
            
            assert data1["user"]["nickname"] == "User1"
            assert data2["user"]["nickname"] == "User2"


class TestProfileManagementIntegration:
    """Integration tests for profile management with other components."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        from app_auth_simple import app
        return TestClient(app)
    
    def test_profile_update_after_registration(self, client):
        """Test profile update after user registration."""
        # First register a user
        registration_data = {
            "email": "newuser@example.com",
            "password": "password123",
            "nickname": "NewUser",
            "first_name": "New",
            "last_name": "User",
            "primary_condition": "Test Condition",
            "language": "en-US",
            "country": "US",
            "timezone": "UTC"
        }
        
        reg_response = client.post("/auth/register", json=registration_data)
        assert reg_response.status_code == 200
        
        # Extract token from registration response
        reg_data = reg_response.json()
        access_token = reg_data["access_token"]
        
        # Update profile with the token
        profile_update_data = {
            "nickname": "UpdatedNewUser",
            "language": "ja-JP",
            "country": "JP"
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
            
            user_data = update_data["user"]
            assert user_data["nickname"] == "UpdatedNewUser"
            assert user_data["language"] == "ja-JP"
            assert user_data["country"] == "JP"

    def test_profile_update_with_login_flow(self, client):
        """Test profile update in a complete login flow."""
        # Register user
        registration_data = {
            "email": "loginuser@example.com",
            "password": "password123",
            "nickname": "LoginUser",
            "first_name": "Login",
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
            "email": "loginuser@example.com",
            "password": "password123",
            "remember_me": False
        }
        
        login_response = client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        login_data_response = login_response.json()
        access_token = login_data_response["access_token"]
        
        # Update profile
        profile_update_data = {
            "nickname": "UpdatedLoginUser",
            "primary_condition": "Updated Condition"
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
            
            user_data = update_data["user"]
            assert user_data["nickname"] == "UpdatedLoginUser"
            assert user_data["primary_condition"] == "Updated Condition"

    def test_profile_update_error_handling(self, client):
        """Test error handling in profile update."""
        # Test with invalid JSON
        response = client.put(
            "/auth/profile",
            data="invalid json",
            headers={
                "Authorization": "Bearer test-token",
                "Content-Type": "application/json"
            }
        )
        
        assert response.status_code == 422
        
        # Test with missing Content-Type
        response = client.put(
            "/auth/profile",
            json={"nickname": "Test"},
            headers={"Authorization": "Bearer test-token"}
        )
        
        # Should still work as FastAPI can handle JSON without explicit Content-Type
        assert response.status_code == 200

    def test_profile_update_performance(self, client):
        """Test profile update performance with multiple fields."""
        large_update_data = {
            "nickname": "PerformanceTest",
            "first_name": "Performance",
            "last_name": "Test",
            "primary_condition": "Performance Testing",
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
                headers={"Authorization": "Bearer test-token"}
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            assert response.status_code == 200
            # Should complete within reasonable time (less than 1 second)
            assert response_time < 1.0
            
            data = response.json()
            user_data = data["user"]
            assert user_data["nickname"] == "PerformanceTest"
            assert user_data["first_name"] == "Performance"
            assert user_data["last_name"] == "Test"
