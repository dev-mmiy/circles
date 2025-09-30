"""
認証システムのテスト
疾患を抱える消費者向けの認証システム
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from unittest.mock import patch
import os

from app_auth import app, get_db
from auth_models import UserRegister, UserLogin, UserProfileUpdate

# テスト用データベース
TEST_DATABASE_URL = "sqlite:///./test_auth.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})

def get_test_db():
    """テスト用データベースセッション"""
    with Session(engine) as session:
        yield session

# テスト用の依存性注入
app.dependency_overrides[get_db] = get_test_db

# テストクライアント
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_db():
    """テストデータベースセットアップ"""
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)

class TestAuthSystem:
    """認証システムのテスト"""
    
    def test_health_check(self):
        """ヘルスチェックテスト"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "authentication" in data
    
    def test_auth_health_check(self):
        """認証サービスヘルスチェックテスト"""
        response = client.get("/auth/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "authentication"
    
    def test_user_registration(self):
        """ユーザー登録テスト"""
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "nickname": "Test User",
            "first_name": "Test",
            "last_name": "User",
            "primary_condition": "Test Condition",
            "language": "en-US",
            "country": "US",
            "timezone": "UTC"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 201
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
        assert data["user"]["nickname"] == "Test User"
    
    def test_user_login(self):
        """ユーザーログインテスト"""
        # まずユーザー登録
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "nickname": "Test User"
        }
        client.post("/auth/register", json=user_data)
        
        # ログイン
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
    
    def test_invalid_login(self):
        """無効なログインテスト"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 401
    
    def test_protected_endpoints_without_auth(self):
        """認証なしでの保護されたエンドポイントアクセステスト"""
        # 投稿一覧取得（認証必須）
        response = client.get("/posts")
        assert response.status_code == 401
        
        # 投稿作成（認証必須）
        post_data = {
            "title": "Test Post",
            "content": "Test content"
        }
        response = client.post("/posts", json=post_data)
        assert response.status_code == 401
    
    def test_protected_endpoints_with_auth(self):
        """認証ありでの保護されたエンドポイントアクセステスト"""
        # ユーザー登録
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "nickname": "Test User"
        }
        register_response = client.post("/auth/register", json=user_data)
        assert register_response.status_code == 201
        
        # アクセストークン取得
        auth_data = register_response.json()
        access_token = auth_data["access_token"]
        
        # 認証ヘッダー付きで投稿作成
        headers = {"Authorization": f"Bearer {access_token}"}
        post_data = {
            "title": "Test Post",
            "content": "Test content"
        }
        
        response = client.post("/posts", json=post_data, headers=headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["title"] == "Test Post"
        assert data["content"] == "Test content"
        assert data["author_id"] == 1  # 登録されたユーザーID
    
    def test_get_user_posts(self):
        """ユーザーの投稿一覧取得テスト"""
        # ユーザー登録
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "nickname": "Test User"
        }
        register_response = client.post("/auth/register", json=user_data)
        access_token = register_response.json()["access_token"]
        
        # 複数の投稿作成
        headers = {"Authorization": f"Bearer {access_token}"}
        for i in range(3):
            post_data = {
                "title": f"Test Post {i+1}",
                "content": f"Test content {i+1}"
            }
            client.post("/posts", json=post_data, headers=headers)
        
        # ユーザーの投稿一覧取得
        response = client.get("/user/posts", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 3
        assert all(post["author_id"] == 1 for post in data)
    
    def test_update_post_authorization(self):
        """投稿更新の認証テスト"""
        # ユーザー登録
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "nickname": "Test User"
        }
        register_response = client.post("/auth/register", json=user_data)
        access_token = register_response.json()["access_token"]
        
        # 投稿作成
        headers = {"Authorization": f"Bearer {access_token}"}
        post_data = {
            "title": "Test Post",
            "content": "Test content"
        }
        create_response = client.post("/posts", json=post_data, headers=headers)
        post_id = create_response.json()["id"]
        
        # 投稿更新
        update_data = {
            "title": "Updated Post",
            "content": "Updated content"
        }
        response = client.put(f"/posts/{post_id}", json=update_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Updated Post"
        assert data["content"] == "Updated content"
    
    def test_delete_post_authorization(self):
        """投稿削除の認証テスト"""
        # ユーザー登録
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "nickname": "Test User"
        }
        register_response = client.post("/auth/register", json=user_data)
        access_token = register_response.json()["access_token"]
        
        # 投稿作成
        headers = {"Authorization": f"Bearer {access_token}"}
        post_data = {
            "title": "Test Post",
            "content": "Test content"
        }
        create_response = client.post("/posts", json=post_data, headers=headers)
        post_id = create_response.json()["id"]
        
        # 投稿削除
        response = client.delete(f"/posts/{post_id}", headers=headers)
        assert response.status_code == 200
        
        # 削除確認
        response = client.get(f"/posts/{post_id}", headers=headers)
        assert response.status_code == 404
    
    def test_token_refresh(self):
        """トークンリフレッシュテスト"""
        # ユーザー登録
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "nickname": "Test User"
        }
        register_response = client.post("/auth/register", json=user_data)
        refresh_token = register_response.json()["refresh_token"]
        
        # トークンリフレッシュ
        refresh_data = {"refresh_token": refresh_token}
        response = client.post("/auth/refresh", json=refresh_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_logout(self):
        """ログアウトテスト"""
        # ユーザー登録
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "nickname": "Test User"
        }
        register_response = client.post("/auth/register", json=user_data)
        access_token = register_response.json()["access_token"]
        
        # ログアウト
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.post("/auth/logout", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Logout successful"
    
    def test_get_current_user_profile(self):
        """現在のユーザープロフィール取得テスト"""
        # ユーザー登録
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "nickname": "Test User",
            "first_name": "Test",
            "last_name": "User"
        }
        register_response = client.post("/auth/register", json=user_data)
        access_token = register_response.json()["access_token"]
        
        # プロフィール取得
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/auth/me", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["nickname"] == "Test User"
        assert data["first_name"] == "Test"
        assert data["last_name"] == "User"
    
    def test_update_user_profile(self):
        """ユーザープロフィール更新テスト"""
        # ユーザー登録
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "nickname": "Test User"
        }
        register_response = client.post("/auth/register", json=user_data)
        access_token = register_response.json()["access_token"]
        
        # プロフィール更新
        headers = {"Authorization": f"Bearer {access_token}"}
        update_data = {
            "nickname": "Updated User",
            "first_name": "Updated",
            "last_name": "User"
        }
        response = client.put("/auth/me", json=update_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["nickname"] == "Updated User"
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "User"

if __name__ == "__main__":
    pytest.main([__file__])


