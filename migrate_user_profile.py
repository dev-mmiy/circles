"""
ユーザープロファイル拡張のデータベースマイグレーション
新しいテーブルとカラムを作成
"""

import sqlite3
from datetime import datetime
from pathlib import Path


def create_tables():
    """新しいテーブルを作成"""
    
    # データベースファイルのパス
    db_path = Path("test.db")
    
    # データベースに接続
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. 拡張ユーザープロファイルテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles_extended (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                birth_date DATE,
                gender VARCHAR(10),
                blood_type VARCHAR(10),
                region VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES accounts(id)
            )
        """)
        
        # 2. 体重・体脂肪率履歴テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS body_measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                measurement_date TIMESTAMP NOT NULL,
                weight_kg DECIMAL(5,2),
                body_fat_percentage DECIMAL(4,2),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES accounts(id)
            )
        """)
        
        # 3. 血圧・心拍数履歴テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vital_signs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                measurement_date TIMESTAMP NOT NULL,
                body_temperature DECIMAL(4,2),
                systolic_bp INTEGER,
                diastolic_bp INTEGER,
                heart_rate INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES accounts(id)
            )
        """)
        
        # インデックスを作成
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_profiles_extended_user_id 
            ON user_profiles_extended(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_body_measurements_user_date 
            ON body_measurements(user_id, measurement_date)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_body_measurements_date 
            ON body_measurements(measurement_date)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_vital_signs_user_date 
            ON vital_signs(user_id, measurement_date)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_vital_signs_date 
            ON vital_signs(measurement_date)
        """)
        
        # コミット
        conn.commit()
        print("✅ テーブルとインデックスの作成が完了しました")
        
        # テーブル一覧を表示
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📊 作成されたテーブル: {[table[0] for table in tables]}")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        conn.rollback()
    finally:
        conn.close()


def create_sample_data():
    """サンプルデータを作成"""
    
    db_path = Path("test.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # サンプルユーザーの拡張プロファイル
        cursor.execute("""
            INSERT OR IGNORE INTO user_profiles_extended 
            (user_id, birth_date, gender, blood_type, region)
            VALUES (1, '1990-01-01', 'male', 'A', '東京都')
        """)
        
        # サンプル体重データ
        sample_weights = [
            (1, '2024-01-01 08:00:00', 70.5, 15.2, '朝の測定'),
            (1, '2024-01-02 08:00:00', 70.3, 15.0, '朝の測定'),
            (1, '2024-01-03 08:00:00', 70.1, 14.8, '朝の測定'),
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO body_measurements 
            (user_id, measurement_date, weight_kg, body_fat_percentage, notes)
            VALUES (?, ?, ?, ?, ?)
        """, sample_weights)
        
        # サンプルバイタルサイン
        sample_vitals = [
            (1, '2024-01-01 09:00:00', 36.5, 120, 80, 72, '健康診断'),
            (1, '2024-01-02 09:00:00', 36.3, 118, 78, 70, '定期測定'),
            (1, '2024-01-03 09:00:00', 36.4, 122, 82, 75, '定期測定'),
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO vital_signs 
            (user_id, measurement_date, body_temperature, systolic_bp, diastolic_bp, heart_rate, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, sample_vitals)
        
        conn.commit()
        print("✅ サンプルデータの作成が完了しました")
        
    except Exception as e:
        print(f"❌ サンプルデータ作成エラー: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    print("🚀 ユーザープロファイル拡張のマイグレーションを開始します...")
    create_tables()
    create_sample_data()
    print("🎉 マイグレーションが完了しました！")
