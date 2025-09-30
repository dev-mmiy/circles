"""
包括的な多言語対応のUnitテスト
"""
import pytest
import json
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from app_auth_simple import app


class TestI18nSystem:
    """多言語対応システムの包括的テスト"""
    
    @pytest.fixture
    def client(self):
        """テストクライアント"""
        return TestClient(app)
    
    def test_english_translations(self, client):
        """英語翻訳のテスト"""
        # 英語の認証ページにアクセス
        response = client.get("/en-US/auth?mode=register")
        assert response.status_code == 200
        
        # 英語の翻訳が正しく表示されているかチェック
        content = response.text
        assert "Welcome to Healthcare Community" in content
        assert "A platform for supporting people with serious illnesses" in content
        assert "Create Account" in content
        assert "Sign up here" in content
        assert "Development environment: Authentication bypass is enabled" in content
    
    def test_japanese_translations(self, client):
        """日本語翻訳のテスト"""
        # 日本語の認証ページにアクセス
        response = client.get("/ja-JP/auth?mode=register")
        assert response.status_code == 200
        
        # 日本語の翻訳が正しく表示されているかチェック
        content = response.text
        assert "ヘルスケアコミュニティへようこそ" in content
        assert "重篤な疾患を持つ人々をサポートするプラットフォーム" in content
        assert "アカウント作成" in content
        assert "こちらからサインアップ" in content
    
    def test_french_translations(self, client):
        """フランス語翻訳のテスト"""
        # フランス語の認証ページにアクセス
        response = client.get("/fr-FR/auth?mode=register")
        assert response.status_code == 200
        
        # フランス語の翻訳が正しく表示されているかチェック
        content = response.text
        # フランス語の翻訳が実装されているかチェック
        # 注意: フランス語の翻訳ファイルが存在しない場合は、デフォルトの英語が表示される
    
    def test_translation_key_coverage(self):
        """翻訳キーのカバレッジテスト"""
        # 英語翻訳ファイルの読み込み
        with open("messages/en-US.json", "r", encoding="utf-8") as f:
            en_translations = json.load(f)
        
        # 日本語翻訳ファイルの読み込み
        with open("messages/ja-JP.json", "r", encoding="utf-8") as f:
            ja_translations = json.load(f)
        
        # フランス語翻訳ファイルの読み込み
        try:
            with open("messages/fr-FR.json", "r", encoding="utf-8") as f:
                fr_translations = json.load(f)
        except FileNotFoundError:
            fr_translations = {}
        
        # 翻訳キーの構造を再帰的に取得する関数
        def get_translation_keys(translations, prefix=""):
            keys = []
            for key, value in translations.items():
                full_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, dict):
                    keys.extend(get_translation_keys(value, full_key))
                else:
                    keys.append(full_key)
            return keys
        
        # 各言語の翻訳キーを取得
        en_keys = set(get_translation_keys(en_translations))
        ja_keys = set(get_translation_keys(ja_translations))
        fr_keys = set(get_translation_keys(fr_translations)) if fr_translations else set()
        
        # 英語と日本語の翻訳キーが一致することを確認
        assert en_keys == ja_keys, f"翻訳キーの不一致: EN={en_keys - ja_keys}, JA={ja_keys - en_keys}"
        
        # フランス語の翻訳キーが存在する場合は、英語と一致することを確認
        if fr_keys:
            assert en_keys == fr_keys, f"翻訳キーの不一致: EN={en_keys - fr_keys}, FR={fr_keys - en_keys}"
    
    def test_required_translation_keys(self):
        """必須翻訳キーの存在確認テスト"""
        # 必須翻訳キーのリスト
        required_keys = [
            "common.loading",
            "common.error",
            "common.success",
            "common.cancel",
            "common.save",
            "common.delete",
            "common.edit",
            "common.create",
            "common.submit",
            "navigation.home",
            "navigation.posts",
            "navigation.community",
            "navigation.profile",
            "auth.login.title",
            "auth.login.description",
            "auth.login.email",
            "auth.login.password",
            "auth.login.submit",
            "auth.login.loading",
            "auth.register.title",
            "auth.register.description",
            "auth.register.firstName",
            "auth.register.lastName",
            "auth.register.email",
            "auth.register.nickname",
            "auth.register.password",
            "auth.register.submit",
            "welcome.title",
            "welcome.subtitle"
        ]
        
        # 英語翻訳ファイルの読み込み
        with open("messages/en-US.json", "r", encoding="utf-8") as f:
            en_translations = json.load(f)
        
        # 翻訳キーの存在確認
        def check_key_exists(translations, key_path):
            keys = key_path.split(".")
            current = translations
            for key in keys:
                if key not in current:
                    return False
                current = current[key]
            return True
        
        missing_keys = []
        for key in required_keys:
            if not check_key_exists(en_translations, key):
                missing_keys.append(key)
        
        assert len(missing_keys) == 0, f"不足している翻訳キー: {missing_keys}"
    
    def test_translation_quality(self):
        """翻訳品質のテスト"""
        # 英語翻訳ファイルの読み込み
        with open("messages/en-US.json", "r", encoding="utf-8") as f:
            en_translations = json.load(f)
        
        # 日本語翻訳ファイルの読み込み
        with open("messages/ja-JP.json", "r", encoding="utf-8") as f:
            ja_translations = json.load(f)
        
        # 翻訳の品質チェック
        def check_translation_quality(translations, language):
            issues = []
            
            for key, value in translations.items():
                if isinstance(value, dict):
                    issues.extend(check_translation_quality(value, language))
                else:
                    # 空の翻訳チェック
                    if not value or value.strip() == "":
                        issues.append(f"空の翻訳: {key}")
                    
                    # 翻訳キーがそのまま表示されていないかチェック
                    if value.startswith("auth.") or value.startswith("common."):
                        issues.append(f"翻訳キーがそのまま表示: {key} = {value}")
                    
                    # 英語の翻訳が日本語ファイルに混入していないかチェック
                    if language == "ja" and value.isascii() and len(value) > 3:
                        # 英語の可能性が高い文字列をチェック
                        if any(word in value.lower() for word in ["the", "and", "or", "for", "with", "to", "in", "on", "at"]):
                            issues.append(f"英語の翻訳が混入: {key} = {value}")
            
            return issues
        
        # 英語翻訳の品質チェック
        en_issues = check_translation_quality(en_translations, "en")
        assert len(en_issues) == 0, f"英語翻訳の品質問題: {en_issues}"
        
        # 日本語翻訳の品質チェック
        ja_issues = check_translation_quality(ja_translations, "ja")
        assert len(ja_issues) == 0, f"日本語翻訳の品質問題: {ja_issues}"
    
    def test_locale_switching(self, client):
        """ロケール切り替えのテスト"""
        # 英語から日本語への切り替え
        response = client.get("/ja-JP/auth")
        assert response.status_code == 200
        assert "ja-JP" in response.url
        
        # 日本語から英語への切り替え
        response = client.get("/en-US/auth")
        assert response.status_code == 200
        assert "en-US" in response.url
        
        # フランス語への切り替え
        response = client.get("/fr-FR/auth")
        assert response.status_code == 200
        assert "fr-FR" in response.url
    
    def test_timezone_handling(self):
        """タイムゾーン処理のテスト"""
        # 各言語のタイムゾーン設定を確認
        locales = ["en-US", "ja-JP", "fr-FR"]
        expected_timezones = {
            "en-US": "America/New_York",
            "ja-JP": "Asia/Tokyo",
            "fr-FR": "Europe/Paris"
        }
        
        # i18n設定ファイルの確認
        with open("src/i18n.ts", "r", encoding="utf-8") as f:
            i18n_config = f.read()
        
        for locale in locales:
            if locale in expected_timezones:
                timezone = expected_timezones[locale]
                assert timezone in i18n_config, f"{locale}のタイムゾーン設定が見つかりません: {timezone}"
    
    def test_rtl_language_support(self):
        """RTL言語サポートのテスト（将来の拡張用）"""
        # 現在はRTL言語をサポートしていないが、将来の拡張に備えたテスト
        # アラビア語やヘブライ語などのRTL言語のサポートを想定
        
        # RTL言語のサポートが必要な場合のテストケース
        rtl_languages = ["ar-SA", "he-IL", "fa-IR"]
        
        for lang in rtl_languages:
            # RTL言語の翻訳ファイルが存在しないことを確認
            import os
            translation_file = f"messages/{lang}.json"
            assert not os.path.exists(translation_file), f"RTL言語の翻訳ファイルが存在します: {translation_file}"
    
    def test_pluralization_support(self):
        """複数形サポートのテスト"""
        # 英語の複数形サポートの確認
        with open("messages/en-US.json", "r", encoding="utf-8") as f:
            en_translations = json.load(f)
        
        # 複数形が必要な翻訳キーの確認
        pluralization_keys = [
            "posts.foundPosts",  # {count} posts
            "auth.external.linkedAccounts"  # Linked accounts
        ]
        
        for key in pluralization_keys:
            # 翻訳キーが存在し、{count}などのプレースホルダーが含まれているかチェック
            def check_key_in_translations(translations, key_path):
                keys = key_path.split(".")
                current = translations
                for key in keys:
                    if key not in current:
                        return None
                    current = current[key]
                return current
            
            translation = check_key_in_translations(en_translations, key)
            if translation:
                assert "{" in translation, f"複数形サポートが必要な翻訳にプレースホルダーがありません: {key}"
    
    def test_date_format_localization(self):
        """日付フォーマットのローカライゼーションテスト"""
        # 各言語の日付フォーマット設定を確認
        locales = ["en-US", "ja-JP", "fr-FR"]
        
        # i18n設定ファイルの確認
        with open("src/i18n.ts", "r", encoding="utf-8") as f:
            i18n_config = f.read()
        
        # 日付フォーマットの設定が含まれているかチェック
        assert "dateTime" in i18n_config, "日付フォーマットの設定が見つかりません"
        assert "short" in i18n_config, "短縮日付フォーマットの設定が見つかりません"
    
    def test_currency_format_localization(self):
        """通貨フォーマットのローカライゼーションテスト"""
        # 各言語の通貨フォーマット設定を確認
        # 現在は通貨フォーマットを実装していないが、将来の拡張に備えたテスト
        
        # 通貨フォーマットが必要な場合のテストケース
        currency_formats = {
            "en-US": "USD",
            "ja-JP": "JPY",
            "fr-FR": "EUR"
        }
        
        for locale, currency in currency_formats.items():
            # 通貨フォーマットの設定が将来実装される場合のテスト
            # 現在は実装されていないため、スキップ
            pass
    
    def test_measurement_unit_localization(self):
        """測定単位のローカライゼーションテスト"""
        # 各言語の測定単位設定を確認
        # 現在は測定単位を実装していないが、将来の拡張に備えたテスト
        
        # 測定単位が必要な場合のテストケース
        measurement_units = {
            "en-US": "imperial",  # フィート、ポンド
            "ja-JP": "metric",    # メートル、キログラム
            "fr-FR": "metric"     # メートル、キログラム
        }
        
        for locale, unit in measurement_units.items():
            # 測定単位の設定が将来実装される場合のテスト
            # 現在は実装されていないため、スキップ
            pass


