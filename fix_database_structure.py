#!/usr/bin/env python3
"""
データベース構造の修正スクリプト（正しいデータで再構築）
"""

import sqlite3
from datetime import datetime, timezone

def fix_database_structure():
    """データベース構造を正しく修正"""
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    try:
        print("🚀 データベース構造の修正を開始します...")
        
        # 1. 古いテーブルを削除
        print("📝 古いテーブルを削除中...")
        cursor.execute("DROP TABLE IF EXISTS user_profiles_healthcondition")
        print("✅ 古いテーブルを削除しました")
        
        # 2. 正しい構造でテーブルを作成
        print("📝 正しい構造でテーブルを作成中...")
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
        
        # 3. 正しいサンプルデータを挿入
        print("📝 正しいサンプルデータを挿入中...")
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            INSERT INTO user_profiles_healthcondition (
                user_id, birth_date, gender, blood_type, region,
                height_cm, target_weight_kg, target_body_fat_percentage, activity_level,
                medical_conditions, medications, allergies,
                emergency_contact_name, emergency_contact_phone, doctor_name, doctor_phone, insurance_number,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            1, '1990-01-01', 'male', 'A', '東京都',
            170.0, 65.0, 15.0, 'moderate',
            '高血圧', '降圧剤', '花粉症',
            '田中太郎', '090-1234-5678', '佐藤医師', '03-1234-5678', '12345678',
            now, now
        ))
        print("✅ 正しいサンプルデータを挿入しました")
        
        # 4. accountsテーブルにローマ字名を追加
        print("📝 accountsテーブルにローマ字名を追加中...")
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
        print("✅ accountsテーブルにローマ字名を追加しました")
        
        conn.commit()
        print("🎉 データベース構造の修正が完了しました！")
        
        # 5. 結果を確認
        print("\n🔍 修正結果の確認...")
        
        cursor.execute("SELECT * FROM user_profiles_healthcondition WHERE user_id = 1")
        health_data = cursor.fetchone()
        if health_data:
            print(f"\n📊 user_profiles_healthconditionデータ:")
            print(f"  ID: {health_data[0]}")
            print(f"  ユーザーID: {health_data[1]}")
            print(f"  生年月日: {health_data[2]}")
            print(f"  性別: {health_data[3]}")
            print(f"  血液型: {health_data[4]}")
            print(f"  地域: {health_data[5]}")
            print(f"  身長: {health_data[6]}cm")
            print(f"  目標体重: {health_data[7]}kg")
            print(f"  目標体脂肪率: {health_data[8]}%")
            print(f"  活動レベル: {health_data[9]}")
            print(f"  既往歴: {health_data[10]}")
            print(f"  薬物: {health_data[11]}")
            print(f"  アレルギー: {health_data[12]}")
            print(f"  緊急連絡先: {health_data[13]} ({health_data[14]})")
            print(f"  医師: {health_data[15]} ({health_data[16]})")
            print(f"  保険証番号: {health_data[17]}")
            print(f"  作成日時: {health_data[18]}")
            print(f"  更新日時: {health_data[19]}")
        
        cursor.execute("SELECT id, email, first_name_romaji, last_name_romaji FROM accounts WHERE id = 1")
        account_data = cursor.fetchone()
        if account_data:
            print(f"\n📊 accountsデータ:")
            print(f"  ID: {account_data[0]}")
            print(f"  メール: {account_data[1]}")
            print(f"  ローマ字名: {account_data[2]} {account_data[3]}")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_database_structure()
