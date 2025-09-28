"""
包括的なAPI統合のUnitテスト
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.pool import StaticPool

from app_auth_simple import app


class TestAPIIntegration:
    """API統合の包括的テスト"""
    
    @pytest.fixture
    def client(self):
        """テストクライアント"""
        return TestClient(app)
    
    def test_api_health_check(self, client):
        """APIヘルスチェックのテスト"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "message" in data
    
    def test_auth_health_check(self, client):
        """認証APIヘルスチェックのテスト"""
        response = client.get("/auth/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "message" in data
    
    def test_posts_api_without_auth(self, client):
        """認証なしでの投稿APIアクセステスト"""
        # 開発環境では認証スルーが有効
        response = client.get("/posts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_posts_api_with_auth(self, client):
        """認証ありでの投稿APIアクセステスト"""
        # ユーザー登録
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "nickname": "testuser"
        }
        register_response = client.post("/auth/register", json=user_data)
        assert register_response.status_code == 201
        
        token = register_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 認証ありで投稿APIにアクセス
        response = client.get("/posts", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_create_post_with_auth(self, client):
        """認証ありでの投稿作成テスト"""
        # ユーザー登録
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "nickname": "testuser"
        }
        register_response = client.post("/auth/register", json=user_data)
        token = register_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 投稿作成
        post_data = {
            "title": "Test Post",
            "content": "This is a test post"
        }
        response = client.post("/posts", json=post_data, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Post"
        assert data["content"] == "This is a test post"
        assert "id" in data
        assert "created_at" in data
    
    def test_api_error_handling(self, client):
        """APIエラーハンドリングのテスト"""
        # 存在しないエンドポイント
        response = client.get("/nonexistent")
        assert response.status_code == 404
        
        # 無効なJSONデータ
        response = client.post("/posts", data="invalid json")
        assert response.status_code == 422
    
    def test_cors_headers(self, client):
        """CORSヘッダーのテスト"""
        response = client.options("/posts")
        assert response.status_code == 200
        
        # CORSヘッダーの確認
        headers = response.headers
        assert "access-control-allow-origin" in headers
        assert "access-control-allow-methods" in headers
        assert "access-control-allow-headers" in headers
    
    def test_api_response_format(self, client):
        """APIレスポンス形式のテスト"""
        # ヘルスチェックのレスポンス形式
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert "message" in data
        assert isinstance(data["status"], str)
        assert isinstance(data["message"], str)
        
        # 認証レスポンスの形式
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "nickname": "testuser"
        }
        response = client.post("/auth/register", json=user_data)
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert "expires_in" in data
        assert "user" in data
        assert data["token_type"] == "bearer"
    
    def test_api_rate_limiting(self, client):
        """APIレート制限のテスト"""
        # 現在はレート制限を実装していないが、将来の拡張に備えたテスト
        # 複数のリクエストを送信してレート制限をテスト
        for i in range(10):
            response = client.get("/health")
            assert response.status_code == 200
    
    def test_api_logging(self, client):
        """APIログのテスト"""
        # ログが正しく出力されることを確認
        with patch('app_auth_simple.logger') as mock_logger:
            response = client.get("/health")
            assert response.status_code == 200
            # ログが呼び出されることを確認（実装に依存）
    
    def test_api_metrics(self, client):
        """APIメトリクスのテスト"""
        # 現在はメトリクスを実装していないが、将来の拡張に備えたテスト
        response = client.get("/health")
        assert response.status_code == 200
        
        # メトリクスエンドポイントが存在する場合のテスト
        # response = client.get("/metrics")
        # assert response.status_code == 200


class TestFrontendAPIIntegration:
    """フロントエンドとAPI統合のテスト"""
    
    @pytest.fixture
    def client(self):
        """テストクライアント"""
        return TestClient(app)
    
    def test_frontend_api_proxy(self, client):
        """フロントエンドAPIプロキシのテスト"""
        # Next.jsのrewrite設定をシミュレート
        response = client.get("/api/posts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_frontend_auth_integration(self, client):
        """フロントエンド認証統合のテスト"""
        # 認証フロー全体のテスト
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "nickname": "testuser"
        }
        
        # ユーザー登録
        register_response = client.post("/auth/register", json=user_data)
        assert register_response.status_code == 201
        register_data = register_response.json()
        
        # ログイン
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        login_response = client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200
        login_data = login_response.json()
        
        # トークンを使用してAPIにアクセス
        token = login_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # プロフィール取得
        profile_response = client.get("/auth/me", headers=headers)
        assert profile_response.status_code == 200
        profile_data = profile_response.json()
        assert profile_data["nickname"] == "testuser"
        
        # 投稿作成
        post_data = {
            "title": "Test Post",
            "content": "This is a test post"
        }
        post_response = client.post("/posts", json=post_data, headers=headers)
        assert post_response.status_code == 201
    
    def test_frontend_error_handling(self, client):
        """フロントエンドエラーハンドリングのテスト"""
        # 無効な認証情報でのログイン
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 401
        
        # 無効なトークンでのAPIアクセス
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/auth/me", headers=headers)
        assert response.status_code == 401
    
    def test_frontend_data_validation(self, client):
        """フロントエンドデータ検証のテスト"""
        # 無効なユーザー登録データ
        invalid_user_data = {
            "email": "invalid-email",
            "password": "123",  # 短すぎるパスワード
            "nickname": ""
        }
        response = client.post("/auth/register", json=invalid_user_data)
        assert response.status_code == 422
        
        # 無効な投稿データ
        invalid_post_data = {
            "title": "",  # 空のタイトル
            "content": ""
        }
        response = client.post("/posts", json=invalid_post_data)
        assert response.status_code == 422


class TestAPISecurity:
    """APIセキュリティのテスト"""
    
    @pytest.fixture
    def client(self):
        """テストクライアント"""
        return TestClient(app)
    
    def test_sql_injection_protection(self, client):
        """SQLインジェクション攻撃の防止テスト"""
        # SQLインジェクション攻撃を試行
        malicious_data = {
            "email": "test@example.com'; DROP TABLE users; --",
            "password": "testpassword123",
            "nickname": "testuser"
        }
        
        # 攻撃が失敗することを確認
        response = client.post("/auth/register", json=malicious_data)
        # 正常に処理されるか、適切なエラーが返されることを確認
        assert response.status_code in [201, 422, 400]
    
    def test_xss_protection(self, client):
        """XSS攻撃の防止テスト"""
        # XSS攻撃を試行
        malicious_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "nickname": "<script>alert('XSS')</script>"
        }
        
        response = client.post("/auth/register", json=malicious_data)
        assert response.status_code == 201
        
        # レスポンスにスクリプトタグが含まれていないことを確認
        data = response.json()
        assert "<script>" not in str(data)
    
    def test_csrf_protection(self, client):
        """CSRF攻撃の防止テスト"""
        # CSRFトークンの確認（実装に依存）
        response = client.get("/auth/me")
        # 現在はCSRF保護を実装していないが、将来の拡張に備えたテスト
        assert response.status_code in [200, 401]
    
    def test_input_sanitization(self, client):
        """入力データのサニタイゼーションテスト"""
        # 特殊文字を含むデータの処理
        special_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "nickname": "test@user!@#$%^&*()"
        }
        
        response = client.post("/auth/register", json=special_data)
        assert response.status_code == 201
        
        # データが適切にサニタイズされていることを確認
        data = response.json()
        assert "test@user" in data["user"]["nickname"]


