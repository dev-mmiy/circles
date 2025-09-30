#!/usr/bin/env python3
"""
包括的なテスト実行スクリプト
"""
import os
import sys
import subprocess
import argparse
import json
from pathlib import Path


def run_command(command, description):
    """コマンドを実行し、結果を表示"""
    print(f"\n{'='*60}")
    print(f"実行中: {description}")
    print(f"コマンド: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print("✅ 成功")
        if result.stdout:
            print("出力:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ 失敗")
        print(f"エラーコード: {e.returncode}")
        if e.stdout:
            print("標準出力:")
            print(e.stdout)
        if e.stderr:
            print("標準エラー:")
            print(e.stderr)
        return False


def check_environment():
    """環境の確認"""
    print("🔍 環境確認中...")
    
    # Pythonのバージョン確認
    python_version = sys.version_info
    print(f"Pythonバージョン: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 必要なファイルの存在確認
    required_files = [
        "tests/test_auth_comprehensive.py",
        "tests/test_i18n_comprehensive.py",
        "tests/test_api_integration_comprehensive.py",
        "tests/test_translation_coverage.py",
        "pytest_comprehensive.ini",
        "messages/en-US.json",
        "messages/ja-JP.json"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ 必要なファイルが見つかりません:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    
    print("✅ 環境確認完了")
    return True


def install_dependencies():
    """依存関係のインストール"""
    print("📦 依存関係のインストール中...")
    
    # 必要なパッケージのリスト
    packages = [
        "pytest>=7.4.0",
        "pytest-cov>=4.1.0",
        "pytest-timeout>=2.1.0",
        "pytest-xdist>=3.3.0",
        "pytest-html>=3.2.0",
        "pytest-json-report>=1.5.0",
        "coverage>=7.3.0",
        "psutil>=5.9.0"
    ]
    
    for package in packages:
        command = f"pip install {package}"
        if not run_command(command, f"インストール: {package}"):
            print(f"⚠️  {package}のインストールに失敗しました")
    
    print("✅ 依存関係のインストール完了")


def run_auth_tests():
    """認証システムのテスト実行"""
    print("🔐 認証システムのテスト実行中...")
    
    command = "pytest tests/test_auth_comprehensive.py -v --tb=short --cov=auth_models,auth_service,auth_endpoints --cov-report=term-missing"
    return run_command(command, "認証システムテスト")


def run_i18n_tests():
    """多言語対応のテスト実行"""
    print("🌐 多言語対応のテスト実行中...")
    
    command = "pytest tests/test_i18n_comprehensive.py -v --tb=short"
    return run_command(command, "多言語対応テスト")


def run_api_tests():
    """API統合のテスト実行"""
    print("🔌 API統合のテスト実行中...")
    
    command = "pytest tests/test_api_integration_comprehensive.py -v --tb=short"
    return run_command(command, "API統合テスト")


def run_translation_tests():
    """翻訳カバレッジのテスト実行"""
    print("📝 翻訳カバレッジのテスト実行中...")
    
    command = "pytest tests/test_translation_coverage.py -v --tb=short"
    return run_command(command, "翻訳カバレッジテスト")


def run_all_tests():
    """すべてのテスト実行"""
    print("🚀 包括的なテスト実行中...")
    
    command = "pytest tests/ -v --tb=short --cov=. --cov-report=html --cov-report=term-missing --cov-report=xml --cov-fail-under=80"
    return run_command(command, "包括的テスト")


def generate_test_report():
    """テストレポートの生成"""
    print("📊 テストレポートの生成中...")
    
    # HTMLレポートの確認
    if os.path.exists("htmlcov/index.html"):
        print("✅ HTMLカバレッジレポートが生成されました: htmlcov/index.html")
    
    # XMLレポートの確認
    if os.path.exists("coverage.xml"):
        print("✅ XMLカバレッジレポートが生成されました: coverage.xml")
    
    # テスト結果のサマリー
    print("\n📈 テスト結果サマリー:")
    print("=" * 50)
    
    # カバレッジレポートの読み込み
    if os.path.exists("coverage.xml"):
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse("coverage.xml")
            root = tree.getroot()
            
            # カバレッジ情報の取得
            for package in root.findall(".//package"):
                name = package.get("name", "Unknown")
                line_rate = float(package.get("line-rate", 0))
                branch_rate = float(package.get("branch-rate", 0))
                
                print(f"📦 {name}:")
                print(f"  行カバレッジ: {line_rate:.1%}")
                print(f"  分岐カバレッジ: {branch_rate:.1%}")
                print()
        except Exception as e:
            print(f"⚠️  カバレッジレポートの解析に失敗: {e}")


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="包括的なテスト実行スクリプト")
    parser.add_argument("--auth", action="store_true", help="認証システムのテストのみ実行")
    parser.add_argument("--i18n", action="store_true", help="多言語対応のテストのみ実行")
    parser.add_argument("--api", action="store_true", help="API統合のテストのみ実行")
    parser.add_argument("--translation", action="store_true", help="翻訳カバレッジのテストのみ実行")
    parser.add_argument("--all", action="store_true", help="すべてのテストを実行")
    parser.add_argument("--install", action="store_true", help="依存関係をインストール")
    parser.add_argument("--report", action="store_true", help="テストレポートを生成")
    
    args = parser.parse_args()
    
    print("🧪 Healthcare Community Platform - 包括的テストスイート")
    print("=" * 60)
    
    # 環境確認
    if not check_environment():
        print("❌ 環境確認に失敗しました")
        sys.exit(1)
    
    # 依存関係のインストール
    if args.install:
        install_dependencies()
    
    # テスト実行
    success = True
    
    if args.auth or args.all:
        success &= run_auth_tests()
    
    if args.i18n or args.all:
        success &= run_i18n_tests()
    
    if args.api or args.all:
        success &= run_api_tests()
    
    if args.translation or args.all:
        success &= run_translation_tests()
    
    if args.all:
        success &= run_all_tests()
    
    # テストレポートの生成
    if args.report or args.all:
        generate_test_report()
    
    # 結果の表示
    print("\n" + "=" * 60)
    if success:
        print("🎉 すべてのテストが成功しました！")
        print("📊 詳細なレポートは htmlcov/index.html で確認できます")
    else:
        print("❌ 一部のテストが失敗しました")
        print("🔍 詳細なログを確認してください")
    
    print("=" * 60)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())




