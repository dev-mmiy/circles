#!/bin/bash

# 開発環境用認証設定スクリプト

echo "🔐 開発環境認証システム起動中..."

# 環境変数設定
export DEV_AUTH_BYPASS=true
export DEV_USER_ID=1
export SECRET_KEY="dev-secret-key-change-in-production"
export DATABASE_URL="sqlite:///./test.db"
export DEBUG=true
export LOG_LEVEL=debug

echo "✅ 認証スルー機能: 有効"
echo "✅ ダミーユーザーID: 1"
echo "✅ データベース: SQLite (test.db)"
echo "✅ デバッグモード: 有効"

# 認証システム起動
echo "🚀 認証システム起動中..."
python app_auth.py


