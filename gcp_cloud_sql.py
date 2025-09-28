"""
GCP Cloud SQL接続設定
Cloud SQL Proxyを使用してCloud SQLインスタンスに接続
"""

import os
import subprocess
import time
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class CloudSQLConnection:
    def __init__(self):
        self.project_id = os.getenv('GCP_PROJECT_ID')
        self.region = os.getenv('GCP_REGION', 'us-central1')
        self.instance_name = os.getenv('CLOUD_SQL_INSTANCE_NAME')
        self.database_name = os.getenv('CLOUD_SQL_DATABASE_NAME', 'healthcare_db')
        self.username = os.getenv('CLOUD_SQL_USERNAME', 'healthcare_user')
        self.password = os.getenv('CLOUD_SQL_PASSWORD')
        
        # Cloud SQL Proxy設定
        self.proxy_host = os.getenv('CLOUD_SQL_PROXY_HOST', '127.0.0.1')
        self.proxy_port = os.getenv('CLOUD_SQL_PROXY_PORT', '5432')
        
        # 接続文字列
        self.connection_name = f"{self.project_id}:{self.region}:{self.instance_name}"
        
    def start_cloud_sql_proxy(self):
        """Cloud SQL Proxyを起動"""
        try:
            # Cloud SQL Proxyが既に起動しているかチェック
            result = subprocess.run(['pgrep', '-f', 'cloud_sql_proxy'], 
                                 capture_output=True, text=True)
            if result.returncode == 0:
                print("Cloud SQL Proxy is already running")
                return True
                
            # Cloud SQL Proxyを起動
            cmd = [
                'cloud_sql_proxy',
                f'-instances={self.connection_name}=tcp:{self.proxy_port}',
                '-credential_file=' + os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
            ]
            
            print(f"Starting Cloud SQL Proxy: {' '.join(cmd)}")
            subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # プロキシの起動を待つ
            time.sleep(5)
            return True
            
        except Exception as e:
            print(f"Error starting Cloud SQL Proxy: {e}")
            return False
    
    def get_connection_string(self):
        """データベース接続文字列を取得"""
        if os.getenv('DATABASE_URL'):
            return os.getenv('DATABASE_URL')
        
        # Cloud SQL Proxy経由の接続
        return f"postgresql://{self.username}:{self.password}@{self.proxy_host}:{self.proxy_port}/{self.database_name}"
    
    def get_engine(self):
        """SQLAlchemyエンジンを取得"""
        connection_string = self.get_connection_string()
        return create_engine(connection_string, pool_pre_ping=True)
    
    def get_session(self):
        """データベースセッションを取得"""
        engine = self.get_engine()
        Session = sessionmaker(bind=engine)
        return Session()
    
    def test_connection(self):
        """データベース接続をテスト"""
        try:
            connection_string = self.get_connection_string()
            conn = psycopg2.connect(connection_string)
            conn.close()
            print("Database connection successful")
            return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False

def setup_cloud_sql():
    """Cloud SQL設定を初期化"""
    cloud_sql = CloudSQLConnection()
    
    # 必要な環境変数をチェック
    required_vars = ['GCP_PROJECT_ID', 'CLOUD_SQL_INSTANCE_NAME', 'CLOUD_SQL_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Missing required environment variables: {missing_vars}")
        return None
    
    # Cloud SQL Proxyを起動
    if cloud_sql.start_cloud_sql_proxy():
        # 接続をテスト
        if cloud_sql.test_connection():
            return cloud_sql
        else:
            print("Failed to connect to Cloud SQL")
            return None
    else:
        print("Failed to start Cloud SQL Proxy")
        return None

# 使用例
if __name__ == "__main__":
    # 環境変数を設定
    os.environ['GCP_PROJECT_ID'] = 'your-project-id'
    os.environ['CLOUD_SQL_INSTANCE_NAME'] = 'your-instance-name'
    os.environ['CLOUD_SQL_PASSWORD'] = 'your-password'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'path/to/service-account-key.json'
    
    # Cloud SQL設定を初期化
    cloud_sql = setup_cloud_sql()
    
    if cloud_sql:
        print("Cloud SQL setup successful")
        # データベースセッションを使用
        session = cloud_sql.get_session()
        # ここでデータベース操作を実行
        session.close()
    else:
        print("Cloud SQL setup failed")
