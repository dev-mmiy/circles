#!/bin/bash

# GCPデプロイメントスクリプト
# このスクリプトを使用してアプリケーションをGCPにデプロイ

set -e

# 色付きの出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ログ関数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 環境変数のチェック
check_env_vars() {
    log_info "環境変数をチェック中..."
    
    required_vars=(
        "GCP_PROJECT_ID"
        "GCP_REGION"
        "CLOUD_SQL_INSTANCE_NAME"
        "MEMORYSTORE_HOST"
        "GCS_BUCKET_NAME"
        "SECRET_KEY"
        "OPENAI_API_KEY"
    )
    
    missing_vars=()
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        log_error "以下の環境変数が設定されていません:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        exit 1
    fi
    
    log_info "環境変数のチェック完了"
}

# GCP認証のチェック
check_gcp_auth() {
    log_info "GCP認証をチェック中..."
    
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        log_error "GCPにログインしていません。以下のコマンドを実行してください:"
        echo "  gcloud auth login"
        exit 1
    fi
    
    log_info "GCP認証チェック完了"
}

# 必要なAPIの有効化
enable_apis() {
    log_info "必要なAPIを有効化中..."
    
    apis=(
        "cloudbuild.googleapis.com"
        "run.googleapis.com"
        "sqladmin.googleapis.com"
        "redis.googleapis.com"
        "storage.googleapis.com"
    )
    
    for api in "${apis[@]}"; do
        log_info "APIを有効化: $api"
        gcloud services enable "$api" --project="$GCP_PROJECT_ID"
    done
    
    log_info "API有効化完了"
}

# Cloud SQLインスタンスの作成
create_cloud_sql() {
    log_info "Cloud SQLインスタンスを作成中..."
    
    # インスタンスが既に存在するかチェック
    if gcloud sql instances describe "$CLOUD_SQL_INSTANCE_NAME" --project="$GCP_PROJECT_ID" >/dev/null 2>&1; then
        log_warn "Cloud SQLインスタンスは既に存在します: $CLOUD_SQL_INSTANCE_NAME"
        return
    fi
    
    gcloud sql instances create "$CLOUD_SQL_INSTANCE_NAME" \
        --database-version=POSTGRES_15 \
        --tier=db-f1-micro \
        --region="$GCP_REGION" \
        --project="$GCP_PROJECT_ID"
    
    log_info "Cloud SQLインスタンス作成完了"
}

# Cloud Memorystoreインスタンスの作成
create_memorystore() {
    log_info "Cloud Memorystoreインスタンスを作成中..."
    
    # インスタンスが既に存在するかチェック
    if gcloud redis instances describe "$MEMORYSTORE_INSTANCE_NAME" --region="$GCP_REGION" --project="$GCP_PROJECT_ID" >/dev/null 2>&1; then
        log_warn "Cloud Memorystoreインスタンスは既に存在します: $MEMORYSTORE_INSTANCE_NAME"
        return
    fi
    
    gcloud redis instances create "$MEMORYSTORE_INSTANCE_NAME" \
        --size=1 \
        --region="$GCP_REGION" \
        --project="$GCP_PROJECT_ID"
    
    log_info "Cloud Memorystoreインスタンス作成完了"
}

# Cloud Storageバケットの作成
create_storage_bucket() {
    log_info "Cloud Storageバケットを作成中..."
    
    # バケットが既に存在するかチェック
    if gsutil ls -b "gs://$GCS_BUCKET_NAME" >/dev/null 2>&1; then
        log_warn "Cloud Storageバケットは既に存在します: $GCS_BUCKET_NAME"
        return
    fi
    
    gsutil mb -p "$GCP_PROJECT_ID" -c STANDARD -l "$GCP_REGION" "gs://$GCS_BUCKET_NAME"
    
    log_info "Cloud Storageバケット作成完了"
}

# アプリケーションのビルド・デプロイ
deploy_app() {
    log_info "アプリケーションをビルド・デプロイ中..."
    
    # Cloud Buildを実行
    gcloud builds submit \
        --config cloudbuild.yaml \
        --substitutions _DATABASE_URL="$DATABASE_URL",_REDIS_URL="$REDIS_URL",_SECRET_KEY="$SECRET_KEY",_OPENAI_API_KEY="$OPENAI_API_KEY",_NEXT_PUBLIC_API_URL="$NEXT_PUBLIC_API_URL" \
        --project="$GCP_PROJECT_ID"
    
    log_info "アプリケーションのデプロイ完了"
}

# メイン関数
main() {
    log_info "GCPデプロイメントを開始します..."
    
    # 環境変数のチェック
    check_env_vars
    
    # GCP認証のチェック
    check_gcp_auth
    
    # 必要なAPIの有効化
    enable_apis
    
    # Cloud SQLインスタンスの作成
    create_cloud_sql
    
    # Cloud Memorystoreインスタンスの作成
    create_memorystore
    
    # Cloud Storageバケットの作成
    create_storage_bucket
    
    # アプリケーションのビルド・デプロイ
    deploy_app
    
    log_info "デプロイメント完了！"
    log_info "アプリケーションのURL:"
    echo "  - バックエンド: https://healthcare-backend-xxxxx-uc.a.run.app"
    echo "  - フロントエンド: https://healthcare-frontend-xxxxx-uc.a.run.app"
}

# スクリプトの実行
main "$@"
