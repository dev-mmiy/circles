#!/bin/bash

# 本格認証システム起動スクリプト

echo "🔐 本格認証システム起動中..."

# 環境変数設定
export DEV_AUTH_BYPASS=false
export SECRET_KEY="production-secret-key-change-in-production"
export DATABASE_URL="sqlite:///./test.db"
export DEBUG=false
export LOG_LEVEL=info

echo "✅ 認証スルー機能: 無効"
echo "✅ 本格認証: 有効"
echo "✅ データベース: SQLite (test.db)"
echo "✅ デバッグモード: 無効"

# 認証システム起動
echo "🚀 認証システム起動中..."
python app_auth.py



