"""
認証サーバー用のデータベース構造を作成
"""

import os
from sqlmodel import Session, create_engine, text
from datetime import datetime, timezone
from passlib.context import CryptContext

# データベース設定
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://healthcare_user:healthcare_password@localhost:5432/healthcare_db")
engine = create_engine(DATABASE_URL, echo=True)

# パスワードハッシュ
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_auth_database():
    """認証用データベース構造を作成"""
    print("🔧 認証用データベース構造を作成中...")
    
    with Session(engine) as db:
        try:
            # usersテーブルを作成
            db.exec(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    first_name_romaji VARCHAR(100),
                    last_name_romaji VARCHAR(100),
                    first_name_local VARCHAR(100),
                    last_name_local VARCHAR(100),
                    phone_number VARCHAR(20),
                    address TEXT,
                    nickname VARCHAR(100),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    last_login_at TIMESTAMP WITH TIME ZONE,
                    failed_login_attempts INTEGER DEFAULT 0,
                    locked_until TIMESTAMP WITH TIME ZONE
                )
            """))
            
            # インデックスを作成
            db.exec(text("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)"))
            db.exec(text("CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active)"))
            
            db.commit()
            print("✅ usersテーブルを作成しました")
            
            # サンプルユーザーを作成
            create_sample_users(db)
            
        except Exception as e:
            print(f"❌ エラー: {e}")
            db.rollback()
            raise

def create_sample_users(db: Session):
    """サンプルユーザーを作成"""
    print("👤 サンプルユーザーを作成中...")
    
    # 既存のユーザーをチェック
    existing_user = db.exec(text("SELECT id FROM users WHERE email = :email").params(email="miyasaka@gmail.com")).first()
    if existing_user:
        print("✅ miyasaka@gmail.com は既に存在します")
        return
    
    # パスワードハッシュを作成（10文字以上のアルファベット）
    password_hash = pwd_context.hash("password123456789")
    
    # サンプルユーザーを挿入
    sample_users = [
        {
            "email": "miyasaka@gmail.com",
            "password_hash": password_hash,
            "first_name_romaji": "Taro",
            "last_name_romaji": "Miyasaka",
            "first_name_local": "太郎",
            "last_name_local": "宮坂",
            "nickname": "Taro",
            "phone_number": "090-1234-5678",
            "address": "東京都渋谷区",
            "is_active": True
        },
        {
            "email": "test@example.com",
            "password_hash": password_hash,
            "first_name_romaji": "Test",
            "last_name_romaji": "User",
            "first_name_local": "テスト",
            "last_name_local": "ユーザー",
            "nickname": "TestUser",
            "phone_number": "090-9876-5432",
            "address": "大阪府大阪市",
            "is_active": True
        }
    ]
    
    for user_data in sample_users:
        db.exec(text("""
            INSERT INTO users (email, password_hash, first_name_romaji, last_name_romaji,
                             first_name_local, last_name_local, nickname, phone_number, address, is_active)
            VALUES (:email, :password_hash, :first_name_romaji, :last_name_romaji,
                   :first_name_local, :last_name_local, :nickname, :phone_number, :address, :is_active)
        """).params(**user_data))
    
    db.commit()
    print("✅ サンプルユーザーを作成しました")

if __name__ == "__main__":
    create_auth_database()
    print("🎉 認証用データベースの作成が完了しました！")
