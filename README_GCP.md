# GCP デプロイメントガイド

このガイドでは、Healthcare Community PlatformをGoogle Cloud Platform (GCP) にデプロイする方法を説明します。

## 前提条件

### 1. 必要なツールのインストール

```bash
# Google Cloud CLIのインストール
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Dockerのインストール
sudo apt-get update
sudo apt-get install docker.io
sudo usermod -aG docker $USER

# 再ログインが必要
```

### 2. GCPプロジェクトの設定

```bash
# GCPにログイン
gcloud auth login

# プロジェクトを設定
gcloud config set project YOUR_PROJECT_ID

# 認証情報を設定
gcloud auth application-default login
```

## 環境変数の設定

### 1. 環境変数ファイルの作成

```bash
# GCP用の環境変数ファイルを作成
cp env.gcp.example .env

# 環境変数を編集
nano .env
```

### 2. 必要な環境変数

```bash
# GCP設定
GCP_PROJECT_ID=your-gcp-project-id
GCP_REGION=us-central1

# データベース設定
CLOUD_SQL_INSTANCE_NAME=healthcare-db
CLOUD_SQL_DATABASE_NAME=healthcare_db
CLOUD_SQL_USERNAME=healthcare_user
CLOUD_SQL_PASSWORD=your-secure-password

# Redis設定
MEMORYSTORE_INSTANCE_NAME=healthcare-redis
MEMORYSTORE_HOST=your-memorystore-ip
MEMORYSTORE_PORT=6379

# Cloud Storage設定
GCS_BUCKET_NAME=healthcare-storage-bucket
GCS_BUCKET_REGION=us-central1

# アプリケーション設定
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key-here
DEBUG=false
```

## デプロイメント手順

### 1. 自動デプロイメント（推奨）

```bash
# デプロイメントスクリプトを実行
./deploy.sh
```

### 2. 手動デプロイメント

#### 2.1. 必要なAPIの有効化

```bash
# Cloud Build API
gcloud services enable cloudbuild.googleapis.com

# Cloud Run API
gcloud services enable run.googleapis.com

# Cloud SQL API
gcloud services enable sqladmin.googleapis.com

# Cloud Memorystore API
gcloud services enable redis.googleapis.com

# Cloud Storage API
gcloud services enable storage.googleapis.com
```

#### 2.2. Cloud SQLインスタンスの作成

```bash
# PostgreSQLインスタンスを作成
gcloud sql instances create healthcare-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --project=YOUR_PROJECT_ID

# データベースを作成
gcloud sql databases create healthcare_db \
    --instance=healthcare-db \
    --project=YOUR_PROJECT_ID

# ユーザーを作成
gcloud sql users create healthcare_user \
    --instance=healthcare-db \
    --password=your-secure-password \
    --project=YOUR_PROJECT_ID
```

#### 2.3. Cloud Memorystoreインスタンスの作成

```bash
# Redisインスタンスを作成
gcloud redis instances create healthcare-redis \
    --size=1 \
    --region=us-central1 \
    --project=YOUR_PROJECT_ID
```

#### 2.4. Cloud Storageバケットの作成

```bash
# バケットを作成
gsutil mb -p YOUR_PROJECT_ID -c STANDARD -l us-central1 gs://healthcare-storage-bucket
```

#### 2.5. アプリケーションのビルド・デプロイ

```bash
# Cloud Buildを実行
gcloud builds submit \
    --config cloudbuild.yaml \
    --substitutions _DATABASE_URL="$DATABASE_URL",_REDIS_URL="$REDIS_URL",_SECRET_KEY="$SECRET_KEY",_OPENAI_API_KEY="$OPENAI_API_KEY" \
    --project=YOUR_PROJECT_ID
```

## ローカル開発環境

### 1. ローカル開発用の起動

```bash
# ローカル開発環境を起動
docker-compose --profile local up -d

# データベースマイグレーション
docker-compose run --rm migration

# 開発用バックエンドを起動
docker-compose up -d dev-backend
```

### 2. Cloud SQL Proxyの使用