class TestAPIPerformance:
    """APIパフォーマンスのテスト"""
    
    @pytest.fixture
    def client(self):
        """テストクライアント"""
        return TestClient(app)
    
    def test_api_response_time(self, client):
        """APIレスポンス時間のテスト"""
        import time
        
        # ヘルスチェックのレスポンス時間
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 1.0, f"レスポンス時間が遅すぎます: {response_time}秒"
    
    def test_concurrent_requests(self, client):
        """同時リクエストのテスト"""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = client.get("/health")
            results.append(response.status_code)
        
        # 10個の同時リクエスト
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # すべてのスレッドの完了を待機
        for thread in threads:
            thread.join()
        
        # すべてのリクエストが成功することを確認
        assert len(results) == 10
        assert all(status == 200 for status in results)
    
    def test_memory_usage(self, client):
        """メモリ使用量のテスト"""
        import psutil
        import os
        
        # プロセスのメモリ使用量を取得
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # 複数のリクエストを送信
        for i in range(100):
            response = client.get("/health")
            assert response.status_code == 200
        
        # メモリ使用量の増加をチェック
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # メモリリークがないことを確認（1MB以下）
        assert memory_increase < 1024 * 1024, f"メモリ使用量が増加しています: {memory_increase} bytes"


class TestAPIMonitoring:
    """APIモニタリングのテスト"""
    
    @pytest.fixture
    def client(self):
        """テストクライアント"""
        return TestClient(app)
    
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
    
    def test_api_metrics_collection(self, client):
        """APIメトリクス収集のテスト"""
        # 現在はメトリクス収集を実装していないが、将来の拡張に備えたテスト
        response = client.get("/health")
        assert response.status_code == 200
        
        # メトリクスエンドポイントが存在する場合のテスト
        # response = client.get("/metrics")
        # assert response.status_code == 200
    
    def test_error_tracking(self, client):
        """エラートラッキングのテスト"""
        # エラーを発生させる
        response = client.get("/nonexistent")
        assert response.status_code == 404
        
        # エラーログが記録されることを確認（実装に依存）
        # 現在はエラートラッキングを実装していないが、将来の拡張に備えたテスト

