# 🔐 認証システム

疾患を抱える消費者向けの認証システムの実装ドキュメント

## 📋 概要

この認証システムは、数万から数十万のユーザーをサポートし、疾患を抱える消費者向けに設計されています。

### 主な機能

- **ユーザー登録・ログイン**: メールアドレスとパスワードによる認証
- **JWT認証**: セキュアなトークンベース認証
- **パスワードハッシュ**: bcryptによる安全なパスワード保存
- **セッション管理**: 複数デバイス対応のセッション管理
- **開発環境スルー**: 開発時の認証スルー機能
- **国際化対応**: 多言語サポート
- **アクセシビリティ**: 疾患を考慮したUI/UX

## 🏗️ アーキテクチャ

### バックエンド

```
auth_models.py          # 認証関連のSQLModel定義
auth_service.py         # 認証ビジネスロジック
auth_endpoints.py       # 認証APIエンドポイント
auth_middleware.py      # 認証ミドルウェア
app_auth.py            # 認証統合FastAPIアプリ
```

### フロントエンド

```
src/components/auth/     # 認証UIコンポーネント
src/hooks/useAuth.ts    # 認証フック
src/app/[locale]/auth/  # 認証ページ
```

## 🚀 セットアップ

### 1. 依存関係のインストール

```bash
# バックエンド依存関係
pip install -r requirements.txt

# フロントエンド依存関係
npm install
```

### 2. 環境変数設定

```bash
# 認証設定
export SECRET_KEY="your-secret-key-here"
export DEV_AUTH_BYPASS="true"  # 開発環境用
export DEV_USER_ID="1"

# データベース設定
export DATABASE_URL="postgresql://healthcare_user:healthcare_password@localhost:5432/healthcare_db"
```

### 3. データベースセットアップ

```bash
# データベーススキーマ作成
python -c "from app_auth import app; from sqlmodel import SQLModel, create_engine; SQLModel.metadata.create_all(create_engine('postgresql://healthcare_user:healthcare_password@localhost:5432/healthcare_db'))"
```

### 4. アプリケーション起動

```bash
# バックエンド起動
python app_auth.py

# フロントエンド起動
npm run dev
```

## 🔧 開発環境での認証スルー

開発環境では、認証をスルーしてテストできる機能があります：

```python
# 環境変数で有効化
DEV_AUTH_BYPASS=true
DEV_USER_ID=1

# ダミーユーザーで自動ログイン
```

## 📊 データベーススキーマ

### 認証関連テーブル

```sql
-- アカウント基本情報
CREATE TABLE core.account (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending_verification',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login_at TIMESTAMP,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP
);

-- ユーザープロフィール
CREATE TABLE core.user_profile (
    account_id INTEGER PRIMARY KEY REFERENCES core.account(id),
    nickname VARCHAR(100),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    date_of_birth DATE,
    gender VARCHAR(20),
    phone VARCHAR(20),
    timezone VARCHAR(50) DEFAULT 'UTC',
    language VARCHAR(10) DEFAULT 'en-US',
    country VARCHAR(10) DEFAULT 'US',
    primary_condition VARCHAR(200),
    conditions JSONB,
    medications JSONB,
    emergency_contact JSONB,
    privacy_level VARCHAR(20) DEFAULT 'private',
    share_medical_info BOOLEAN DEFAULT FALSE,
    accessibility_needs JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ユーザーセッション
CREATE TABLE core.user_session (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id INTEGER REFERENCES core.account(id),
    session_token VARCHAR(255) UNIQUE NOT NULL,
    refresh_token VARCHAR(255) UNIQUE NOT NULL,
    device_info JSONB,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    last_activity_at TIMESTAMP DEFAULT NOW()
);
```

## 🔌 APIエンドポイント

### 認証エンドポイント

```http
POST /auth/register          # ユーザー登録
POST /auth/login            # ユーザーログイン
POST /auth/refresh          # トークンリフレッシュ
POST /auth/logout           # ユーザーログアウト
GET  /auth/me              # 現在のユーザー情報取得
PUT  /auth/me              # ユーザープロフィール更新
GET  /auth/health          # 認証サービスヘルスチェック
```

