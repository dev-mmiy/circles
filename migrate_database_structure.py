#!/usr/bin/env python3
"""
データベース構造の修正スクリプト
- accountsテーブルにローマ字名を追加
- user_profiles_healthconditionテーブルに名前変更
"""

import sqlite3
from datetime import datetime, timezone

def migrate_database_structure():
    """データベース構造を修正"""
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    try:
        print("🚀 データベース構造の修正を開始します...")
        
        # 1. accountsテーブルにローマ字名フィールドを追加
        print("📝 accountsテーブルにローマ字名フィールドを追加中...")
        cursor.execute("""
            ALTER TABLE accounts ADD COLUMN first_name_romaji VARCHAR(100)
        """)
        cursor.execute("""
            ALTER TABLE accounts ADD COLUMN last_name_romaji VARCHAR(100)
        """)
        print("✅ accountsテーブルにローマ字名フィールドを追加しました")
        
        # 2. user_profiles_extendedテーブルをuser_profiles_healthconditionにリネーム
        print("📝 健康情報テーブルをリネーム中...")
        
        # 新しいテーブルを作成
        cursor.execute("""
            CREATE TABLE user_profiles_healthcondition (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                birth_date DATE,
                gender VARCHAR(10),
                blood_type VARCHAR(10),
                region VARCHAR(100),
                height_cm REAL,
                target_weight_kg REAL,
                target_body_fat_percentage REAL,
                activity_level TEXT,
                medical_conditions TEXT,
                medications TEXT,
                allergies TEXT,
                emergency_contact_name TEXT,
                emergency_contact_phone TEXT,
                doctor_name TEXT,
                doctor_phone TEXT,
                insurance_number TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES accounts (id)
            )
        """)
        print("✅ user_profiles_healthconditionテーブルを作成しました")
        
        # 3. 既存データを新しいテーブルにコピー
        print("📝 既存データを新しいテーブルにコピー中...")
        cursor.execute("""
            INSERT INTO user_profiles_healthcondition 
            SELECT * FROM user_profiles_extended
        """)
        print("✅ 既存データをコピーしました")
        
        # 4. 古いテーブルを削除
        print("📝 古いテーブルを削除中...")
        cursor.execute("DROP TABLE user_profiles_extended")
        print("✅ 古いテーブルを削除しました")
        
        # 5. インデックスを作成
        print("📝 インデックスを作成中...")
        cursor.execute("""
            CREATE INDEX idx_user_profiles_healthcondition_user_id 
            ON user_profiles_healthcondition(user_id)
        """)
        print("✅ インデックスを作成しました")
        
        # 6. サンプルデータを更新
        print("📝 サンプルデータを更新中...")
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        
        # accountsテーブルにローマ字名を追加
        cursor.execute("""
            UPDATE accounts 
            SET first_name_romaji = 'Test', last_name_romaji = 'User'
            WHERE id = 1
        """)
        cursor.execute("""
            UPDATE accounts 
            SET first_name_romaji = 'Admin', last_name_romaji = 'User'
            WHERE id = 2
        """)
        print("✅ サンプルデータを更新しました")
        
        conn.commit()
        print("🎉 データベース構造の修正が完了しました！")
        
        # 7. 結果を確認
        print("\n🔍 修正結果の確認...")
        
        # accountsテーブルの構造確認
        cursor.execute("PRAGMA table_info(accounts)")
        accounts_columns = cursor.fetchall()
        print("\n📊 accountsテーブル構造:")
        for col in accounts_columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # user_profiles_healthconditionテーブルの構造確認
        cursor.execute("PRAGMA table_info(user_profiles_healthcondition)")
        health_columns = cursor.fetchall()
        print("\n📊 user_profiles_healthconditionテーブル構造:")
        for col in health_columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # データ確認
        cursor.execute("SELECT id, email, first_name_romaji, last_name_romaji FROM accounts")
        accounts_data = cursor.fetchall()
        print("\n🔍 accountsデータ:")
        for acc in accounts_data:
            print(f"  ID: {acc[0]}, Email: {acc[1]}, ローマ字名: {acc[2]} {acc[3]}")
        
        cursor.execute("SELECT user_id, height_cm, activity_level FROM user_profiles_healthcondition")
        health_data = cursor.fetchall()
        print("\n🔍 user_profiles_healthconditionデータ:")
        for health in health_data:
            print(f"  ユーザーID: {health[0]}, 身長: {health[1]}cm, 活動レベル: {health[2]}")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database_structure()
