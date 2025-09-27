# データベースマイグレーション管理

このドキュメントでは、ヘルスケアコミュニティプラットフォームのデータベースマイグレーション管理について説明します。

## 概要

このプロジェクトでは、Alembicを使用したデータベースマイグレーション管理システムを実装しています。国際化対応のデータベーススキーマを効率的に管理できます。

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements_migration.txt
```

### 2. データベースの初期化

```bash
python migrate.py setup
```

このコマンドは以下を実行します：
- データベーステーブルの作成
- Alembicマイグレーションの初期化
- 初期マイグレーションの作成
- シードデータの投入

## 使用方法

### 基本的なコマンド

#### データベースのセットアップ
```bash
python migrate.py setup
```

#### データベースのアップグレード
```bash
python migrate.py upgrade
```

#### データベースのダウングレード
```bash
python migrate.py downgrade <revision>
```

#### ステータスの確認
```bash
python migrate.py status
```

#### マイグレーション履歴の表示
```bash
python migrate.py history
```

#### 新しいマイグレーションの作成
```bash
python migrate.py create "Add new feature"
```

#### データベースのリセット（注意：全データが削除されます）
```bash
python migrate.py reset
```

#### シードデータの投入
```bash
python migrate.py seed
```

#### データベースのバックアップ
```bash
python migrate.py backup backup.db
```

#### データベースの復元
```bash
python migrate.py restore backup.db
```

### 環境変数

#### DATABASE_URL
データベース接続URLを指定します。

```bash
# SQLite（デフォルト）
export DATABASE_URL="sqlite:///./app_i18n.db"

# PostgreSQL
export DATABASE_URL="postgresql://user:password@localhost:5432/healthcare_db"

# MySQL
export DATABASE_URL="mysql+pymysql://user:password@localhost:3306/healthcare_db"
```

## マイグレーション管理

### マイグレーションファイルの構造

```
migrations/
├── env.py              # Alembic環境設定
├── script.py.mako      # マイグレーションスクリプトテンプレート
└── versions/           # マイグレーションファイル
    ├── 0001_initial_migration.py
    ├── 0002_add_i18n_support.py
    └── ...
```

### 新しいマイグレーションの作成

1. モデルを変更
2. マイグレーションを作成：
   ```bash
   python migrate.py create "Add new feature"
   ```
3. マイグレーションファイルを確認・編集
4. マイグレーションを適用：
   ```bash
   python migrate.py upgrade
   ```

### マイグレーションの確認

```bash
# 現在のステータス
python migrate.py status

# マイグレーション履歴
python migrate.py history
```

## 国際化対応

### サポート言語

- 英語 (en)
- 日本語 (ja)
- 中国語簡体字 (zh-CN)
- 中国語繁体字 (zh-TW)
- 韓国語 (ko)
- スペイン語 (es)
- フランス語 (fr)
- ドイツ語 (de)
- イタリア語 (it)
- ポルトガル語 (pt)
- ロシア語 (ru)
- アラビア語 (ar)
- ヒンディー語 (hi)

### サポート国・地域

- アメリカ合衆国 (US)
- 日本 (JP)
- 中国 (CN)
- 韓国 (KR)
- イギリス (GB)
- カナダ (CA)
- オーストラリア (AU)
- ドイツ (DE)
- フランス (FR)
- スペイン (ES)
- イタリア (IT)
- ブラジル (BR)
- インド (IN)
- ロシア (RU)
- サウジアラビア (SA)

## シードデータ

初期データとして以下が投入されます：

### 言語データ
- サポート言語の一覧
- ネイティブ名
- RTL（右から左）言語の設定

### 国・地域データ
- 国名（多言語）
- タイムゾーン
- 通貨
- 日付フォーマット
- 単位系

### 翻訳名前空間
- UI要素
- 医療用語
- コミュニティ機能
- 研究用語
- バリデーション
- エラーメッセージ

### ユーザーロール
- メンバー
- 医療従事者
- 治験コーディネーター
- モデレーター
- 管理者

### 同意スコープ
- 研究データ利用
- 治験紹介
- コミュニティ共有
- データエクスポート

## トラブルシューティング

### よくある問題

#### 1. マイグレーションが適用されない
```bash
# 現在のステータスを確認
python migrate.py status

# 手動でアップグレード
python migrate.py upgrade
```

#### 2. データベースが初期化されていない
```bash
# データベースをセットアップ
python migrate.py setup
```

#### 3. マイグレーション履歴が表示されない
```bash
# マイグレーションを初期化
python migrate.py setup
```

#### 4. シードデータが投入されていない
```bash
# シードデータを投入
python migrate.py seed
```

### ログの確認

```bash
# 詳細なログを有効にする
export PYTHONPATH=.
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from migration_manager import MigrationManager
manager = MigrationManager()
manager.upgrade_database()
"
```

## 本番環境での使用

### 1. データベースのバックアップ
```bash
python migrate.py backup production_backup.db
```

### 2. マイグレーションの適用
```bash
python migrate.py upgrade
```

### 3. ロールバック（必要に応じて）
```bash
python migrate.py downgrade <previous_revision>
```

### 4. データベースの復元
```bash
python migrate.py restore production_backup.db
```

## 開発環境での使用

### 1. 開発用データベースのセットアップ
```bash
export DATABASE_URL="sqlite:///./dev.db"
python migrate.py setup
```

### 2. テスト用データベースのリセット
```bash
python migrate.py reset
```

### 3. 新しい機能のマイグレーション
```bash
# モデルを変更後
python migrate.py create "Add new feature"
python migrate.py upgrade
```

## 注意事項

1. **本番環境でのリセットは避ける**: `migrate.py reset`は全データを削除します
2. **バックアップの取得**: 重要な変更前には必ずバックアップを取得してください
3. **マイグレーションの順序**: マイグレーションは順序通りに適用されます
4. **データの整合性**: マイグレーション後はデータの整合性を確認してください

## サポート

問題が発生した場合は、以下を確認してください：

1. データベース接続設定
2. マイグレーション履歴
3. ログファイル
4. データベースの状態

詳細な情報が必要な場合は、ログレベルをDEBUGに設定して実行してください。
