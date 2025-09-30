#!/usr/bin/env python3
"""
拡張プロファイルのマイグレーションスクリプト
新しい健康関連属性をデータベースに追加
"""

import os
import sqlite3
from pathlib import Path
from datetime import datetime


def migrate_extended_profile():
    """拡張プロファイルのマイグレーションを実行"""
    db_path = Path("test.db")
    
    if not db_path.exists():
        print("❌ データベースファイルが見つかりません: test.db")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("🔄 拡張プロファイルのマイグレーションを開始します...")
        
        # 新しいカラムを追加
        new_columns = [
            ("height_cm", "REAL"),
            ("target_weight_kg", "REAL"),
            ("target_body_fat_percentage", "REAL"),
            ("activity_level", "TEXT"),
            ("medical_conditions", "TEXT"),
            ("medications", "TEXT"),
            ("allergies", "TEXT"),
            ("emergency_contact_name", "TEXT"),
            ("emergency_contact_phone", "TEXT"),
            ("doctor_name", "TEXT"),
            ("doctor_phone", "TEXT"),
            ("insurance_number", "TEXT")
        ]
        
        for column_name, column_type in new_columns:
            try:
                # カラムが存在するかチェック
                cursor.execute(f"PRAGMA table_info(user_profiles_extended)")
                columns = [col[1] for col in cursor.fetchall()]
                
                if column_name not in columns:
                    cursor.execute(f"ALTER TABLE user_profiles_extended ADD COLUMN {column_name} {column_type}")
                    print(f"✅ カラム '{column_name}' を追加しました")
                else:
                    print(f"⚠️ カラム '{column_name}' は既に存在します")
                    
            except sqlite3.Error as e:
                print(f"❌ カラム '{column_name}' の追加に失敗: {e}")
        
        # サンプルデータを更新
        sample_data = {
            "height_cm": 170.0,
            "target_weight_kg": 65.0,
            "target_body_fat_percentage": 15.0,
            "activity_level": "moderate",
            "medical_conditions": "高血圧",
            "medications": "降圧剤",
            "allergies": "花粉症",
            "emergency_contact_name": "田中太郎",
            "emergency_contact_phone": "090-1234-5678",
            "doctor_name": "佐藤医師",
            "doctor_phone": "03-1234-5678",
            "insurance_number": "12345678"
        }
        
        # 既存のレコードを更新
        update_sql = """
        UPDATE user_profiles_extended 
        SET height_cm = ?, target_weight_kg = ?, target_body_fat_percentage = ?,
            activity_level = ?, medical_conditions = ?, medications = ?,
            allergies = ?, emergency_contact_name = ?, emergency_contact_phone = ?,
            doctor_name = ?, doctor_phone = ?, insurance_number = ?,
            updated_at = ?
        WHERE user_id = 1
        """
        
        cursor.execute(update_sql, (
            sample_data["height_cm"],
            sample_data["target_weight_kg"],
            sample_data["target_body_fat_percentage"],
            sample_data["activity_level"],
            sample_data["medical_conditions"],
            sample_data["medications"],
            sample_data["allergies"],
            sample_data["emergency_contact_name"],
            sample_data["emergency_contact_phone"],
            sample_data["doctor_name"],
            sample_data["doctor_phone"],
            sample_data["insurance_number"],
            datetime.now().isoformat()
        ))
        
        if cursor.rowcount > 0:
            print("✅ サンプルデータを更新しました")
        else:
            print("⚠️ 更新対象のレコードが見つかりませんでした")
        
        # テーブル構造を確認
        cursor.execute("PRAGMA table_info(user_profiles_extended)")
        columns = cursor.fetchall()
        
        print("\n📊 更新後のテーブル構造:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.commit()
        print("\n🎉 マイグレーションが完了しました！")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ マイグレーションエラー: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()


def verify_migration():
    """マイグレーション結果を確認"""
    db_path = Path("test.db")
    
    if not db_path.exists():
        print("❌ データベースファイルが見つかりません")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 拡張プロファイルのデータを確認
        cursor.execute("""
            SELECT user_id, height_cm, target_weight_kg, activity_level, 
                   medical_conditions, emergency_contact_name, doctor_name
            FROM user_profiles_extended 
            WHERE user_id = 1
        """)
        
        result = cursor.fetchone()
        if result:
            print("\n📋 マイグレーション結果:")
            print(f"  - ユーザーID: {result[0]}")
            print(f"  - 身長: {result[1]} cm")
            print(f"  - 目標体重: {result[2]} kg")
            print(f"  - 活動レベル: {result[3]}")
            print(f"  - 既往歴: {result[4]}")
            print(f"  - 緊急連絡先: {result[5]}")
            print(f"  - 主治医: {result[6]}")
            return True
        else:
            print("❌ データが見つかりません")
            return False
            
    except sqlite3.Error as e:
        print(f"❌ 確認エラー: {e}")
        return False
        
    finally:
        conn.close()


if __name__ == "__main__":
    print("🚀 拡張プロファイルマイグレーションを開始します...")
    
    if migrate_extended_profile():
        print("\n🔍 マイグレーション結果を確認します...")
        verify_migration()
    else:
        print("❌ マイグレーションに失敗しました")
