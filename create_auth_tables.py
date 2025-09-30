#!/usr/bin/env python3
"""
認証テーブルの作成スクリプト
"""

import sqlite3
from datetime import datetime, timezone

def create_auth_tables():
    """認証テーブルを作成"""
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    try:
        # accounts テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                is_verified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                failed_login_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP NULL
            )
        """)
        
        # user_profiles テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                date_of_birth DATE,
                gender VARCHAR(10),
                phone_number VARCHAR(20),
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts (id)
            )
        """)
        
        # user_role_assignments テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_role_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                role VARCHAR(50) NOT NULL,
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts (id)
            )
        """)
        
        # user_sessions テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                session_token VARCHAR(255) UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts (id)
            )
        """)
        
        # mfa_configs テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mfa_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                mfa_type VARCHAR(20) NOT NULL,
                secret_key VARCHAR(255),
                backup_codes TEXT,
                is_enabled BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts (id)
            )
        """)
        
        conn.commit()
        print("✅ 認証テーブルの作成が完了しました")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 認証テーブル作成を開始します...")
    create_auth_tables()
    print("🎉 完了しました！")
