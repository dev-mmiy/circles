"""
包括的な認証システムのUnitテスト
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.pool import StaticPool

from app_auth_simple import app
from auth_models import Account, UserProfile, UserSession, MFAConfig, UserRoleAssignment
from auth_service import AuthService
from auth_endpoints import auth_router


class TestAuthSystem:
    """認証システムの包括的テスト"""
    
    @pytest.fixture
    def db_session(self):
        """テスト用データベースセッション"""
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        SQLModel.metadata.create_all(engine)
        with Session(engine) as session:
            yield session
    
    @pytest.fixture
    def auth_service(self, db_session):
        """認証サービス"""
        return AuthService(db_session)
    
    @pytest.fixture
    def client(self):
        """テストクライアント"""
        return TestClient(app)
    
    def test_user_registration_success(self, auth_service, db_session):
        """ユーザー登録の成功テスト"""
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "nickname": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "primary_condition": "Test Condition"
        }
        
        # ユーザー登録
        account = auth_service.register_user(user_data)
        
        # 検証
        assert account.email == "test@example.com"
        assert account.status == "pending_verification"
        assert account.id is not None
        
        # プロフィールの確認
        profile = auth_service.get_user_profile(account.id)
        assert profile is not None
        assert profile.nickname == "testuser"
        assert profile.primary_condition == "Test Condition"
        
        # ロールの確認
        roles = db_session.query(UserRoleAssignment).filter(
            UserRoleAssignment.account_id == account.id
        ).all()
        assert len(roles) == 1
        assert roles[0].role == "patient"
    
    def test_user_registration_duplicate_email(self, auth_service, db_session):
        """重複メールアドレスでの登録失敗テスト"""
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "nickname": "testuser"
        }
        
        # 最初の登録
        auth_service.register_user(user_data)
        
        # 重複メールアドレスでの登録試行
        with pytest.raises(Exception):  # HTTPException or similar
            auth_service.register_user(user_data)
    
    def test_user_login_success(self, auth_service, db_session):
        """ユーザーログインの成功テスト"""
        # ユーザー登録
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "nickname": "testuser"
        }
        account = auth_service.register_user(user_data)
        
        # ログイン
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        with patch('auth_service.Request') as mock_request:
            mock_request.client.host = "127.0.0.1"
            mock_request.headers = {"user-agent": "test"}
            
            response = auth_service.login_user(login_data, mock_request)
            
            # 検証
            assert response.access_token is not None
            assert response.token_type == "bearer"
            assert response.refresh_token is not None
            assert response.user.account_id == account.id
    
    def test_user_login_invalid_credentials(self, auth_service, db_session):
        """無効な認証情報でのログイン失敗テスト"""
        # ユーザー登録
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "nickname": "testuser"
        }
        auth_service.register_user(user_data)
        
        # 無効なパスワードでログイン試行
        login_data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        
        with patch('auth_service.Request') as mock_request:
            mock_request.client.host = "127.0.0.1"
            mock_request.headers = {"user-agent": "test"}
            
            with pytest.raises(Exception):  # HTTPException
                auth_service.login_user(login_data, mock_request)
    
    def test_token_refresh(self, auth_service, db_session):
        """トークンリフレッシュのテスト"""
        # ユーザー登録とログイン
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "nickname": "testuser"
        }
        account = auth_service.register_user(user_data)
        
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        with patch('auth_service.Request') as mock_request:
            mock_request.client.host = "127.0.0.1"
            mock_request.headers = {"user-agent": "test"}
            
            login_response = auth_service.login_user(login_data, mock_request)
            refresh_token = login_response.refresh_token
            
            # トークンリフレッシュ
            new_tokens = auth_service.refresh_token(refresh_token)
            
            # 検証
            assert new_tokens.access_token is not None
            assert new_tokens.refresh_token is not None
            assert new_tokens.access_token != login_response.access_token
    
    def test_user_profile_update(self, auth_service, db_session):
        """ユーザープロフィール更新のテスト"""
        # ユーザー登録
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "nickname": "testuser"
        }
        account = auth_service.register_user(user_data)
        
        # プロフィール更新
        update_data = {
            "nickname": "updateduser",
            "first_name": "Updated",
            "last_name": "Name",
            "primary_condition": "Updated Condition"
        }
        
        updated_profile = auth_service.update_user_profile(account.id, update_data)
        
        # 検証
        assert updated_profile.nickname == "updateduser"
        assert updated_profile.first_name == "Updated"
        assert updated_profile.last_name == "Name"
        assert updated_profile.primary_condition == "Updated Condition"
    
    def test_password_change(self, auth_service, db_session):
        """パスワード変更のテスト"""
        # ユーザー登録
        user_data = {
            "email": "test@example.com",
            "password": "oldpassword123",
            "nickname": "testuser"
        }
        account = auth_service.register_user(user_data)
        
        # パスワード変更
        password_change_data = {
            "old_password": "oldpassword123",
            "new_password": "newpassword123"
        }
        
        auth_service.change_password(account.id, password_change_data)
        
        # 新しいパスワードでログイン確認
        login_data = {
            "email": "test@example.com",
            "password": "newpassword123"
        }
        
        with patch('auth_service.Request') as mock_request:
            mock_request.client.host = "127.0.0.1"
            mock_request.headers = {"user-agent": "test"}
            
            response = auth_service.login_user(login_data, mock_request)
            assert response.access_token is not None
    
    def test_mfa_configuration(self, auth_service, db_session):
        """MFA設定のテスト"""
        # ユーザー登録
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "nickname": "testuser"
        }
        account = auth_service.register_user(user_data)
        
        # MFA有効化
        mfa_data = {
            "method": "email",
            "contact_info": "test@example.com"
        }
        
        auth_service.enable_mfa(account.id, mfa_data)
        
        # MFA設定の確認
        mfa_config = auth_service.get_mfa_status(account.id)
        assert mfa_config.mfa_enabled is True
        assert mfa_config.mfa_method == "email"
    
    def test_session_management(self, auth_service, db_session):
        """セッション管理のテスト"""
        # ユーザー登録とログイン
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "nickname": "testuser"
        }
        account = auth_service.register_user(user_data)
        
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        with patch('auth_service.Request') as mock_request:
            mock_request.client.host = "127.0.0.1"
            mock_request.headers = {"user-agent": "test"}
            
            login_response = auth_service.login_user(login_data, mock_request)
            
            # セッションの確認
            sessions = db_session.query(UserSession).filter(
                UserSession.account_id == account.id
            ).all()
            assert len(sessions) == 1
            assert sessions[0].is_active is True
    
    def test_logout(self, auth_service, db_session):
        """ログアウトのテスト"""
        # ユーザー登録とログイン
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "nickname": "testuser"
        }
        account = auth_service.register_user(user_data)
        
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        with patch('auth_service.Request') as mock_request:
            mock_request.client.host = "127.0.0.1"
            mock_request.headers = {"user-agent": "test"}
            
            login_response = auth_service.login_user(login_data, mock_request)
            
            # ログアウト
            auth_service.logout_user(login_response.access_token)
            
            # セッションの無効化確認
            sessions = db_session.query(UserSession).filter(
                UserSession.account_id == account.id
            ).all()
            assert len(sessions) == 1
            assert sessions[0].is_active is False


class TestAuthAPIEndpoints:
    """認証APIエンドポイントのテスト"""
    
    @pytest.fixture
    def client(self):
        """テストクライアント"""
        return TestClient(app)
    
    def test_register_endpoint(self, client):
        """ユーザー登録エンドポイントのテスト"""
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "nickname": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "primary_condition": "Test Condition"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        # 検証
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["nickname"] == "testuser"
    
    def test_login_endpoint(self, client):
        """ログインエンドポイントのテスト"""
        # ユーザー登録
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "nickname": "testuser"
        }
        client.post("/auth/register", json=user_data)
        
        # ログイン
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        # 検証
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["nickname"] == "testuser"
    
    def test_profile_endpoint(self, client):
        """プロフィールエンドポイントのテスト"""
        # ユーザー登録とログイン
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "nickname": "testuser"
        }
        register_response = client.post("/auth/register", json=user_data)
        token = register_response.json()["access_token"]
        
        # プロフィール取得
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/auth/me", headers=headers)
        
        # 検証
        assert response.status_code == 200
        data = response.json()
        assert data["nickname"] == "testuser"
    
    def test_protected_endpoint_without_auth(self, client):
        """認証なしでの保護されたエンドポイントアクセステスト"""
        response = client.get("/posts")
        
        # 開発環境では認証スルーが有効
        assert response.status_code == 200
    
    def test_health_check_endpoints(self, client):
        """ヘルスチェックエンドポイントのテスト"""
        # メインヘルスチェック
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        
        # 認証ヘルスチェック
        response = client.get("/auth/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"




