#!/usr/bin/env python3
"""
健康データ管理機能のテスト実行スクリプト
"""

import subprocess
import sys
import os


def run_tests():
    """テストを実行"""
    print("🧪 健康データ管理機能のテストを開始します...")
    
    # テストファイルのリスト
    test_files = [
        "tests/test_datetime_utils.py",
        "tests/test_health_data_management.py",
        "tests/test_frontend_health_components.py"
    ]
    
    # 各テストファイルを実行
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\n📋 {test_file} を実行中...")
            try:
                result = subprocess.run([
                    sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ {test_file} - 成功")
                else:
                    print(f"❌ {test_file} - 失敗")
                    print("STDOUT:", result.stdout)
                    print("STDERR:", result.stderr)
                    
            except Exception as e:
                print(f"❌ {test_file} - エラー: {e}")
        else:
            print(f"⚠️ {test_file} が見つかりません")
    
    print("\n🎉 テスト実行完了！")


def run_specific_test(test_name):
    """特定のテストを実行"""
    print(f"🧪 {test_name} のテストを実行します...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", test_name, "-v", "--tb=short"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {test_name} - 成功")
        else:
            print(f"❌ {test_name} - 失敗")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            
    except Exception as e:
        print(f"❌ {test_name} - エラー: {e}")


def run_coverage_test():
    """カバレッジ付きテストを実行"""
    print("🧪 カバレッジ付きテストを実行します...")
    
    try:
        # カバレッジ付きでテストを実行
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/test_datetime_utils.py",
            "tests/test_health_data_management.py",
            "--cov=datetime_utils",
            "--cov=simple_user_profile_api",
            "--cov-report=html",
            "--cov-report=term"
        ], capture_output=True, text=True)
        
        print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
    except Exception as e:
        print(f"❌ カバレッジテスト - エラー: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "coverage":
            run_coverage_test()
        else:
            run_specific_test(sys.argv[1])
    else:
        run_tests()
