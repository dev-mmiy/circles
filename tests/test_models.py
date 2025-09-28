"""
Unit tests for Pydantic models and data validation.
"""

import pytest
from pydantic import ValidationError
from app_simple import HealthCheck, PostCreate, PostRead


class TestHealthCheckModel:
    """Test HealthCheck model validation."""
    
    def test_valid_health_check(self):
        """Test valid HealthCheck creation."""
        health = HealthCheck(status="ok", message="test message")
        assert health.status == "ok"
        assert health.message == "test message"
    
    def test_health_check_with_different_statuses(self):
        """Test HealthCheck with different status values."""
        statuses = ["ok", "healthy", "error", "warning", "info"]
        
        for status in statuses:
            health = HealthCheck(status=status, message="test")
            assert health.status == status
    
    def test_health_check_with_empty_message(self):
        """Test HealthCheck with empty message."""
        health = HealthCheck(status="ok", message="")
        assert health.status == "ok"
        assert health.message == ""
    
    def test_health_check_with_long_message(self):
        """Test HealthCheck with long message."""
        long_message = "x" * 1000
        health = HealthCheck(status="ok", message=long_message)
        assert health.message == long_message
    
    def test_health_check_serialization(self):
        """Test HealthCheck serialization to dict."""
        health = HealthCheck(status="ok", message="test")
        data = health.model_dump()
        
        assert data["status"] == "ok"
        assert data["message"] == "test"
        assert len(data) == 2  # Only status and message fields
    
    def test_health_check_json_serialization(self):
        """Test HealthCheck JSON serialization."""
        health = HealthCheck(status="ok", message="test")
        json_data = health.model_dump_json()
        
        assert '"status":"ok"' in json_data
        assert '"message":"test"' in json_data


class TestPostCreateModel:
    """Test PostCreate model validation."""
    
    def test_valid_post_create(self):
        """Test valid PostCreate creation."""
        post = PostCreate(title="Test Title", content="Test Content", group_id=1)
        assert post.title == "Test Title"
        assert post.content == "Test Content"
        assert post.group_id == 1
    
    def test_post_create_with_empty_strings(self):
        """Test PostCreate with empty strings."""
        post = PostCreate(title="", content="", group_id=1)
        assert post.title == ""
        assert post.content == ""
        assert post.group_id == 1
    
    def test_post_create_with_whitespace(self):
        """Test PostCreate with whitespace-only strings."""
        post = PostCreate(title="   ", content="\n\t", group_id=1)
        assert post.title == "   "
        assert post.content == "\n\t"
        assert post.group_id == 1
    
    def test_post_create_with_special_characters(self):
        """Test PostCreate with special characters."""
        title = "Test Title with émojis 🚀 and special chars: !@#$%^&*()"
        content = "Content with\nnewlines\tand\ttabs"
        
        post = PostCreate(title=title, content=content, group_id=1)
        assert post.title == title
        assert post.content == content
    
    def test_post_create_with_different_group_ids(self):
        """Test PostCreate with different group ID values."""
        group_ids = [0, 1, 100, -1, 999999]
        
        for group_id in group_ids:
            post = PostCreate(title="Test", content="Content", group_id=group_id)
            assert post.group_id == group_id
    
    def test_post_create_serialization(self):
        """Test PostCreate serialization."""
        post = PostCreate(title="Test", content="Content", group_id=1)
        data = post.model_dump()
        
        assert data["title"] == "Test"
        assert data["content"] == "Content"
        assert data["group_id"] == 1
        assert len(data) == 3
    
    def test_post_create_validation_errors(self):
        """Test PostCreate validation errors."""
        # Missing required fields
        with pytest.raises(ValidationError):
            PostCreate(title="Test")  # Missing content and group_id
        
        with pytest.raises(ValidationError):
            PostCreate(content="Content")  # Missing title and group_id
        
        with pytest.raises(ValidationError):
            PostCreate(group_id=1)  # Missing title and content
        
        # Invalid types
        with pytest.raises(ValidationError):
            PostCreate(title=123, content="Content", group_id=1)  # title should be string
        
        with pytest.raises(ValidationError):
            PostCreate(title="Test", content=123, group_id=1)  # content should be string
        
        # Note: Pydantic V2 is more lenient with type coercion
        # group_id="1" will be converted to int(1), so this won't raise an error
        # Let's test with a truly invalid type
        with pytest.raises(ValidationError):
            PostCreate(title="Test", content="Content", group_id="abc")  # group_id should be int


