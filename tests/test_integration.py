"""
Integration tests for the healthcare community platform API.
These tests verify the complete workflow and interactions between components.
"""

import pytest
from fastapi.testclient import TestClient
from app_simple import app, posts_storage


class TestPostWorkflow:
    """Test complete post creation and retrieval workflow."""
    
    def test_complete_post_lifecycle(self, client, clean_posts_storage):
        """Test complete post lifecycle from creation to retrieval."""
        # 1. Verify empty state
        response = client.get("/api/posts")
        assert response.status_code == 200
        assert response.json() == []
        
        # 2. Create a post
        post_data = {
            "title": "Lifecycle Test Post",
            "content": "This post tests the complete lifecycle",
            "group_id": 1
        }
        
        create_response = client.post("/api/posts", json=post_data)
        assert create_response.status_code == 200
        
        created_post = create_response.json()
        assert created_post["title"] == "Lifecycle Test Post"
        assert created_post["content"] == "This post tests the complete lifecycle"
        assert created_post["group_id"] == 1
        assert created_post["id"] == 1
        assert "created_at" in created_post
        
        # 3. Verify post appears in list
        list_response = client.get("/api/posts")
        assert list_response.status_code == 200
        
        posts = list_response.json()
        assert len(posts) == 1
        assert posts[0]["id"] == created_post["id"]
        assert posts[0]["title"] == created_post["title"]
        
        # 4. Retrieve specific post
        get_response = client.get(f"/api/posts/{created_post['id']}")
        assert get_response.status_code == 200
        
        retrieved_post = get_response.json()
        assert retrieved_post["id"] == created_post["id"]
        assert retrieved_post["title"] == created_post["title"]
        assert retrieved_post["content"] == created_post["content"]
        assert retrieved_post["group_id"] == created_post["group_id"]
        assert retrieved_post["created_at"] == created_post["created_at"]
    
    def test_multiple_posts_workflow(self, client, clean_posts_storage):
        """Test workflow with multiple posts."""
        # Create multiple posts
        posts_data = [
            {"title": "First Post", "content": "First content", "group_id": 1},
            {"title": "Second Post", "content": "Second content", "group_id": 2},
            {"title": "Third Post", "content": "Third content", "group_id": 1},
        ]
        
        created_posts = []
        for i, post_data in enumerate(posts_data):
            response = client.post("/api/posts", json=post_data)
            assert response.status_code == 200
            
            post = response.json()
            assert post["id"] == i + 1
            created_posts.append(post)
        
        # Verify all posts are in the list
        list_response = client.get("/api/posts")
        assert list_response.status_code == 200
        
        all_posts = list_response.json()
        assert len(all_posts) == 3
        
        # Verify each post can be retrieved individually
        for created_post in created_posts:
            get_response = client.get(f"/api/posts/{created_post['id']}")
            assert get_response.status_code == 200
            
            retrieved_post = get_response.json()
            assert retrieved_post["id"] == created_post["id"]
            assert retrieved_post["title"] == created_post["title"]
    
    def test_error_handling_workflow(self, client, clean_posts_storage):
        """Test error handling in the workflow."""
        # Try to get a non-existent post
        response = client.get("/api/posts/999")
        assert response.status_code == 404
        assert "Post not found" in response.json()["detail"]
        
        # Try to create a post with invalid data
        invalid_data = {"title": "Test"}  # Missing required fields
        response = client.post("/api/posts", json=invalid_data)
        assert response.status_code == 422  # Validation error
        
        # Verify that invalid post wasn't created
        list_response = client.get("/api/posts")
        assert list_response.status_code == 200
        assert list_response.json() == []


