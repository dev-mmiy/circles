"""
GCP Cloud Memorystore (Redis) 接続設定
Cloud Memorystoreインスタンスに接続
"""

import os
import redis
from redis import Redis
import json
import time

class CloudMemorystoreConnection:
    def __init__(self):
        self.project_id = os.getenv('GCP_PROJECT_ID')
        self.region = os.getenv('GCP_REGION', 'us-central1')
        self.instance_name = os.getenv('MEMORYSTORE_INSTANCE_NAME')
        self.host = os.getenv('MEMORYSTORE_HOST')
        self.port = int(os.getenv('MEMORYSTORE_PORT', '6379'))
        self.password = os.getenv('MEMORYSTORE_PASSWORD', '')
        
        # 接続設定
        self.connection_kwargs = {
            'host': self.host,
            'port': self.port,
            'decode_responses': True,
            'socket_connect_timeout': 5,
            'socket_timeout': 5,
            'retry_on_timeout': True,
            'health_check_interval': 30
        }
        
        if self.password:
            self.connection_kwargs['password'] = self.password
    
    def get_redis_client(self):
        """Redisクライアントを取得"""
        try:
            client = Redis(**self.connection_kwargs)
            return client
        except Exception as e:
            print(f"Error creating Redis client: {e}")
            return None
    
    def test_connection(self):
        """Redis接続をテスト"""
        try:
            client = self.get_redis_client()
            if client:
                # 接続テスト
                client.ping()
                print("Redis connection successful")
                return True
            else:
                print("Failed to create Redis client")
                return False
        except Exception as e:
            print(f"Redis connection failed: {e}")
            return False
    
    def get_connection_string(self):
        """Redis接続文字列を取得"""
        if os.getenv('REDIS_URL'):
            return os.getenv('REDIS_URL')
        
        # Cloud Memorystore接続文字列
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}"
        else:
            return f"redis://{self.host}:{self.port}"
    
    def set_cache(self, key, value, expire=None):
        """キャッシュを設定"""
        try:
            client = self.get_redis_client()
            if client:
                if expire:
                    client.setex(key, expire, json.dumps(value))
                else:
                    client.set(key, json.dumps(value))
                return True
        except Exception as e:
            print(f"Error setting cache: {e}")
            return False
    
    def get_cache(self, key):
        """キャッシュを取得"""
        try:
            client = self.get_redis_client()
            if client:
                value = client.get(key)
                if value:
                    return json.loads(value)
                return None
        except Exception as e:
            print(f"Error getting cache: {e}")
            return None
    
    def delete_cache(self, key):
        """キャッシュを削除"""
        try:
            client = self.get_redis_client()
            if client:
                client.delete(key)
                return True
        except Exception as e:
            print(f"Error deleting cache: {e}")
            return False
    
    def get_cache_info(self):
        """キャッシュ情報を取得"""
        try:
            client = self.get_redis_client()
            if client:
                info = client.info()
                return {
                    'used_memory': info.get('used_memory_human'),
                    'connected_clients': info.get('connected_clients'),
                    'total_commands_processed': info.get('total_commands_processed'),
                    'keyspace_hits': info.get('keyspace_hits'),
                    'keyspace_misses': info.get('keyspace_misses')
                }
        except Exception as e:
            print(f"Error getting cache info: {e}")
            return None

def setup_cloud_memorystore():
    """Cloud Memorystore設定を初期化"""
    memorystore = CloudMemorystoreConnection()
    
    # 必要な環境変数をチェック
    required_vars = ['GCP_PROJECT_ID', 'MEMORYSTORE_HOST']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Missing required environment variables: {missing_vars}")
        return None
    
    # 接続をテスト
    if memorystore.test_connection():
        return memorystore
    else:
        print("Failed to connect to Cloud Memorystore")
        return None

# 使用例
if __name__ == "__main__":
    # 環境変数を設定
    os.environ['GCP_PROJECT_ID'] = 'your-project-id'
    os.environ['MEMORYSTORE_HOST'] = 'your-memorystore-ip'
    os.environ['MEMORYSTORE_PORT'] = '6379'
    os.environ['MEMORYSTORE_PASSWORD'] = 'your-password'
    
    # Cloud Memorystore設定を初期化
    memorystore = setup_cloud_memorystore()
    
    if memorystore:
        print("Cloud Memorystore setup successful")
        
        # キャッシュの使用例
        memorystore.set_cache('test_key', {'message': 'Hello World'}, expire=3600)
        cached_value = memorystore.get_cache('test_key')
        print(f"Cached value: {cached_value}")
        
        # キャッシュ情報を取得
        cache_info = memorystore.get_cache_info()
        print(f"Cache info: {cache_info}")
    else:
        print("Cloud Memorystore setup failed")
