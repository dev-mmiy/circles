# 開発環境用テストアカウント情報

## 🔐 認証スルー機能（推奨）

開発環境では認証スルー機能が有効になっています：

```bash
export DEV_AUTH_BYPASS=true
export DEV_USER_ID=1
```

この設定により、認証なしでシステムにアクセスできます。

## 🧪 テスト用アカウント（手動作成時）

認証システムが正常に動作する場合のテストアカウント情報：

### 1. テストユーザー
- **Email**: `test@example.com`
- **Password**: `test123`
- **Nickname**: `testuser`
- **Role**: `patient`

### 2. 管理者アカウント
- **Email**: `admin@example.com`
- **Password**: `admin123`
- **Nickname**: `admin`
- **Role**: `admin`

### 3. 患者アカウント
- **Email**: `patient@example.com`
- **Password**: `patient123`
- **Nickname**: `patient`
- **Role**: `patient`

### 4. 医師アカウント
- **Email**: `doctor@example.com`
- **Password**: `doctor123`
- **Nickname**: `doctor`
- **Role**: `doctor`

## 🚀 使用方法

### 認証スルー機能を使用する場合
1. 環境変数を設定：
   ```bash
   export DEV_AUTH_BYPASS=true
   export DEV_USER_ID=1
   ```

2. フロントエンドにアクセス：
   ```
   http://localhost:3000/en-US/auth
   ```

3. 認証なしでシステムにアクセスできます

### 手動でアカウントを作成する場合
1. フロントエンドの登録ページにアクセス：
   ```
   http://localhost:3000/en-US/auth?mode=register
   ```

2. 上記のテストアカウント情報を使用して登録

## 📝 注意事項

- 開発環境でのみ使用してください
- 本番環境では認証スルー機能を無効にしてください
- パスワードは開発用の簡単なものなので、本番環境では強力なパスワードを使用してください

## 🔧 トラブルシューティング

認証システムで問題が発生した場合：

1. **認証スルー機能を使用**：
   ```bash
   export DEV_AUTH_BYPASS=true
   export DEV_USER_ID=1
   ```

2. **バックエンドを再起動**：
   ```bash
   python app_auth_simple.py
   ```

3. **フロントエンドを再起動**：
   ```bash
   npm run dev
   ```