class TestPostReadModel:
    """Test PostRead model validation."""
    
    def test_valid_post_read(self):
        """Test valid PostRead creation."""
        post = PostRead(
            id=1,
            title="Test Title",
            content="Test Content",
            group_id=1,
            created_at="2024-01-01T00:00:00Z"
        )
        assert post.id == 1
        assert post.title == "Test Title"
        assert post.content == "Test Content"
        assert post.group_id == 1
        assert post.created_at == "2024-01-01T00:00:00Z"
    
    def test_post_read_with_different_ids(self):
        """Test PostRead with different ID values."""
        ids = [0, 1, 100, 999999]
        
        for post_id in ids:
            post = PostRead(
                id=post_id,
                title="Test",
                content="Content",
                group_id=1,
                created_at="2024-01-01T00:00:00Z"
            )
            assert post.id == post_id
    
    def test_post_read_with_different_created_at_formats(self):
        """Test PostRead with different created_at formats."""
        timestamps = [
            "2024-01-01T00:00:00Z",
            "2024-12-31T23:59:59Z",
            "2023-06-15T12:30:45Z",
            "2025-01-01T00:00:00.000Z"
        ]
        
        for timestamp in timestamps:
            post = PostRead(
                id=1,
                title="Test",
                content="Content",
                group_id=1,
                created_at=timestamp
            )
            assert post.created_at == timestamp
    
    def test_post_read_serialization(self):
        """Test PostRead serialization."""
        post = PostRead(
            id=1,
            title="Test",
            content="Content",
            group_id=1,
            created_at="2024-01-01T00:00:00Z"
        )
        data = post.model_dump()
        
        assert data["id"] == 1
        assert data["title"] == "Test"
        assert data["content"] == "Content"
        assert data["group_id"] == 1
        assert data["created_at"] == "2024-01-01T00:00:00Z"
        assert len(data) == 5
    
    def test_post_read_validation_errors(self):
        """Test PostRead validation errors."""
        # Missing required fields
        with pytest.raises(ValidationError):
            PostRead(
                title="Test",
                content="Content",
                group_id=1,
                created_at="2024-01-01T00:00:00Z"
            )  # Missing id
        
        # Invalid types - Pydantic V2 is more lenient with type coercion
        # "1" will be converted to int(1), so let's test with truly invalid types
        with pytest.raises(ValidationError):
            PostRead(
                id="abc",  # Should be int, not convertible string
                title="Test",
                content="Content",
                group_id=1,
                created_at="2024-01-01T00:00:00Z"
            )


class TestModelIntegration:
    """Test model integration and conversion."""
    
    def test_post_create_to_post_read_conversion(self):
        """Test converting PostCreate to PostRead."""
        post_create = PostCreate(title="Test", content="Content", group_id=1)
        
        # Simulate the conversion that happens in the API
        post_read = PostRead(
            id=1,
            title=post_create.title,
            content=post_create.content,
            group_id=post_create.group_id,
            created_at="2024-01-01T00:00:00Z"
        )
        
        assert post_read.title == post_create.title
        assert post_read.content == post_create.content
        assert post_read.group_id == post_create.group_id
    
    def test_model_json_roundtrip(self):
        """Test JSON serialization and deserialization."""
        # HealthCheck roundtrip
        health = HealthCheck(status="ok", message="test")
        json_str = health.model_dump_json()
        health_restored = HealthCheck.model_validate_json(json_str)
        assert health_restored.status == health.status
        assert health_restored.message == health.message
        
        # PostCreate roundtrip
        post_create = PostCreate(title="Test", content="Content", group_id=1)
        json_str = post_create.model_dump_json()
        post_restored = PostCreate.model_validate_json(json_str)
        assert post_restored.title == post_create.title
        assert post_restored.content == post_create.content
        assert post_restored.group_id == post_create.group_id
        
        # PostRead roundtrip
        post_read = PostRead(
            id=1,
            title="Test",
            content="Content",
            group_id=1,
            created_at="2024-01-01T00:00:00Z"
        )
        json_str = post_read.model_dump_json()
        post_restored = PostRead.model_validate_json(json_str)
        assert post_restored.id == post_read.id
        assert post_restored.title == post_read.title
        assert post_restored.content == post_read.content
        assert post_restored.group_id == post_read.group_id
        assert post_restored.created_at == post_read.created_at


if __name__ == "__main__":
    pytest.main([__file__])
