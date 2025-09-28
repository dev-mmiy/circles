#!/usr/bin/env python3
"""
開発環境用テストアカウント作成スクリプト
"""
import os
import sys
from sqlmodel import Session, create_engine, SQLModel
from auth_models import Account, UserProfile, UserRoleAssignment, UserRegister
from auth_service import AuthService
from datetime import datetime, timezone


def create_test_accounts():
    """テスト用アカウントを作成"""
    print("🧪 テスト用アカウントを作成中...")
    
    # データベース接続
    database_url = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    engine = create_engine(database_url, echo=False, connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        auth_service = AuthService(session)
        
        # テスト用アカウントのデータ
        test_accounts = [
            {
                "email": "test@example.com",
                "password": "test123",
                "nickname": "testuser",
                "first_name": "Test",
                "last_name": "User",
                "primary_condition": "Test Condition"
            },
            {
                "email": "admin@example.com",
                "password": "admin123",
                "nickname": "admin",
                "first_name": "Admin",
                "last_name": "User",
                "primary_condition": "Administrator"
            },
            {
                "email": "patient@example.com",
                "password": "patient123",
                "nickname": "patient",
                "first_name": "Patient",
                "last_name": "User",
                "primary_condition": "Chronic Condition"
            },
            {
                "email": "doctor@example.com",
                "password": "doctor123",
                "nickname": "doctor",
                "first_name": "Doctor",
                "last_name": "User",
                "primary_condition": "Medical Professional"
            }
        ]
        
        created_accounts = []
        
        for account_data in test_accounts:
            try:
                # 既存のアカウントをチェック
                existing_account = session.query(Account).filter(
                    Account.email == account_data["email"]
                ).first()
                
                if existing_account:
                    print(f"⚠️  アカウントが既に存在します: {account_data['email']}")
                    continue
                
                # アカウント作成
                user_register = UserRegister(**account_data)
                auth_response = auth_service.register_user(user_register)
                created_accounts.append({
                    "email": account_data["email"],
                    "nickname": account_data["nickname"],
                    "password": account_data["password"],
                    "account_id": auth_response.user.account_id
                })
                
                print(f"✅ アカウント作成完了: {account_data['email']}")
                
            except Exception as e:
                print(f"❌ アカウント作成失敗: {account_data['email']} - {e}")
        
        # 管理者ロールの追加
        admin_account = session.query(Account).filter(
            Account.email == "admin@example.com"
        ).first()
        
        if admin_account:
            # 既存のロールを削除
            session.query(UserRoleAssignment).filter(
                UserRoleAssignment.account_id == admin_account.id
            ).delete()
            
            # 管理者ロールを追加
            admin_role = UserRoleAssignment(
                account_id=admin_account.id,
                role="admin",
                assigned_at=datetime.now(timezone.utc)
            )
            session.add(admin_role)
            session.commit()
            print("✅ 管理者ロールを追加しました")
        
        # 医師ロールの追加
        doctor_account = session.query(Account).filter(
            Account.email == "doctor@example.com"
        ).first()
        
        if doctor_account:
            # 既存のロールを削除
            session.query(UserRoleAssignment).filter(
                UserRoleAssignment.account_id == doctor_account.id
            ).delete()
            
            # 医師ロールを追加
            doctor_role = UserRoleAssignment(
                account_id=doctor_account.id,
                role="doctor",
                assigned_at=datetime.now(timezone.utc)
            )
            session.add(doctor_role)
            session.commit()
            print("✅ 医師ロールを追加しました")
        
        return created_accounts


def print_test_accounts(accounts):
    """テストアカウント情報を表示"""
    print("\n" + "="*60)
    print("🧪 開発環境用テストアカウント")
    print("="*60)
    
    for i, account in enumerate(accounts, 1):
        print(f"\n{i}. {account['nickname'].upper()} アカウント")
        print(f"   Email: {account['email']}")
        print(f"   Password: {account['password']}")
        print(f"   Account ID: {account['account_id']}")
    
    print("\n" + "="*60)
    print("📝 使用方法:")
    print("1. フロントエンドでログイン: http://localhost:3000/en-US/auth")
    print("2. 上記のEmail/Passwordでログイン")
    print("3. 開発環境では認証スルーも有効")
    print("="*60)


def main():
    """メイン関数"""
    print("🚀 Healthcare Community Platform - テストアカウント作成")
    
    # 環境変数の設定
    os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
    os.environ.setdefault("SECRET_KEY", "test-secret-key")
    
    try:
        # テストアカウント作成
        accounts = create_test_accounts()
        
        if accounts:
            print_test_accounts(accounts)
        else:
            print("❌ テストアカウントの作成に失敗しました")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
