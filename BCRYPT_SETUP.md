# bcrypt 4.x 初期設定ガイド

## 🔧 概要

このプロジェクトでは、bcrypt 4.xの新しいバージョンを使用してパスワードハッシュ化を行います。bcrypt 4.xは以下の利点があります：

- **互換性の向上**: passlibとの互換性が改善
- **パフォーマンス向上**: より効率的なハッシュ化
- **セキュリティ強化**: 最新のセキュリティ標準に対応

## 📦 インストール

### 1. 自動インストール

```bash
# 初期設定スクリプトを実行
python setup_bcrypt.py
```

### 2. 手動インストール

```bash
# 古いバージョンをアンインストール
pip uninstall bcrypt -y

# bcrypt 4.xをインストール
pip install "bcrypt>=4.0.1,<5.0.0"

# passlibを再インストール
pip install --upgrade "passlib[bcrypt]==1.7.4"
```

## 🐳 Docker環境での設定

### Dockerfile
```dockerfile
# bcrypt 4.xの確実なインストール
RUN pip3 uninstall bcrypt -y || true
RUN pip3 install "bcrypt>=4.0.1,<5.0.0"
RUN pip3 install --upgrade "passlib[bcrypt]==1.7.4"
```

### docker-compose.yml
```yaml
services:
  backend:
    build: .
    environment:
      - BCRYPT_ROUNDS=12
```

## ⚙️ 設定

### 認証サービス設定

```python
from passlib.context import CryptContext

# bcrypt 4.x対応の設定
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__default_rounds=12,
    bcrypt__min_rounds=10,
    bcrypt__max_rounds=15
)
```

### パスワードハッシュ化

```python
def create_password_hash(self, password: str) -> str:
    """パスワードハッシュ作成（bcrypt 4.x対応）"""
    try:
        # パスワードが72バイトを超える場合は事前にSHA256でハッシュ化
        if len(password.encode('utf-8')) > 72:
            password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
            return pwd_context.hash(password_hash)
        else:
            return pwd_context.hash(password)
    except Exception as e:
        print(f"パスワードハッシュ化エラー: {e}")
        # フォールバック: SHA256でハッシュ化
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        return pwd_context.hash(password_hash)
```

## 🧪 テスト

### 互換性テスト

```bash
# bcrypt互換性テストを実行
python -c "
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
test_password = 'test1234'
hashed = pwd_context.hash(test_password)
verified = pwd_context.verify(test_password, hashed)
print(f'✅ bcrypt動作確認: ハッシュ化={bool(hashed)}, 検証={verified}')
"
```

### 認証システムテスト

```bash
# 認証システムのテスト
export DEV_AUTH_BYPASS=false
export SECRET_KEY="test-secret-key"
export DATABASE_URL="sqlite:///./test.db"
python -c "
from auth_service import AuthService
from sqlmodel import Session, create_engine
from auth_models import UserRegister, UserLogin

engine = create_engine('sqlite:///./test.db')
with Session(engine) as session:
    auth_service = AuthService(session)
    
    # ユーザー登録テスト
    user_data = UserRegister(
        email='test@example.com',
        password='test1234',
        nickname='Test User',
        first_name='Test',
        last_name='User',
        primary_condition='Test Condition'
    )
    
    result = auth_service.register_user(user_data)
    print(f'✅ ユーザー登録成功: Account ID {result.user.account_id}')
    
    # ログインテスト
    login_data = UserLogin(email='test@example.com', password='test1234')
    login_result = auth_service.login_user(login_data)
    print(f'✅ ログイン成功: {login_result.access_token[:20]}...')
"
```

## 🔍 トラブルシューティング

### よくある問題

1. **bcryptバージョン互換性エラー**
   ```
   AttributeError: module 'bcrypt' has no attribute '__about__'
   ```
   **解決方法**: bcrypt 4.xをインストール
   ```bash
   pip uninstall bcrypt -y
   pip install "bcrypt>=4.0.1,<5.0.0"
   ```

2. **パスワード長制限エラー**
   ```
   password cannot be longer than 72 bytes
   ```
   **解決方法**: 長いパスワードは事前にSHA256でハッシュ化

3. **passlib互換性エラー**
   ```
   (trapped) error reading bcrypt version
   ```
   **解決方法**: passlibを再インストール
   ```bash
   pip install --upgrade "passlib[bcrypt]==1.7.4"
   ```

### ログ確認

```bash
# 認証ログを確認
tail -f logs/auth.log

# エラーログを確認
tail -f logs/error.log
```

## 📋 環境変数

```bash
# bcrypt設定
export BCRYPT_ROUNDS=12
export BCRYPT_MIN_ROUNDS=10
export BCRYPT_MAX_ROUNDS=15

# 認証設定
export SECRET_KEY="your-secret-key"
export DEV_AUTH_BYPASS=false
export DATABASE_URL="sqlite:///./test.db"
```

## 🚀 本番環境での注意事項

1. **セキュリティキーの変更**
   ```bash
   export SECRET_KEY="your-production-secret-key"
   ```

2. **bcryptラウンド数の調整**
   ```bash
   export BCRYPT_ROUNDS=15  # より高いセキュリティ
   ```

3. **データベースの設定**
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost/dbname"
   ```

## 📚 参考資料

- [bcrypt 4.x Documentation](https://github.com/pyca/bcrypt)
- [passlib Documentation](https://passlib.readthedocs.io/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

## 🔄 アップデート手順

1. 古いバージョンをアンインストール
2. 新しいバージョンをインストール
3. 設定ファイルを更新
4. テストを実行
5. 本番環境にデプロイ

```bash
# アップデートスクリプト
python setup_bcrypt.py
```

