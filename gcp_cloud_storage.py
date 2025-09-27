"""
GCP Cloud Storage 接続設定
Cloud Storageバケットにファイルをアップロード・ダウンロード
"""

import os
import json
import mimetypes
from datetime import datetime, timedelta
from google.cloud import storage
from google.cloud.exceptions import NotFound
from google.auth import default
from google.auth.exceptions import DefaultCredentialsError

class CloudStorageConnection:
    def __init__(self):
        self.project_id = os.getenv('GCP_PROJECT_ID')
        self.bucket_name = os.getenv('GCS_BUCKET_NAME')
        self.region = os.getenv('GCS_BUCKET_REGION', 'us-central1')
        
        # 認証設定
        self.credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        
        # Cloud Storageクライアントを初期化
        try:
            if self.credentials_path:
                self.client = storage.Client.from_service_account_json(
                    self.credentials_path, project=self.project_id
                )
            else:
                # Application Default Credentialsを使用
                self.client = storage.Client(project=self.project_id)
        except DefaultCredentialsError:
            print("Error: No valid credentials found")
            self.client = None
    
    def get_bucket(self):
        """バケットを取得"""
        try:
            if not self.client:
                return None
            return self.client.bucket(self.bucket_name)
        except Exception as e:
            print(f"Error getting bucket: {e}")
            return None
    
    def upload_file(self, local_file_path, remote_file_path, content_type=None):
        """ファイルをアップロード"""
        try:
            bucket = self.get_bucket()
            if not bucket:
                return False
            
            blob = bucket.blob(remote_file_path)
            
            # コンテンツタイプを自動判定
            if not content_type:
                content_type, _ = mimetypes.guess_type(local_file_path)
                if not content_type:
                    content_type = 'application/octet-stream'
            
            # メタデータを設定
            blob.content_type = content_type
            blob.metadata = {
                'uploaded_at': datetime.utcnow().isoformat(),
                'original_filename': os.path.basename(local_file_path)
            }
            
            # ファイルをアップロード
            blob.upload_from_filename(local_file_path, content_type=content_type)
            
            print(f"File uploaded successfully: {remote_file_path}")
            return True
            
        except Exception as e:
            print(f"Error uploading file: {e}")
            return False
    
    def download_file(self, remote_file_path, local_file_path):
        """ファイルをダウンロード"""
        try:
            bucket = self.get_bucket()
            if not bucket:
                return False
            
            blob = bucket.blob(remote_file_path)
            
            # ファイルが存在するかチェック
            if not blob.exists():
                print(f"File not found: {remote_file_path}")
                return False
            
            # ファイルをダウンロード
            blob.download_to_filename(local_file_path)
            
            print(f"File downloaded successfully: {local_file_path}")
            return True
            
        except Exception as e:
            print(f"Error downloading file: {e}")
            return False
    
    def delete_file(self, remote_file_path):
        """ファイルを削除"""
        try:
            bucket = self.get_bucket()
            if not bucket:
                return False
            
            blob = bucket.blob(remote_file_path)
            blob.delete()
            
            print(f"File deleted successfully: {remote_file_path}")
            return True
            
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def list_files(self, prefix=None, max_results=None):
        """ファイル一覧を取得"""
        try:
            bucket = self.get_bucket()
            if not bucket:
                return []
            
            blobs = bucket.list_blobs(prefix=prefix, max_results=max_results)
            
            files = []
            for blob in blobs:
                files.append({
                    'name': blob.name,
                    'size': blob.size,
                    'content_type': blob.content_type,
                    'created': blob.time_created,
                    'updated': blob.updated,
                    'url': blob.public_url
                })
            
            return files
            
        except Exception as e:
            print(f"Error listing files: {e}")
            return []
    
    def get_signed_url(self, remote_file_path, expiration_minutes=60):
        """署名付きURLを生成"""
        try:
            bucket = self.get_bucket()
            if not bucket:
                return None
            
            blob = bucket.blob(remote_file_path)
            
            # 署名付きURLを生成
            url = blob.generate_signed_url(
                version="v4",
                expiration=datetime.utcnow() + timedelta(minutes=expiration_minutes),
                method="GET"
            )
            
            return url
            
        except Exception as e:
            print(f"Error generating signed URL: {e}")
            return None
    
    def get_file_info(self, remote_file_path):
        """ファイル情報を取得"""
        try:
            bucket = self.get_bucket()
            if not bucket:
                return None
            
            blob = bucket.blob(remote_file_path)
            
            if not blob.exists():
                return None
            
            return {
                'name': blob.name,
                'size': blob.size,
                'content_type': blob.content_type,
                'created': blob.time_created,
                'updated': blob.updated,
                'md5_hash': blob.md5_hash,
                'crc32c': blob.crc32c,
                'metadata': blob.metadata
            }
            
        except Exception as e:
            print(f"Error getting file info: {e}")
            return None
    
    def create_bucket(self, bucket_name=None, location=None):
        """バケットを作成"""
        try:
            if not self.client:
                return False
            
            bucket_name = bucket_name or self.bucket_name
            location = location or self.region
            
            bucket = self.client.bucket(bucket_name)
            bucket.location = location
            
            # バケットを作成
            bucket.create()
            
            print(f"Bucket created successfully: {bucket_name}")
            return True
            
        except Exception as e:
            print(f"Error creating bucket: {e}")
            return False

def setup_cloud_storage():
    """Cloud Storage設定を初期化"""
    storage_conn = CloudStorageConnection()
    
    # 必要な環境変数をチェック
    required_vars = ['GCP_PROJECT_ID', 'GCS_BUCKET_NAME']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Missing required environment variables: {missing_vars}")
        return None
    
    # クライアントが正常に初期化されているかチェック
    if not storage_conn.client:
        print("Failed to initialize Cloud Storage client")
        return None
    
    # バケットが存在するかチェック
    bucket = storage_conn.get_bucket()
    if not bucket:
        print(f"Bucket not found: {storage_conn.bucket_name}")
        return None
    
    print("Cloud Storage setup successful")
    return storage_conn

# 使用例
if __name__ == "__main__":
    # 環境変数を設定
    os.environ['GCP_PROJECT_ID'] = 'your-project-id'
    os.environ['GCS_BUCKET_NAME'] = 'your-bucket-name'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'path/to/service-account-key.json'
    
    # Cloud Storage設定を初期化
    storage_conn = setup_cloud_storage()
    
    if storage_conn:
        print("Cloud Storage setup successful")
        
        # ファイル一覧を取得
        files = storage_conn.list_files()
        print(f"Files in bucket: {len(files)}")
        
        # ファイル情報を取得
        if files:
            file_info = storage_conn.get_file_info(files[0]['name'])
            print(f"File info: {file_info}")
    else:
        print("Cloud Storage setup failed")