```bash
# Cloud SQL Proxyをインストール
curl -o cloud_sql_proxy https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64
chmod +x cloud_sql_proxy

# Cloud SQL Proxyを起動
./cloud_sql_proxy -instances=YOUR_PROJECT_ID:us-central1:healthcare-db=tcp:5432
```

## 監視とログ

### 1. Cloud Logging

```bash
# アプリケーションログを確認
gcloud logging read "resource.type=cloud_run_revision" --limit=50

# エラーログを確認
gcloud logging read "severity>=ERROR" --limit=50
```

### 2. Cloud Monitoring

```bash
# メトリクスを確認
gcloud monitoring metrics list
```

## トラブルシューティング

### 1. よくある問題

#### データベース接続エラー
```bash
# Cloud SQLインスタンスの状態を確認
gcloud sql instances describe healthcare-db

# 接続文字列を確認
echo $DATABASE_URL
```

#### Redis接続エラー
```bash
# Cloud Memorystoreインスタンスの状態を確認
gcloud redis instances describe healthcare-redis --region=us-central1
```

#### ストレージアクセスエラー
```bash
# バケットの権限を確認
gsutil iam get gs://healthcare-storage-bucket
```

### 2. ログの確認

```bash
# Cloud Runのログを確認
gcloud logging read "resource.type=cloud_run_revision" --limit=100

# 特定のサービスのログを確認
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=healthcare-backend" --limit=100
```

## セキュリティ設定

### 1. IAMロールの設定

```bash
# サービスアカウントを作成
gcloud iam service-accounts create healthcare-service-account \
    --display-name="Healthcare Service Account"

# 必要なロールを付与
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:healthcare-service-account@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:healthcare-service-account@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/redis.editor"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:healthcare-service-account@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"
```

### 2. ネットワークセキュリティ

```bash
# VPCネットワークを作成
gcloud compute networks create healthcare-vpc \
    --subnet-mode=regional

# サブネットを作成
gcloud compute networks subnets create healthcare-subnet \
    --network=healthcare-vpc \
    --range=10.0.0.0/24 \
    --region=us-central1
```

## コスト最適化

### 1. リソースの最適化

```bash
# Cloud SQLインスタンスのサイズを調整
gcloud sql instances patch healthcare-db \
    --tier=db-f1-micro

# Cloud Runの設定を調整
gcloud run services update healthcare-backend \
    --min-instances=0 \
    --max-instances=5 \
    --memory=512Mi \
    --cpu=0.5
```

### 2. 監視とアラート

```bash
# アラートポリシーを作成
gcloud alpha monitoring policies create \
    --policy-from-file=alert-policy.yaml
```

## バックアップと復旧

### 1. データベースのバックアップ

```bash
# 自動バックアップを有効化
gcloud sql instances patch healthcare-db \
    --backup-start-time=02:00

# 手動バックアップを作成
gcloud sql backups create \
    --instance=healthcare-db \
    --description="Manual backup"
```

### 2. ストレージのバックアップ

```bash
# バケットのバックアップを作成
gsutil -m cp -r gs://healthcare-storage-bucket gs://healthcare-storage-backup
```

## スケーリング

### 1. 自動スケーリング

```bash
# Cloud Runの自動スケーリングを設定
gcloud run services update healthcare-backend \
    --min-instances=1 \
    --max-instances=10 \
    --cpu-throttling
```

### 2. 負荷分散

```bash
# ロードバランサーを作成
gcloud compute backend-services create healthcare-backend-service \
    --global \
    --load-balancing-scheme=EXTERNAL
```

## メンテナンス

### 1. 定期メンテナンス

```bash
# データベースのメンテナンス
gcloud sql instances patch healthcare-db \
    --maintenance-window-day=SUN \
    --maintenance-window-hour=02

# アプリケーションの更新
gcloud builds submit --config cloudbuild.yaml
```

### 2. 監視とアラート

```bash
# ヘルスチェックを設定
gcloud compute health-checks create http healthcare-health-check \
    --port=8000 \
    --request-path=/health
```

このガイドに従って、Healthcare Community PlatformをGCPに正常にデプロイできます。何か問題が発生した場合は、ログを確認してトラブルシューティングを行ってください。
