"""
プライバシー設定テーブルのマイグレーション
"""

import os
import sqlite3
from pathlib import Path
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
DB_PATH = Path("test.db")

def create_privacy_settings_table():
    """プライバシー設定テーブルの作成"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_privacy_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                basic_info_level TEXT DEFAULT 'private',
                birth_date_visible BOOLEAN DEFAULT 0,
                gender_visible BOOLEAN DEFAULT 0,
                blood_type_visible BOOLEAN DEFAULT 0,
                region_visible BOOLEAN DEFAULT 0,
                health_data_level TEXT DEFAULT 'private',
                height_visible BOOLEAN DEFAULT 0,
                weight_visible BOOLEAN DEFAULT 0,
                body_fat_visible BOOLEAN DEFAULT 0,
                activity_level_visible BOOLEAN DEFAULT 0,
                medical_info_level TEXT DEFAULT 'private',
                medical_conditions_visible BOOLEAN DEFAULT 0,
                medications_visible BOOLEAN DEFAULT 0,
                allergies_visible BOOLEAN DEFAULT 0,
                doctor_info_visible BOOLEAN DEFAULT 0,
                insurance_visible BOOLEAN DEFAULT 0,
                emergency_contact_level TEXT DEFAULT 'family_only',
                emergency_contact_visible BOOLEAN DEFAULT 1,
                body_measurements_level TEXT DEFAULT 'private',
                body_measurements_visible BOOLEAN DEFAULT 0,
                vital_signs_level TEXT DEFAULT 'private',
                vital_signs_visible BOOLEAN DEFAULT 0,
                allow_data_sharing BOOLEAN DEFAULT 0,
                share_with_healthcare_providers BOOLEAN DEFAULT 0,
                share_with_family BOOLEAN DEFAULT 0,
                share_with_friends BOOLEAN DEFAULT 0,
                allow_research_participation BOOLEAN DEFAULT 0,
                allow_anonymous_statistics BOOLEAN DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES accounts (id)
            )
        """)
        print("✅ user_privacy_settings テーブルを作成しました")
    except Exception as e:
        print(f"❌ テーブル作成エラー: {e}")
        conn.rollback()
    finally:
        conn.close()

def create_data_access_requests_table():
    """データアクセス要求テーブルの作成"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_access_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                requester_user_id INTEGER NOT NULL,
                target_user_id INTEGER NOT NULL,
                requested_data_categories TEXT,
                request_reason TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                responded_at TEXT,
                response_message TEXT,
                FOREIGN KEY (requester_user_id) REFERENCES accounts (id),
                FOREIGN KEY (target_user_id) REFERENCES accounts (id)
            )
        """)
        print("✅ data_access_requests テーブルを作成しました")
    except Exception as e:
        print(f"❌ テーブル作成エラー: {e}")
        conn.rollback()
    finally:
        conn.close()

def create_sample_privacy_settings():
    """サンプルプライバシー設定の作成"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # ユーザー1のプライバシー設定（デフォルト）
        cursor.execute("""
            INSERT OR IGNORE INTO user_privacy_settings (
                user_id, basic_info_level, birth_date_visible, gender_visible,
                health_data_level, height_visible, weight_visible,
                medical_info_level, medical_conditions_visible,
                emergency_contact_level, emergency_contact_visible,
                body_measurements_level, body_measurements_visible,
                vital_signs_level, vital_signs_visible,
                allow_data_sharing, share_with_family,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            1, 'private', 0, 0, 'private', 0, 0, 'private', 0,
            'family_only', 1, 'private', 0, 'private', 0,
            0, 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        
        # ユーザー2のプライバシー設定（より公開的）
        cursor.execute("""
            INSERT OR IGNORE INTO user_privacy_settings (
                user_id, basic_info_level, birth_date_visible, gender_visible,
                health_data_level, height_visible, weight_visible,
                medical_info_level, medical_conditions_visible,
                emergency_contact_level, emergency_contact_visible,
                body_measurements_level, body_measurements_visible,
                vital_signs_level, vital_signs_visible,
                allow_data_sharing, share_with_family, share_with_friends,
                allow_research_participation,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            2, 'friends_only', 1, 1, 'friends_only', 1, 1, 'private', 0,
            'family_only', 1, 'friends_only', 1, 'private', 0,
            1, 1, 1, 1,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        
        conn.commit()
        print("✅ サンプルプライバシー設定を作成しました")
    except Exception as e:
        print(f"❌ サンプルデータ作成エラー: {e}")
        conn.rollback()
    finally:
        conn.close()

def create_sample_data_access_requests():
    """サンプルデータアクセス要求の作成"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # ユーザー2からユーザー1へのデータアクセス要求
        cursor.execute("""
            INSERT OR IGNORE INTO data_access_requests (
                requester_user_id, target_user_id, requested_data_categories,
                request_reason, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            2, 1, '["health_data", "body_measurements"]',
            '健康データの共有をお願いします。一緒に運動をしているので、進捗を共有したいです。',
            'pending',
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        
        # ユーザー1からユーザー2へのデータアクセス要求（承認済み）
        cursor.execute("""
            INSERT OR IGNORE INTO data_access_requests (
                requester_user_id, target_user_id, requested_data_categories,
                request_reason, status, created_at, responded_at, response_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            1, 2, '["basic_info", "health_data"]',
            '基本情報と健康データの共有をお願いします。',
            'approved',
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            '承認しました。お互いの健康管理に役立てましょう。'
        ))
        
        conn.commit()
        print("✅ サンプルデータアクセス要求を作成しました")
    except Exception as e:
        print(f"❌ サンプルデータアクセス要求作成エラー: {e}")
        conn.rollback()
    finally:
        conn.close()

def verify_privacy_settings():
    """プライバシー設定の確認"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # テーブル構造の確認
        cursor.execute("PRAGMA table_info(user_privacy_settings)")
        columns = cursor.fetchall()
        print("\n📊 user_privacy_settings テーブル構造:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # データの確認
        cursor.execute("SELECT user_id, basic_info_level, health_data_level, allow_data_sharing FROM user_privacy_settings")
        data = cursor.fetchall()
        print(f"\n🔍 プライバシー設定データ ({len(data)}件):")
        for row in data:
            print(f"  ユーザーID: {row[0]}, 基本情報: {row[1]}, 健康データ: {row[2]}, データ共有: {row[3]}")
        
        # データアクセス要求の確認
        cursor.execute("SELECT id, requester_user_id, target_user_id, status FROM data_access_requests")
        requests = cursor.fetchall()
        print(f"\n📋 データアクセス要求 ({len(requests)}件):")
        for req in requests:
            print(f"  ID: {req[0]}, 要求者: {req[1]}, 対象: {req[2]}, ステータス: {req[3]}")
            
    except Exception as e:
        print(f"❌ 確認エラー: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 プライバシー設定マイグレーションを開始します...")
    
    print("\n📋 テーブル作成中...")
    create_privacy_settings_table()
    create_data_access_requests_table()
    
    print("\n📊 サンプルデータ作成中...")
    create_sample_privacy_settings()
    create_sample_data_access_requests()
    
    print("\n🔍 マイグレーション結果の確認...")
    verify_privacy_settings()
    
    print("\n🎉 プライバシー設定マイグレーションが完了しました！")
