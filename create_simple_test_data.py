#!/usr/bin/env python3
"""
簡易的なテストデータ作成スクリプト
"""

import sqlite3
from datetime import datetime, timezone

def create_test_data():
    """テストデータを作成"""
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    try:
        # アカウントテーブルにテストデータを挿入
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        
        # テストアカウント1
        cursor.execute("""
            INSERT OR IGNORE INTO accounts (
                id, email, password_hash, is_active, is_verified,
                created_at, updated_at, failed_login_attempts
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            1, 'test@example.com', 'hashed_password_1', True, True,
            now, now, 0
        ))
        
        # テストアカウント2
        cursor.execute("""
            INSERT OR IGNORE INTO accounts (
                id, email, password_hash, is_active, is_verified,
                created_at, updated_at, failed_login_attempts
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            2, 'admin@example.com', 'hashed_password_2', True, True,
            now, now, 0
        ))
        
        # ユーザープロフィール
        cursor.execute("""
            INSERT OR IGNORE INTO user_profiles (
                id, account_id, first_name, last_name, date_of_birth,
                gender, phone_number, address, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            1, 1, 'テスト', 'ユーザー', '1990-01-01',
            'male', '090-1234-5678', '東京都渋谷区', now, now
        ))
        
        # ユーザーロール
        cursor.execute("""
            INSERT OR IGNORE INTO user_role_assignments (
                id, account_id, role, assigned_at, created_at
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            1, 1, 'patient', now, now
        ))
        
        cursor.execute("""
            INSERT OR IGNORE INTO user_role_assignments (
                id, account_id, role, assigned_at, created_at
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            2, 2, 'admin', now, now
        ))
        
        conn.commit()
        print("✅ テストデータの作成が完了しました")
        
        # 作成されたデータを確認
        cursor.execute("SELECT COUNT(*) FROM accounts")
        account_count = cursor.fetchone()[0]
        print(f"📊 アカウント数: {account_count}")
        
        cursor.execute("SELECT COUNT(*) FROM user_profiles")
        profile_count = cursor.fetchone()[0]
        print(f"📊 プロフィール数: {profile_count}")
        
        cursor.execute("SELECT COUNT(*) FROM user_role_assignments")
        role_count = cursor.fetchone()[0]
        print(f"📊 ロール数: {role_count}")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 簡易テストデータ作成を開始します...")
    create_test_data()
    print("🎉 完了しました！")
