"""
Pytest configuration and fixtures for the test suite.
"""

import pytest
from fastapi.testclient import TestClient
from app_simple import app, posts_storage, post_id_counter


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def clean_posts_storage():
    """Clean posts storage before each test."""
    global posts_storage, post_id_counter
    posts_storage.clear()
    # Reset counter to 1 for each test
    import app_simple
    app_simple.post_id_counter = 1
    yield
    # Cleanup after test
    posts_storage.clear()
    app_simple.post_id_counter = 1


@pytest.fixture
def sample_post_data():
    """Sample post data for testing."""
    return {
        "title": "Test Post",
        "content": "This is a test post",
        "group_id": 1
    }


@pytest.fixture
def multiple_posts_data():
    """Multiple sample posts for testing."""
    return [
        {"title": "Post 1", "content": "Content 1", "group_id": 1},
        {"title": "Post 2", "content": "Content 2", "group_id": 2},
        {"title": "Post 3", "content": "Content 3", "group_id": 1},
    ]


@pytest.fixture
def created_post(client, sample_post_data):
    """Create a post and return its data."""
    response = client.post("/api/posts", json=sample_post_data)
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def created_posts(client, multiple_posts_data):
    """Create multiple posts and return their data."""
    posts = []
    for post_data in multiple_posts_data:
        response = client.post("/api/posts", json=post_data)
        assert response.status_code == 200
        posts.append(response.json())
    return posts


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom settings."""
    config.addinivalue_line(
        "markers", "unit: Unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow running tests"
    )
    config.addinivalue_line(
        "markers", "api: API endpoint tests"
    )
    config.addinivalue_line(
        "markers", "model: Model validation tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add unit marker to all tests in test_models.py
        if "test_models" in item.nodeid:
            item.add_marker(pytest.mark.unit)
            item.add_marker(pytest.mark.model)
        
        # Add api marker to all tests in test_app_simple.py
        if "test_app_simple" in item.nodeid:
            item.add_marker(pytest.mark.unit)
            item.add_marker(pytest.mark.api)
        
        # Add integration marker to tests that use fixtures
        if "created_post" in item.fixturenames or "created_posts" in item.fixturenames:
            item.add_marker(pytest.mark.integration)
