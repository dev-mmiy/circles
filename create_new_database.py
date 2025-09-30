#!/usr/bin/env python3
"""
新しいデータベース構造の作成スクリプト
統合されたユーザー管理システム
"""

import sqlite3
import os
from datetime import datetime, timezone

def create_database():
    """新しいデータベース構造を作成"""
    
    # 既存のデータベースファイルを削除
    if os.path.exists('test.db'):
        os.remove('test.db')
    
    # データベース接続
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    print("🗑️  既存データベースを削除しました")
    
    # 1. users テーブル（統合されたユーザー管理）
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            first_name_romaji VARCHAR(100),
            last_name_romaji VARCHAR(100),
            first_name_local VARCHAR(100),
            last_name_local VARCHAR(100),
            phone_number VARCHAR(20),
            address TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )
    ''')
    print("✅ users テーブルを作成しました")
    
    # 2. user_health_profiles テーブル
    cursor.execute('''
        CREATE TABLE user_health_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            birth_date DATE,
            gender VARCHAR(10),
            blood_type VARCHAR(5),
            region VARCHAR(100),
            height_cm FLOAT,
            current_weight_kg FLOAT,
            target_weight_kg FLOAT,
            target_body_fat_percentage FLOAT,
            activity_level VARCHAR(20),
            medical_conditions TEXT,
            medications TEXT,
            allergies TEXT,
            emergency_contact_name VARCHAR(100),
            emergency_contact_phone VARCHAR(20),
            doctor_name VARCHAR(100),
            doctor_phone VARCHAR(20),
            insurance_number VARCHAR(50),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    print("✅ user_health_profiles テーブルを作成しました")
    
    # 3. user_sessions テーブル
    cursor.execute('''
        CREATE TABLE user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_token VARCHAR(255) UNIQUE NOT NULL,
            refresh_token VARCHAR(255),
            device_info TEXT,
            expires_at DATETIME NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    print("✅ user_sessions テーブルを作成しました")
    
    # 4. body_measurements テーブル
    cursor.execute('''
        CREATE TABLE body_measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            weight_kg FLOAT,
            body_fat_percentage FLOAT,
            notes TEXT,
            measurement_date DATETIME NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    print("✅ body_measurements テーブルを作成しました")
    
    # 5. privacy_settings テーブル
    cursor.execute('''
        CREATE TABLE privacy_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            privacy_level VARCHAR(20) DEFAULT 'private',
            share_medical_info BOOLEAN DEFAULT FALSE,
            share_contact_info BOOLEAN DEFAULT FALSE,
            share_measurements BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    print("✅ privacy_settings テーブルを作成しました")
    
    # インデックスの作成
    cursor.execute('CREATE INDEX idx_users_email ON users(email)')
    cursor.execute('CREATE INDEX idx_user_health_profiles_user_id ON user_health_profiles(user_id)')
    cursor.execute('CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id)')
    cursor.execute('CREATE INDEX idx_user_sessions_token ON user_sessions(session_token)')
    cursor.execute('CREATE INDEX idx_body_measurements_user_id ON body_measurements(user_id)')
    cursor.execute('CREATE INDEX idx_body_measurements_date ON body_measurements(measurement_date)')
    cursor.execute('CREATE INDEX idx_privacy_settings_user_id ON privacy_settings(user_id)')
    
    print("✅ インデックスを作成しました")
    
    # コミット
    conn.commit()
    print("💾 データベース構造を保存しました")
    
    return conn

def create_test_data(conn):
    """テストデータの作成"""
    cursor = conn.cursor()
    
    # 現在の日時
    now = datetime.now(timezone.utc)
    now_str = now.strftime('%Y-%m-%d %H:%M:%S')
    
    # 1. テストユーザーの作成
    test_users = [
        {
            'email': 'miyasaka@gmail.com',
            'password_hash': '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/9.8.8.8',  # 'password'
            'first_name_romaji': 'Taro',
            'last_name_romaji': 'Miyasaka',
            'first_name_local': '太郎',
            'last_name_local': '宮坂',
            'phone_number': '090-1234-5678',
            'address': '東京都渋谷区'
        },
        {
            'email': 'test@example.com',
            'password_hash': '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/9.8.8.8',  # 'password'
            'first_name_romaji': 'Hanako',
            'last_name_romaji': 'Yamada',
            'first_name_local': '花子',
            'last_name_local': '山田',
            'phone_number': '090-9876-5432',
            'address': '大阪府大阪市'
        },
        {
            'email': 'admin@example.com',
            'password_hash': '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/9.8.8.8',  # 'password'
            'first_name_romaji': 'Admin',
            'last_name_romaji': 'User',
            'first_name_local': '管理者',
            'last_name_local': 'ユーザー',
            'phone_number': '090-0000-0000',
            'address': '東京都新宿区'
        }
    ]
    
    user_ids = []
    for user in test_users:
        cursor.execute('''
            INSERT INTO users (email, password_hash, first_name_romaji, last_name_romaji, 
                             first_name_local, last_name_local, phone_number, address, 
                             created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user['email'], user['password_hash'], user['first_name_romaji'], 
            user['last_name_romaji'], user['first_name_local'], user['last_name_local'],
            user['phone_number'], user['address'], now_str, now_str
        ))
        user_ids.append(cursor.lastrowid)
    
    print(f"✅ {len(test_users)} 人のテストユーザーを作成しました")
    
    # 2. ヘルスプロファイルの作成
    health_profiles = [
        {
            'user_id': user_ids[0],  # miyasaka@gmail.com
            'birth_date': '1985-05-15',
            'gender': 'male',
            'blood_type': 'A',
            'region': '東京都',
            'height_cm': 175.0,
            'current_weight_kg': 70.0,
            'target_weight_kg': 68.0,
            'target_body_fat_percentage': 15.0,
            'activity_level': 'moderate',
            'medical_conditions': '高血圧',
            'medications': '降圧剤',
            'allergies': '花粉症',
            'emergency_contact_name': '宮坂花子',
            'emergency_contact_phone': '090-1111-2222',
            'doctor_name': '佐藤医師',
            'doctor_phone': '03-1234-5678',
            'insurance_number': '1234567890'
        },
        {
            'user_id': user_ids[1],  # test@example.com
            'birth_date': '1990-01-01',
            'gender': 'female',
            'blood_type': 'B',
            'region': '大阪府',
            'height_cm': 160.0,
            'current_weight_kg': 55.0,
            'target_weight_kg': 52.0,
            'target_body_fat_percentage': 20.0,
            'activity_level': 'high',
            'medical_conditions': '',
            'medications': '',
            'allergies': '',
            'emergency_contact_name': '山田太郎',
            'emergency_contact_phone': '090-3333-4444',
            'doctor_name': '田中医師',
            'doctor_phone': '06-9876-5432',
            'insurance_number': '0987654321'
        },
        {
            'user_id': user_ids[2],  # admin@example.com
            'birth_date': '1980-12-25',
            'gender': 'male',
            'blood_type': 'O',
            'region': '東京都',
            'height_cm': 180.0,
            'current_weight_kg': 75.0,
            'target_weight_kg': 72.0,
            'target_body_fat_percentage': 12.0,
            'activity_level': 'high',
            'medical_conditions': '',
            'medications': '',
            'allergies': '',
            'emergency_contact_name': '管理者花子',
            'emergency_contact_phone': '090-5555-6666',
            'doctor_name': '鈴木医師',
            'doctor_phone': '03-1111-2222',
            'insurance_number': '1122334455'
        }
    ]
    
    for profile in health_profiles:
        cursor.execute('''
            INSERT INTO user_health_profiles (
                user_id, birth_date, gender, blood_type, region, height_cm,
                current_weight_kg, target_weight_kg, target_body_fat_percentage,
                activity_level, medical_conditions, medications, allergies,
                emergency_contact_name, emergency_contact_phone, doctor_name,
                doctor_phone, insurance_number, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            profile['user_id'], profile['birth_date'], profile['gender'],
            profile['blood_type'], profile['region'], profile['height_cm'],
            profile['current_weight_kg'], profile['target_weight_kg'],
            profile['target_body_fat_percentage'], profile['activity_level'],
            profile['medical_conditions'], profile['medications'],
            profile['allergies'], profile['emergency_contact_name'],
            profile['emergency_contact_phone'], profile['doctor_name'],
            profile['doctor_phone'], profile['insurance_number'],
            now_str, now_str
        ))
    
    print(f"✅ {len(health_profiles)} 件のヘルスプロファイルを作成しました")
    
    # 3. プライバシー設定の作成
    privacy_settings = [
        {'user_id': user_ids[0], 'privacy_level': 'private', 'share_medical_info': False, 'share_contact_info': False, 'share_measurements': False},
        {'user_id': user_ids[1], 'privacy_level': 'public', 'share_medical_info': True, 'share_contact_info': True, 'share_measurements': True},
        {'user_id': user_ids[2], 'privacy_level': 'private', 'share_medical_info': False, 'share_contact_info': False, 'share_measurements': False}
    ]
    
    for setting in privacy_settings:
        cursor.execute('''
            INSERT INTO privacy_settings (
                user_id, privacy_level, share_medical_info, 
                share_contact_info, share_measurements, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            setting['user_id'], setting['privacy_level'],
            setting['share_medical_info'], setting['share_contact_info'],
            setting['share_measurements'], now_str, now_str
        ))
    
    print(f"✅ {len(privacy_settings)} 件のプライバシー設定を作成しました")
    
    # 4. サンプル体組成測定データの作成
    import random
    from datetime import timedelta
    
    for user_id in user_ids:
        # 各ユーザーに過去30日分の測定データを作成
        for i in range(30):
            measurement_date = now - timedelta(days=i)
            weight = 70.0 + random.uniform(-2, 2)  # 体重の変動
            body_fat = 15.0 + random.uniform(-1, 1)  # 体脂肪率の変動
            
            cursor.execute('''
                INSERT INTO body_measurements (
                    user_id, weight_kg, body_fat_percentage, notes, measurement_date, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_id, round(weight, 1), round(body_fat, 1),
                f'朝の測定 - {measurement_date.strftime("%Y-%m-%d")}',
                measurement_date.strftime('%Y-%m-%d %H:%M:%S'),
                now_str
            ))
    
    print(f"✅ 各ユーザーに30日分の体組成測定データを作成しました")
    
    # コミット
    conn.commit()
    print("💾 テストデータを保存しました")
    
    return user_ids

def verify_data(conn):
    """データの検証"""
    cursor = conn.cursor()
    
    # ユーザー数
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    print(f"📊 ユーザー数: {user_count}")
    
    # ヘルスプロファイル数
    cursor.execute('SELECT COUNT(*) FROM user_health_profiles')
    health_count = cursor.fetchone()[0]
    print(f"📊 ヘルスプロファイル数: {health_count}")
    
    # 体組成測定データ数
    cursor.execute('SELECT COUNT(*) FROM body_measurements')
    measurement_count = cursor.fetchone()[0]
    print(f"📊 体組成測定データ数: {measurement_count}")
    
    # プライバシー設定数
    cursor.execute('SELECT COUNT(*) FROM privacy_settings')
    privacy_count = cursor.fetchone()[0]
    print(f"📊 プライバシー設定数: {privacy_count}")
    
    # サンプルデータの表示
    print("\n📋 サンプルユーザーデータ:")
    cursor.execute('''
        SELECT u.id, u.email, u.first_name_local, u.last_name_local,
               h.height_cm, h.current_weight_kg, h.activity_level
        FROM users u
        LEFT JOIN user_health_profiles h ON u.id = h.user_id
        ORDER BY u.id
    ''')
    
    for row in cursor.fetchall():
        print(f"  ID: {row[0]}, Email: {row[1]}, Name: {row[2]} {row[3]}, Height: {row[4]}cm, Weight: {row[5]}kg, Activity: {row[6]}")

if __name__ == "__main__":
    print("🚀 新しいデータベース構造の作成を開始します...")
    
    # データベース作成
    conn = create_database()
    
    # テストデータ作成
    user_ids = create_test_data(conn)
    
    # データ検証
    verify_data(conn)
    
    # 接続終了
    conn.close()
    
    print("\n✅ 新しいデータベース構造の作成が完了しました！")
    print(f"📁 データベースファイル: test.db")
    print(f"👥 テストユーザー数: 3人")
    print(f"📊 体組成測定データ: 90件 (各ユーザー30日分)")
