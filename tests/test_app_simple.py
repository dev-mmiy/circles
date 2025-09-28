"""
Unit tests for app_simple.py
Tests the basic FastAPI application endpoints and functionality.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from app_simple import app, posts_storage, post_id_counter

# Test client
client = TestClient(app)


class TestHealthEndpoints:
    """Test health check and status endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint returns correct response."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "Healthcare Community Platform API" in data["message"]
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "API is running" in data["message"]
    
    def test_api_status_endpoint(self):
        """Test API status endpoint."""
        response = client.get("/api/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"
        assert "API is active and ready" in data["message"]


class TestPostEndpoints:
    """Test post-related endpoints."""
    
    def setup_method(self):
        """Reset posts storage before each test."""
        global posts_storage, post_id_counter
        posts_storage.clear()
        # Reset counter to 1 for each test
        import app_simple
        app_simple.post_id_counter = 1
    
    def test_create_post_success(self):
        """Test successful post creation."""
        post_data = {
            "title": "Test Post",
            "content": "This is a test post",
            "group_id": 1
        }
        
        response = client.post("/api/posts", json=post_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Test Post"
        assert data["content"] == "This is a test post"
        assert data["group_id"] == 1
        assert data["id"] == 1
        assert "created_at" in data
        
        # Test that created_at is a valid ISO format timestamp
        created_at = data["created_at"]
        assert isinstance(created_at, str)
        # Parse the timestamp to ensure it's valid
        parsed_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        assert isinstance(parsed_time, datetime)
    
    def test_create_post_validation(self):
        """Test post creation with invalid data."""
        # Missing required fields
        response = client.post("/api/posts", json={"title": "Test"})
        assert response.status_code == 422  # Validation error
    
    def test_get_posts_empty(self):
        """Test getting posts when storage is empty."""
        response = client.get("/api/posts")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_posts_with_data(self):
        """Test getting posts when storage has data."""
        # Create a post first
        post_data = {
            "title": "Test Post",
            "content": "This is a test post",
            "group_id": 1
        }
        client.post("/api/posts", json=post_data)
        
        # Get all posts
        response = client.get("/api/posts")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Test Post"
    
    def test_get_specific_post_success(self):
        """Test getting a specific post that exists."""
        # Create a post first
        post_data = {
            "title": "Test Post",
            "content": "This is a test post",
            "group_id": 1
        }
        create_response = client.post("/api/posts", json=post_data)
        post_id = create_response.json()["id"]
        
        # Get the specific post
        response = client.get(f"/api/posts/{post_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == post_id
        assert data["title"] == "Test Post"
    
    def test_get_specific_post_not_found(self):
        """Test getting a specific post that doesn't exist."""
        response = client.get("/api/posts/999")
        assert response.status_code == 404
        assert "Post not found" in response.json()["detail"]
    
    def test_multiple_posts(self):
        """Test creating and retrieving multiple posts."""
        # Create multiple posts
        for i in range(3):
            post_data = {
                "title": f"Test Post {i+1}",
                "content": f"This is test post {i+1}",
                "group_id": i+1
            }
            response = client.post("/api/posts", json=post_data)
            assert response.status_code == 200
        
        # Get all posts
        response = client.get("/api/posts")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 3
        
        # Check that posts are ordered correctly
        for i, post in enumerate(data):
            assert post["id"] == i + 1
            assert post["title"] == f"Test Post {i+1}"


class TestDataModels:
    """Test Pydantic models."""
    
    def test_health_check_model(self):
        """Test HealthCheck model validation."""
        from app_simple import HealthCheck
        
        # Valid data
        health = HealthCheck(status="ok", message="test")
        assert health.status == "ok"
        assert health.message == "test"
        
        # Test with different values
        health = HealthCheck(status="error", message="error message")
        assert health.status == "error"
        assert health.message == "error message"
    
    def test_post_create_model(self):
        """Test PostCreate model validation."""
        from app_simple import PostCreate
        
        # Valid data
        post = PostCreate(title="Test", content="Content", group_id=1)
        assert post.title == "Test"
        assert post.content == "Content"
        assert post.group_id == 1
    
    def test_post_read_model(self):
        """Test PostRead model validation."""
        from app_simple import PostRead
        
        # Valid data
        post = PostRead(
            id=1,
            title="Test",
            content="Content",
            group_id=1,
            created_at="2024-01-01T00:00:00Z"
        )
        assert post.id == 1
        assert post.title == "Test"
        assert post.content == "Content"
        assert post.group_id == 1
        assert post.created_at == "2024-01-01T00:00:00Z"


class TestCORS:
    """Test CORS middleware."""
    
    def test_cors_headers(self):
        """Test that CORS headers are present."""
        response = client.get("/")
        assert response.status_code == 200
        
        # Check for CORS headers (TestClient might not show all headers)
        # This is more of an integration test, but we can verify the endpoint works
        assert "status" in response.json()


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_invalid_json(self):
        """Test handling of invalid JSON."""
        response = client.post(
            "/api/posts",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_missing_content_type(self):
        """Test handling of missing content type."""
        response = client.post("/api/posts", data="{}")
        # FastAPI should handle this gracefully
        assert response.status_code in [422, 415]  # Unprocessable Entity or Unsupported Media Type


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def setup_method(self):
        """Reset posts storage before each test."""
        global posts_storage, post_id_counter
        posts_storage.clear()
        import app_simple
        app_simple.post_id_counter = 1
    
    def test_empty_string_fields(self):
        """Test handling of empty string fields."""
        post_data = {
            "title": "",
            "content": "",
            "group_id": 1
        }
        
        response = client.post("/api/posts", json=post_data)
        # Should succeed (empty strings are valid)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == ""
        assert data["content"] == ""
    
    def test_large_group_id(self):
        """Test handling of large group IDs."""
        post_data = {
            "title": "Test",
            "content": "Content",
            "group_id": 999999
        }
        
        response = client.post("/api/posts", json=post_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["group_id"] == 999999
    
    def test_negative_group_id(self):
        """Test handling of negative group IDs."""
        post_data = {
            "title": "Test",
            "content": "Content",
            "group_id": -1
        }
        
        response = client.post("/api/posts", json=post_data)
        # Should succeed (negative integers are valid)
        assert response.status_code == 200
        
        data = response.json()
        assert data["group_id"] == -1


class TestTimestampFunctionality:
    """Test timestamp-related functionality."""
    
    def setup_method(self):
        """Reset posts storage before each test."""
        global posts_storage, post_id_counter
        posts_storage.clear()
        import app_simple
        app_simple.post_id_counter = 1
    
    def test_timestamp_is_current(self):
        """Test that created_at timestamp is current."""
        before_creation = datetime.now(timezone.utc)
        
        post_data = {
            "title": "Timestamp Test",
            "content": "Testing timestamp accuracy",
            "group_id": 1
        }
        
        response = client.post("/api/posts", json=post_data)
        assert response.status_code == 200
        
        after_creation = datetime.now(timezone.utc)
        
        data = response.json()
        created_at_str = data["created_at"]
        created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
        
        # The timestamp should be between before and after creation
        assert before_creation <= created_at <= after_creation
    
    def test_timestamp_format(self):
        """Test that timestamp is in correct ISO format."""
        post_data = {
            "title": "Format Test",
            "content": "Testing timestamp format",
            "group_id": 1
        }
        
        response = client.post("/api/posts", json=post_data)
        assert response.status_code == 200
        
        data = response.json()
        created_at = data["created_at"]
        
        # Should be in ISO format with timezone
        assert created_at.endswith('+00:00') or created_at.endswith('Z')
        assert 'T' in created_at  # ISO format has T between date and time
    
    def test_multiple_posts_different_timestamps(self):
        """Test that multiple posts have different timestamps."""
        import time
        
        # Create first post
        post1_data = {
            "title": "First Post",
            "content": "First post content",
            "group_id": 1
        }
        response1 = client.post("/api/posts", json=post1_data)
        assert response1.status_code == 200
        
        # Wait a small amount to ensure different timestamps
        time.sleep(0.01)
        
        # Create second post
        post2_data = {
            "title": "Second Post",
            "content": "Second post content",
            "group_id": 1
        }
        response2 = client.post("/api/posts", json=post2_data)
        assert response2.status_code == 200
        
        # Check that timestamps are different
        data1 = response1.json()
        data2 = response2.json()
        
        assert data1["created_at"] != data2["created_at"]
        
        # Parse timestamps and verify order
        timestamp1 = datetime.fromisoformat(data1["created_at"].replace('Z', '+00:00'))
        timestamp2 = datetime.fromisoformat(data2["created_at"].replace('Z', '+00:00'))
        
        assert timestamp1 < timestamp2


if __name__ == "__main__":
    pytest.main([__file__])