### 保護されたエンドポイント

```http
GET    /posts              # 投稿一覧（認証必須）
POST   /posts              # 投稿作成（認証必須）
GET    /posts/{id}         # 投稿詳細（認証必須）
PUT    /posts/{id}         # 投稿更新（認証必須）
DELETE /posts/{id}         # 投稿削除（認証必須）
GET    /user/posts         # ユーザーの投稿一覧（認証必須）
```

## 🧪 テスト

### 認証システムのテスト実行

```bash
# 認証テスト実行
python -m pytest test_auth.py -v

# 特定のテスト実行
python -m pytest test_auth.py::TestAuthSystem::test_user_registration -v
```

### テストカバレッジ

```bash
# カバレッジ付きテスト実行
python -m pytest test_auth.py --cov=auth_service --cov=auth_endpoints
```

## 🔒 セキュリティ機能

### パスワードセキュリティ

- **bcryptハッシュ**: パスワードの安全な保存
- **ソルト**: レインボーテーブル攻撃対策
- **強度チェック**: パスワード強度の検証

### アカウント保護

- **ログイン試行制限**: 5回失敗で30分ロック
- **セッション管理**: 複数デバイス対応
- **トークン有効期限**: アクセストークン30分、リフレッシュトークン30日

### 開発環境セキュリティ

- **認証スルー**: 開発時の認証バイパス
- **ダミーユーザー**: テスト用ユーザー情報
- **環境分離**: 本番環境との分離

## 🌐 国際化対応

### サポート言語

- **英語 (en-US)**: デフォルト言語
- **日本語 (ja-JP)**: 日本向け
- **フランス語 (fr-FR)**: フランス向け

### 翻訳キー

```json
{
  "auth": {
    "login": {
      "title": "Sign In",
      "description": "Sign in to your account to access the community"
    },
    "register": {
      "title": "Create Account",
      "description": "Join our community to connect with others"
    }
  }
}
```

## 🚀 本番環境デプロイ

### 環境変数設定

```bash
# 本番環境設定
export DEV_AUTH_BYPASS="false"
export SECRET_KEY="your-production-secret-key"
export DATABASE_URL="postgresql://user:password@host:port/database"
```

### セキュリティチェックリスト

- [ ] 強力なSECRET_KEYの設定
- [ ] データベース接続の暗号化
- [ ] HTTPSの有効化
- [ ] 認証スルー機能の無効化
- [ ] ログ監視の設定
- [ ] セッションタイムアウトの設定

## 📈 パフォーマンス最適化

### データベース最適化

- **インデックス**: メールアドレス、セッショントークン
- **接続プール**: データベース接続の効率化
- **クエリ最適化**: N+1問題の回避

### キャッシュ戦略

- **セッションキャッシュ**: Redis活用
- **ユーザー情報キャッシュ**: 頻繁なアクセス情報
- **トークンキャッシュ**: 認証状態の高速化

## 🔧 トラブルシューティング

### よくある問題

1. **認証エラー**: トークンの有効期限切れ
2. **データベース接続エラー**: 接続文字列の確認
3. **開発環境スルー**: 環境変数の設定確認

### ログ確認

```bash
# アプリケーションログ
tail -f logs/app.log

# データベースログ
tail -f logs/database.log
```

## 📚 参考資料

- [FastAPI認証ガイド](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT認証ベストプラクティス](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/)
- [bcryptパスワードハッシュ](https://passlib.readthedocs.io/en/stable/lib/passlib.hash.bcrypt.html)
- [SQLModel認証統合](https://sqlmodel.tiangolo.com/tutorial/fastapi/authentication/)

## 🤝 コントリビューション

認証システムの改善や新機能の追加については、以下の手順でお願いします：

1. フィーチャーブランチの作成
2. 認証テストの追加
3. セキュリティレビューの実施
4. プルリクエストの作成

## 📄 ライセンス

この認証システムは、Healthcare Community Platformの一部として開発されています。