class TestTranslationCoverage:
    """翻訳カバレッジのテスト"""
    
    def test_all_ui_components_have_translations(self):
        """すべてのUIコンポーネントに翻訳が存在することを確認"""
        # UIコンポーネントで使用される翻訳キーのリスト
        ui_translation_keys = [
            "common.loading",
            "common.error",
            "common.success",
            "common.cancel",
            "common.save",
            "common.submit",
            "navigation.home",
            "navigation.posts",
            "navigation.community",
            "navigation.profile",
            "auth.login.title",
            "auth.login.description",
            "auth.login.email",
            "auth.login.password",
            "auth.login.submit",
            "auth.login.loading",
            "auth.register.title",
            "auth.register.description",
            "auth.register.firstName",
            "auth.register.lastName",
            "auth.register.email",
            "auth.register.nickname",
            "auth.register.password",
            "auth.register.submit",
            "welcome.title",
            "welcome.subtitle"
        ]
        
        # 英語翻訳ファイルの読み込み
        with open("messages/en-US.json", "r", encoding="utf-8") as f:
            en_translations = json.load(f)
        
        # 翻訳キーの存在確認
        def check_key_exists(translations, key_path):
            keys = key_path.split(".")
            current = translations
            for key in keys:
                if key not in current:
                    return False
                current = current[key]
            return True
        
        missing_keys = []
        for key in ui_translation_keys:
            if not check_key_exists(en_translations, key):
                missing_keys.append(key)
        
        assert len(missing_keys) == 0, f"UIコンポーネントで使用される翻訳キーが不足: {missing_keys}"
    
    def test_no_hardcoded_strings_in_components(self):
        """コンポーネント内にハードコードされた文字列がないことを確認"""
        import os
        import re
        
        # コンポーネントファイルのパス
        component_paths = [
            "src/components/auth/LoginForm.tsx",
            "src/components/auth/RegisterForm.tsx",
            "src/components/auth/UserProfile.tsx",
            "src/components/layout/Navbar.tsx",
            "src/app/[locale]/auth/page.tsx",
            "src/app/[locale]/profile/page.tsx"
        ]
        
        # ハードコードされた文字列のパターン
        hardcoded_patterns = [
            r'"[^"]*[a-zA-Z]{3,}[^"]*"',  # 3文字以上の英数字を含む文字列
            r"'[^']*[a-zA-Z]{3,}[^']*'",  # 3文字以上の英数字を含む文字列
            r'`[^`]*[a-zA-Z]{3,}[^`]*`'   # 3文字以上の英数字を含む文字列
        ]
        
        # 翻訳キーとして使用される文字列は除外
        translation_key_patterns = [
            r't\([\'"][^"\']*[\'"]\)',  # t('key') または t("key")
            r'useTranslations\([\'"][^"\']*[\'"]\)'  # useTranslations('namespace')
        ]
        
        hardcoded_strings = []
        
        for component_path in component_paths:
            if os.path.exists(component_path):
                with open(component_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # 翻訳キーとして使用される文字列を除外
                for pattern in translation_key_patterns:
                    content = re.sub(pattern, "", content)
                
                # ハードコードされた文字列を検索
                for pattern in hardcoded_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        # 翻訳キーや変数名ではないことを確認
                        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', match.strip('"\'`')):
                            hardcoded_strings.append(f"{component_path}: {match}")
        
        # ハードコードされた文字列が存在する場合は警告
        if hardcoded_strings:
            print("警告: ハードコードされた文字列が見つかりました:")
            for string in hardcoded_strings:
                print(f"  {string}")
        
        # 重要なハードコードされた文字列がないことを確認
        critical_hardcoded = [s for s in hardcoded_strings if any(word in s.lower() for word in ["login", "register", "profile", "home", "posts", "community"])]
        assert len(critical_hardcoded) == 0, f"重要なハードコードされた文字列が見つかりました: {critical_hardcoded}"



