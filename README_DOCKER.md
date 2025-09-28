# Docker環境構築ガイド

このドキュメントでは、ヘルスケアコミュニティプラットフォームのDocker環境構築について説明します。

## 概要

Docker Composeを使用して、以下のサービスを統合した開発・本番環境を構築します：

- **PostgreSQL** - メインデータベース
- **Redis** - キャッシュ・セッション管理
- **Backend API** - FastAPI アプリケーション
- **Frontend** - Next.js アプリケーション
- **Nginx** - リバースプロキシ
- **Prometheus** - 監視（オプション）
- **Grafana** - ダッシュボード（オプション）

## 前提条件

- Docker 20.10+
- Docker Compose 2.0+
- 8GB以上のRAM
- 20GB以上のディスク容量

## セットアップ

### 1. 環境変数の設定

```bash
# 環境変数ファイルをコピー
cp env.example .env

# 必要な値を設定
nano .env
```

重要な設定項目：

```bash
# データベース
DATABASE_URL=postgresql://healthcare_user:healthcare_password@postgres:5432/healthcare_db

# AI機能（OpenAI APIキー）
OPENAI_API_KEY=your-openai-api-key-here

# セキュリティ
SECRET_KEY=your-secret-key-here-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-here

# 本番環境
PRODUCTION_MODE=false
SSL_ENABLED=false
```

### 2. 開発環境の起動

```bash
# 開発環境を起動
docker-compose --profile dev up -d

# ログを確認
docker-compose logs -f
```

### 3. 本番環境の起動

```bash
# 本番環境を起動
docker-compose up -d

# データベースマイグレーション
docker-compose run --rm migration

# サービス状態を確認
docker-compose ps
```

## サービス構成

### データベース（PostgreSQL）

```yaml
postgres:
  image: postgres:15-alpine
  environment:
    POSTGRES_DB: healthcare_db
    POSTGRES_USER: healthcare_user
    POSTGRES_PASSWORD: healthcare_password
  volumes:
    - postgres_data:/var/lib/postgresql/data
  ports:
    - "5432:5432"
```

**接続情報：**
- ホスト: localhost
- ポート: 5432
- データベース: healthcare_db
- ユーザー: healthcare_user
- パスワード: healthcare_password

### キャッシュ（Redis）

```yaml
redis:
  image: redis:7-alpine
  command: redis-server --appendonly yes
  volumes:
    - redis_data:/data
  ports:
    - "6379:6379"
```

**接続情報：**
- ホスト: localhost
- ポート: 6379
- パスワード: なし

### バックエンドAPI

```yaml
backend:
  build:
    context: .
    dockerfile: Dockerfile
  environment:
    - DATABASE_URL=postgresql://healthcare_user:healthcare_password@postgres:5432/healthcare_db
    - REDIS_URL=redis://redis:6379
  ports:
    - "8000:8000"
```

**アクセス情報：**
- URL: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### フロントエンド

```yaml
frontend:
  build:
    context: .
    dockerfile: Dockerfile.frontend
  environment:
    - NEXT_PUBLIC_API_URL=http://localhost:8000
  ports:
    - "3000:3000"
```

**アクセス情報：**
- URL: http://localhost:3000
- 開発モード: ホットリロード対応

### リバースプロキシ（Nginx）

```yaml
nginx:
  image: nginx:alpine
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
  ports:
    - "80:80"
    - "443:443"
```

**アクセス情報：**
- HTTP: http://localhost
- HTTPS: https://localhost（SSL設定時）

## 開発ワークフロー

### 1. 開発環境での作業

```bash
# 開発環境を起動
docker-compose --profile dev up -d

# バックエンドのログを確認
docker-compose logs -f dev-backend

# フロントエンドのログを確認
docker-compose logs -f frontend

# データベースに接続
docker-compose exec postgres psql -U healthcare_user -d healthcare_db
```

### 2. コードの変更

```bash
# バックエンドコードを変更
# ホットリロードで自動反映

# フロントエンドコードを変更
# ホットリロードで自動反映
```

### 3. データベースマイグレーション

```bash
# マイグレーションを実行
docker-compose run --rm migration

# マイグレーション履歴を確認
docker-compose run --rm migration python migrate.py history

# データベースをリセット
docker-compose run --rm migration python migrate.py reset
```

### 4. テストの実行

```bash
# バックエンドテスト
docker-compose exec backend pytest

# フロントエンドテスト
docker-compose exec frontend npm test

# 統合テスト
docker-compose exec backend python -m pytest tests/integration/
```

## 本番デプロイ

### 1. 本番環境の準備

```bash
# 環境変数を本番用に設定
export PRODUCTION_MODE=true
export SSL_ENABLED=true
export DEBUG=false

# 本番環境を起動
docker-compose up -d
```

### 2. SSL証明書の設定

