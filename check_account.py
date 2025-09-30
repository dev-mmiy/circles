#!/usr/bin/env python3
"""
登録されたアカウントの確認スクリプト
"""
import os
import sys
from sqlmodel import Session, create_engine, SQLModel, select
from auth_models import Account, UserProfile, UserRoleAssignment


def check_account(email):
    """指定されたメールアドレスのアカウントを確認"""
    print(f"🔍 アカウント確認中: {email}")
    
    # データベース接続
    database_url = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    engine = create_engine(database_url, echo=False, connect_args={"check_same_thread": False})
    
    with Session(engine) as session:
        # アカウントを検索
        account = session.exec(select(Account).where(Account.email == email)).first()
        
        if account:
            print(f"✅ アカウントが見つかりました:")
            print(f"   ID: {account.id}")
            print(f"   Email: {account.email}")
            print(f"   Status: {account.status}")
            print(f"   Created: {account.created_at}")
            print(f"   Last Login: {account.last_login_at}")
            
            # プロフィール情報を取得
            profile = session.exec(select(UserProfile).where(UserProfile.account_id == account.id)).first()
            if profile:
                print(f"   Profile:")
                print(f"     Nickname: {profile.nickname}")
                print(f"     First Name: {profile.first_name}")
                print(f"     Last Name: {profile.last_name}")
                print(f"     Primary Condition: {profile.primary_condition}")
                print(f"     Language: {profile.language}")
                print(f"     Timezone: {profile.timezone}")
            
            # ロール情報を取得
            roles = session.exec(select(UserRoleAssignment).where(UserRoleAssignment.account_id == account.id)).all()
            if roles:
                print(f"   Roles:")
                for role in roles:
                    print(f"     - {role.role} (granted: {role.granted_at})")
            else:
                print(f"   Roles: なし")
            
            return True
        else:
            print(f"❌ アカウントが見つかりませんでした: {email}")
            return False


def list_all_accounts():
    """すべてのアカウントを一覧表示"""
    print(f"📋 すべてのアカウント一覧:")
    
    # データベース接続
    database_url = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    engine = create_engine(database_url, echo=False, connect_args={"check_same_thread": False})
    
    with Session(engine) as session:
        # すべてのアカウントを取得
        accounts = session.exec(select(Account)).all()
        
        if accounts:
            for account in accounts:
                print(f"   - {account.email} (ID: {account.id}, Status: {account.status})")
        else:
            print("   アカウントが見つかりませんでした")


def main():
    """メイン関数"""
    print("🔍 Healthcare Community Platform - アカウント確認")
    
    # 環境変数の設定
    os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
    
    # 指定されたメールアドレスを確認
    email = "miyasaka@gmail.com"
    found = check_account(email)
    
    print("\n" + "="*60)
    
    # すべてのアカウントを一覧表示
    list_all_accounts()
    
    print("\n" + "="*60)
    if found:
        print(f"✅ {email} のアカウントが登録されています")
    else:
        print(f"❌ {email} のアカウントが見つかりませんでした")


if __name__ == "__main__":
    main()




