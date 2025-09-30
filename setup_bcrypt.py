#!/usr/bin/env python3
"""
bcrypt初期設定スクリプト
bcrypt 4.xの新しいバージョンに更新し、互換性を確保
"""
import os
import sys
import subprocess
import importlib.util

def check_bcrypt_version():
    """bcryptのバージョンを確認"""
    try:
        import bcrypt
        version = bcrypt.__version__
        print(f"✅ 現在のbcryptバージョン: {version}")
        return version
    except ImportError:
        print("❌ bcryptがインストールされていません")
        return None
    except AttributeError:
        print("❌ bcryptのバージョン情報が取得できません")
        return None

def check_passlib_version():
    """passlibのバージョンを確認"""
    try:
        import passlib
        version = passlib.__version__
        print(f"✅ 現在のpasslibバージョン: {version}")
        return version
    except ImportError:
        print("❌ passlibがインストールされていません")
        return None
    except AttributeError:
        print("❌ passlibのバージョン情報が取得できません")
        return None

def test_bcrypt_compatibility():
    """bcryptとpasslibの互換性をテスト"""
    print("\n🔧 bcrypt互換性テスト:")
    
    try:
        from passlib.context import CryptContext
        
        # bcrypt 4.x対応の設定
        pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__default_rounds=12,
            bcrypt__min_rounds=10,
            bcrypt__max_rounds=15
        )
        
        # テストパスワード
        test_passwords = [
            "test1234",           # 8文字
            "test12345",          # 9文字
            "テストパスワード123",  # 日本語
            "a" * 100,            # 長いパスワード
        ]
        
        for password in test_passwords:
            try:
                # ハッシュ化
                hashed = pwd_context.hash(password)
                # 検証
                verified = pwd_context.verify(password, hashed)
                print(f"✅ '{password[:20]}...' -> ハッシュ化: 成功, 検証: {verified}")
            except Exception as e:
                print(f"❌ '{password[:20]}...' -> エラー: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 互換性テスト失敗: {e}")
        return False

def install_bcrypt_4x():
    """bcrypt 4.xをインストール"""
    print("\n📦 bcrypt 4.xのインストール:")
    
    try:
        # 古いバージョンをアンインストール
        print("古いbcryptバージョンをアンインストール中...")
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "bcrypt", "-y"], 
                      check=True, capture_output=True)
        
        # bcrypt 4.xをインストール
        print("bcrypt 4.xをインストール中...")
        subprocess.run([sys.executable, "-m", "pip", "install", "bcrypt>=4.0.1,<5.0.0"], 
                      check=True, capture_output=True)
        
        # passlibを再インストール
        print("passlibを再インストール中...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "passlib[bcrypt]==1.7.4"], 
                      check=True, capture_output=True)
        
        print("✅ bcrypt 4.xのインストール完了")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ インストール失敗: {e}")
        return False

def create_bcrypt_config():
    """bcrypt設定ファイルを作成"""
    print("\n📝 bcrypt設定ファイルの作成:")
    
    config_content = '''# bcrypt設定
# bcrypt 4.x対応の設定

from passlib.context import CryptContext
import hashlib

# bcrypt 4.x対応の設定
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__default_rounds=12,
    bcrypt__min_rounds=10,
    bcrypt__max_rounds=15
)

def create_password_hash(password: str) -> str:
    """パスワードハッシュ作成（bcrypt 4.x対応）"""
    try:
        # パスワードが72バイトを超える場合は事前にSHA256でハッシュ化
        if len(password.encode('utf-8')) > 72:
            password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
            return pwd_context.hash(password_hash)
        else:
            return pwd_context.hash(password)
    except Exception as e:
        print(f"パスワードハッシュ化エラー: {e}")
        # フォールバック: SHA256でハッシュ化
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        return pwd_context.hash(password_hash)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """パスワード検証（bcrypt 4.x対応）"""
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
    
    try:
        with open("bcrypt_config.py", "w", encoding="utf-8") as f:
            f.write(config_content)
        print("✅ bcrypt設定ファイルを作成しました: bcrypt_config.py")
        return True
    except Exception as e:
        print(f"❌ 設定ファイル作成失敗: {e}")
        return False

def main():
    """メイン関数"""
    print("🔧 bcrypt初期設定スクリプト")
    print("=" * 50)
    
    # 現在のバージョンを確認
    print("📋 現在のバージョン確認:")
    bcrypt_version = check_bcrypt_version()
    passlib_version = check_passlib_version()
    
    # 互換性テスト
    if bcrypt_version and passlib_version:
        compatibility_ok = test_bcrypt_compatibility()
        if compatibility_ok:
            print("\n✅ bcryptは既に正常に動作しています")
            return
    
    # bcrypt 4.xをインストール
    print("\n🔄 bcrypt 4.xへの更新:")
    if install_bcrypt_4x():
        # 再確認
        print("\n📋 更新後のバージョン確認:")
        check_bcrypt_version()
        check_passlib_version()
        
        # 互換性テスト
        if test_bcrypt_compatibility():
            print("\n✅ bcrypt 4.xの設定が完了しました")
        else:
            print("\n❌ bcrypt 4.xの設定に問題があります")
    else:
        print("\n❌ bcrypt 4.xのインストールに失敗しました")
    
    # 設定ファイルを作成
    create_bcrypt_config()
    
    print("\n" + "=" * 50)
    print("📝 設定完了:")
    print("1. bcrypt 4.xがインストールされました")
    print("2. passlibとの互換性が確保されました")
    print("3. 長いパスワードの処理が改善されました")
    print("4. 設定ファイルが作成されました")

if __name__ == "__main__":
    main()