```bash
# SSL証明書を配置
mkdir -p ssl
cp your-cert.pem ssl/cert.pem
cp your-key.pem ssl/key.pem

# Nginx設定を更新
nano nginx.conf
```

### 3. 監視の設定

```bash
# 監視サービスを起動
docker-compose --profile monitoring up -d

# Prometheus: http://localhost:9090
# Grafana: http://localhost:3001
```

## トラブルシューティング

### よくある問題

#### 1. データベース接続エラー

```bash
# データベースの状態を確認
docker-compose exec postgres pg_isready -U healthcare_user

# データベースログを確認
docker-compose logs postgres

# データベースを再起動
docker-compose restart postgres
```

#### 2. メモリ不足

```bash
# メモリ使用量を確認
docker stats

# 不要なコンテナを停止
docker-compose stop unused-service

# メモリ制限を設定
docker-compose up -d --scale backend=1
```

#### 3. ポート競合

```bash
# 使用中のポートを確認
netstat -tulpn | grep :8000

# ポートを変更
# docker-compose.yml で ports を変更
```

#### 4. ボリュームの問題

```bash
# ボリュームを確認
docker volume ls

# ボリュームを削除（注意：データが失われます）
docker-compose down -v

# ボリュームを再作成
docker-compose up -d
```

### ログの確認

```bash
# 全サービスのログ
docker-compose logs

# 特定のサービスのログ
docker-compose logs backend

# リアルタイムログ
docker-compose logs -f backend

# エラーログのみ
docker-compose logs --tail=100 backend | grep ERROR
```

### パフォーマンスの最適化

#### 1. リソース制限の設定

```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'
```

#### 2. キャッシュの最適化

```yaml
# docker-compose.yml
services:
  redis:
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
```

#### 3. データベースの最適化

```yaml
# docker-compose.yml
services:
  postgres:
    environment:
      POSTGRES_SHARED_BUFFERS: 256MB
      POSTGRES_EFFECTIVE_CACHE_SIZE: 1GB
      POSTGRES_WORK_MEM: 4MB
```

## バックアップとリストア

### 1. データベースのバックアップ

```bash
# バックアップを作成
docker-compose exec postgres pg_dump -U healthcare_user healthcare_db > backup.sql

# バックアップをリストア
docker-compose exec -T postgres psql -U healthcare_user healthcare_db < backup.sql
```

### 2. ボリュームのバックアップ

```bash
# ボリュームをバックアップ
docker run --rm -v healthcare_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .

# ボリュームをリストア
docker run --rm -v healthcare_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /data
```

### 3. 自動バックアップ

```bash
# バックアップスクリプトを作成
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U healthcare_user healthcare_db > "backup_${DATE}.sql"
find . -name "backup_*.sql" -mtime +7 -delete
EOF

chmod +x backup.sh

# 定期実行を設定
crontab -e
# 0 2 * * * /path/to/backup.sh
```

## セキュリティ

### 1. 環境変数の管理

```bash
# 機密情報を環境変数で管理
export SECRET_KEY=$(openssl rand -hex 32)
export JWT_SECRET_KEY=$(openssl rand -hex 32)

# .envファイルを保護
chmod 600 .env
```

### 2. ネットワークの分離

```yaml
# docker-compose.yml
networks:
  healthcare_network:
    driver: bridge
    internal: false
  healthcare_internal:
    driver: bridge
    internal: true
```

### 3. リソース制限

```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
```

## 監視とログ

### 1. ヘルスチェック

```bash
# サービス状態を確認
docker-compose ps

# ヘルスチェックを実行
curl http://localhost:8000/health
curl http://localhost:3000
```

### 2. メトリクス収集

```bash
# Prometheusを起動
docker-compose --profile monitoring up -d

# メトリクスを確認
curl http://localhost:9090/metrics
```

### 3. ログ管理

```bash
# ログローテーションを設定
# docker-compose.yml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## スケーリング

### 1. 水平スケーリング

```bash
# バックエンドをスケール
docker-compose up -d --scale backend=3

# フロントエンドをスケール
docker-compose up -d --scale frontend=2
```

### 2. ロードバランシング

```yaml
# nginx.conf
upstream backend {
    server backend_1:8000;
    server backend_2:8000;
    server backend_3:8000;
}
```

## メンテナンス

### 1. 定期メンテナンス

```bash
# 不要なイメージを削除
docker system prune -a

# ボリュームをクリーンアップ
docker volume prune

# ネットワークをクリーンアップ
docker network prune
```

### 2. アップデート

```bash
# イメージを更新
docker-compose pull

# サービスを再起動
docker-compose up -d

# データベースマイグレーション
docker-compose run --rm migration
```

## サポート

問題が発生した場合は、以下を確認してください：

1. ログファイルの確認
2. リソース使用量の確認
3. ネットワーク接続の確認
4. 環境変数の設定確認

詳細な情報が必要な場合は、ログレベルをDEBUGに設定して実行してください。