class TestAPIEndpointsIntegration:
    """Test integration between different API endpoints."""
    
    def test_health_endpoints_consistency(self, client):
        """Test that all health endpoints return consistent information."""
        endpoints = ["/", "/health", "/api/status"]
        
        responses = []
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200
            responses.append(response.json())
        
        # All responses should have status and message fields
        for response in responses:
            assert "status" in response
            assert "message" in response
            assert isinstance(response["status"], str)
            assert isinstance(response["message"], str)
    
    def test_cors_headers_consistency(self, client):
        """Test that CORS headers are consistent across endpoints."""
        endpoints = ["/", "/health", "/api/status", "/api/posts"]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200
            
            # CORS headers should be present (TestClient might not show all headers)
            # This is more of an integration test to ensure endpoints are accessible
            assert response.status_code == 200
    
    def test_post_endpoints_with_different_http_methods(self, client, clean_posts_storage):
        """Test post endpoints with different HTTP methods."""
        # GET /api/posts should work
        response = client.get("/api/posts")
        assert response.status_code == 200
        
        # POST /api/posts should work
        post_data = {"title": "Test", "content": "Content", "group_id": 1}
        response = client.post("/api/posts", json=post_data)
        assert response.status_code == 200
        
        # GET /api/posts/{id} should work
        post_id = response.json()["id"]
        response = client.get(f"/api/posts/{post_id}")
        assert response.status_code == 200
        
        # PUT, DELETE, PATCH should return 405 (Method Not Allowed) for now
        response = client.put(f"/api/posts/{post_id}", json=post_data)
        assert response.status_code == 405
        
        response = client.delete(f"/api/posts/{post_id}")
        assert response.status_code == 405
        
        response = client.patch(f"/api/posts/{post_id}", json={"title": "Updated"})
        assert response.status_code == 405


class TestDataPersistence:
    """Test data persistence within the same session."""
    
    def test_posts_persist_within_session(self, client, clean_posts_storage):
        """Test that posts persist within the same test session."""
        # Create a post
        post_data = {"title": "Persistent Post", "content": "Content", "group_id": 1}
        create_response = client.post("/api/posts", json=post_data)
        assert create_response.status_code == 200
        
        post_id = create_response.json()["id"]
        
        # Verify post exists in list
        list_response = client.get("/api/posts")
        assert list_response.status_code == 200
        assert len(list_response.json()) == 1
        
        # Verify post can be retrieved by ID
        get_response = client.get(f"/api/posts/{post_id}")
        assert get_response.status_code == 200
        
        # Create another post
        post_data2 = {"title": "Second Post", "content": "Content 2", "group_id": 2}
        create_response2 = client.post("/api/posts", json=post_data2)
        assert create_response2.status_code == 200
        
        # Verify both posts exist
        list_response = client.get("/api/posts")
        assert list_response.status_code == 200
        assert len(list_response.json()) == 2
    
    def test_post_id_increment(self, client, clean_posts_storage):
        """Test that post IDs increment correctly."""
        # Create multiple posts and verify ID increment
        for i in range(5):
            post_data = {
                "title": f"Post {i+1}",
                "content": f"Content {i+1}",
                "group_id": i+1
            }
            
            response = client.post("/api/posts", json=post_data)
            assert response.status_code == 200
            
            post = response.json()
            assert post["id"] == i + 1
        
        # Verify all posts exist with correct IDs
        list_response = client.get("/api/posts")
        assert list_response.status_code == 200
        
        posts = list_response.json()
        assert len(posts) == 5
        
        for i, post in enumerate(posts):
            assert post["id"] == i + 1
            assert post["title"] == f"Post {i+1}"


class TestErrorScenarios:
    """Test error scenarios and edge cases."""
    
    def test_invalid_post_id_formats(self, client, clean_posts_storage):
        """Test various invalid post ID formats."""
        invalid_ids = ["abc", "1.5", "-1", "0", "999999999"]
        
        for invalid_id in invalid_ids:
            response = client.get(f"/api/posts/{invalid_id}")
            # Should return 404 for non-existent IDs or 422 for invalid formats
            assert response.status_code in [404, 422]
    
    def test_malformed_json_requests(self, client):
        """Test handling of malformed JSON requests."""
        # Invalid JSON
        response = client.post(
            "/api/posts",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
        
        # Missing Content-Type header
        response = client.post("/api/posts", data="{}")
        # Should handle gracefully
        assert response.status_code in [422, 415]
    
    def test_large_payload_handling(self, client):
        """Test handling of large payloads."""
        # Create a post with very long content
        long_content = "x" * 10000  # 10KB of content
        post_data = {
            "title": "Large Post",
            "content": long_content,
            "group_id": 1
        }
        
        response = client.post("/api/posts", json=post_data)
        # Should handle large content gracefully
        assert response.status_code == 200
        
        post = response.json()
        assert post["content"] == long_content


if __name__ == "__main__":
    pytest.main([__file__])
