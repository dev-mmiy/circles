#!/usr/bin/env python3
"""
bcrypt問題の修正スクリプト
"""
import os
import sys
from passlib.context import CryptContext
from passlib.hash import bcrypt

def test_bcrypt_issues():
    """bcryptの問題をテスト"""
    print("🔍 bcrypt問題の診断")
    
    # パスワード長制限のテスト
    test_passwords = [
        "test123",           # 7文字（短すぎる）
        "test1234",          # 8文字（最小要件）
        "test12345",         # 9文字
        "test123456789012345678901234567890123456789012345678901234567890123456789012",  # 72文字以上
        "テストパスワード123",  # 日本語（バイト数が多い）
    ]
    
    print("\n📏 パスワード長制限のテスト:")
    for password in test_passwords:
        try:
            # bcryptでハッシュ化
            hashed = bcrypt.hash(password)
            print(f"✅ '{password}' ({len(password)}文字, {len(password.encode('utf-8'))}バイト) -> 成功")
        except Exception as e:
            print(f"❌ '{password}' ({len(password)}文字, {len(password.encode('utf-8'))}バイト) -> エラー: {e}")
    
    # passlibの設定テスト
    print("\n🔧 passlib設定のテスト:")
    try:
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        test_password = "test1234"
        hashed = pwd_context.hash(test_password)
        verified = pwd_context.verify(test_password, hashed)
        print(f"✅ passlib設定: 成功 (検証: {verified})")
    except Exception as e:
        print(f"❌ passlib設定: エラー: {e}")

def fix_auth_service():
    """認証サービスの修正"""
    print("\n🔧 認証サービスの修正")
    
    # 修正された認証サービスコード
    fixed_code = '''
# 修正された認証サービス
from passlib.context import CryptContext
import hashlib

# bcryptの問題を回避するための設定
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__default_rounds=12,
    bcrypt__min_rounds=10,
    bcrypt__max_rounds=15
)

def create_password_hash(self, password: str) -> str:
    """パスワードハッシュ作成（bcrypt問題回避）"""
    # パスワードが72バイトを超える場合は事前にハッシュ化
    if len(password.encode('utf-8')) > 72:
        # SHA256でハッシュ化してからbcryptでハッシュ化
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        return pwd_context.hash(password_hash)
    else:
        return pwd_context.hash(password)

def verify_password(self, plain_password: str, hashed_password: str) -> bool:
    """パスワード検証（bcrypt問題回避）"""
    try:
        # 直接検証を試行
        if pwd_context.verify(plain_password, hashed_password):
            return True
        
        # 72バイトを超えるパスワードの場合はSHA256ハッシュで検証
        if len(plain_password.encode('utf-8')) > 72:
            password_hash = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
            return pwd_context.verify(password_hash, hashed_password)
        
        return False
    except Exception as e:
        print(f"パスワード検証エラー: {e}")
        return False
'''
    
    print("修正された認証サービスコード:")
    print(fixed_code)

def alternative_solutions():
    """代替ソリューション"""
    print("\n🔄 代替ソリューション")
    
    solutions = [
        {
            "name": "Argon2の使用",
            "description": "bcryptの代わりにArgon2を使用",
            "code": '''
from passlib.context import CryptContext

# Argon2を使用（より安全で現代的なハッシュ関数）
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
'''
        },
        {
            "name": "PBKDF2の使用",
            "description": "bcryptの代わりにPBKDF2を使用",
            "code": '''
from passlib.context import CryptContext

# PBKDF2を使用（パスワード長制限なし）
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
'''
        },
        {
            "name": "bcryptの設定調整",
            "description": "bcryptの設定を調整して問題を回避",
            "code": '''
from passlib.context import CryptContext

# bcryptの設定を調整
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__default_rounds=10,  # ラウンド数を下げる
    bcrypt__min_rounds=8,
    bcrypt__max_rounds=12
)
'''
        }
    ]
    
    for i, solution in enumerate(solutions, 1):
        print(f"\n{i}. {solution['name']}")
        print(f"   {solution['description']}")
        print(f"   コード: {solution['code']}")

def main():
    """メイン関数"""
    print("🔧 bcrypt問題の診断と修正")
    print("=" * 50)
    
    # 問題の診断
    test_bcrypt_issues()
    
    # 修正方法の提示
    fix_auth_service()
    
    # 代替ソリューション
    alternative_solutions()
    
    print("\n" + "=" * 50)
    print("📝 推奨解決方法:")
    print("1. パスワード長を72バイト以下に制限")
    print("2. 長いパスワードは事前にSHA256でハッシュ化")
    print("3. Argon2やPBKDF2への移行を検討")
    print("4. 開発環境では認証スルー機能を使用")

if __name__ == "__main__":
    main()




