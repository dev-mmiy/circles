"""
翻訳カバレッジの包括的テスト
"""
import pytest
import json
import os
import re
from pathlib import Path


class TestTranslationCoverage:
    """翻訳カバレッジの包括的テスト"""
    
    def test_all_languages_have_same_structure(self):
        """すべての言語で翻訳構造が一致することを確認"""
        # 翻訳ファイルのパス
        translation_files = {
            "en-US": "messages/en-US.json",
            "ja-JP": "messages/ja-JP.json",
            "fr-FR": "messages/fr-FR.json"
        }
        
        # 各言語の翻訳ファイルを読み込み
        translations = {}
        for locale, file_path in translation_files.items():
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    translations[locale] = json.load(f)
            else:
                pytest.skip(f"翻訳ファイルが見つかりません: {file_path}")
        
        # 翻訳キーの構造を再帰的に取得する関数
        def get_translation_structure(translations, prefix=""):
            structure = {}
            for key, value in translations.items():
                full_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, dict):
                    structure[key] = get_translation_structure(value, full_key)
                else:
                    structure[key] = type(value).__name__
            return structure
        
        # 各言語の翻訳構造を取得
        structures = {}
        for locale, translation in translations.items():
            structures[locale] = get_translation_structure(translation)
        
        # 構造が一致することを確認
        base_structure = structures["en-US"]
        for locale, structure in structures.items():
            if locale != "en-US":
                assert structure == base_structure, f"{locale}の翻訳構造が英語と一致しません"
    
    def test_no_missing_translations(self):
        """不足している翻訳がないことを確認"""
        # 翻訳ファイルのパス
        translation_files = {
            "en-US": "messages/en-US.json",
            "ja-JP": "messages/ja-JP.json",
            "fr-FR": "messages/fr-FR.json"
        }
        
        # 各言語の翻訳ファイルを読み込み
        translations = {}
        for locale, file_path in translation_files.items():
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    translations[locale] = json.load(f)
        
        # 英語を基準として翻訳キーを取得
        def get_all_keys(translations, prefix=""):
            keys = []
            for key, value in translations.items():
                full_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, dict):
                    keys.extend(get_all_keys(value, full_key))
                else:
                    keys.append(full_key)
            return keys
        
        en_keys = set(get_all_keys(translations["en-US"]))
        
        # 各言語で不足している翻訳キーをチェック
        for locale, translation in translations.items():
            if locale != "en-US":
                locale_keys = set(get_all_keys(translation))
                missing_keys = en_keys - locale_keys
                assert len(missing_keys) == 0, f"{locale}で不足している翻訳キー: {missing_keys}"
    
    def test_no_extra_translations(self):
        """余分な翻訳がないことを確認"""
        # 翻訳ファイルのパス
        translation_files = {
            "en-US": "messages/en-US.json",
            "ja-JP": "messages/ja-JP.json",
            "fr-FR": "messages/fr-FR.json"
        }
        
        # 各言語の翻訳ファイルを読み込み
        translations = {}
        for locale, file_path in translation_files.items():
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    translations[locale] = json.load(f)
        
        # 英語を基準として翻訳キーを取得
        def get_all_keys(translations, prefix=""):
            keys = []
            for key, value in translations.items():
                full_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, dict):
                    keys.extend(get_all_keys(value, full_key))
                else:
                    keys.append(full_key)
            return keys
        
        en_keys = set(get_all_keys(translations["en-US"]))
        
        # 各言語で余分な翻訳キーをチェック
        for locale, translation in translations.items():
            if locale != "en-US":
                locale_keys = set(get_all_keys(translation))
                extra_keys = locale_keys - en_keys
                assert len(extra_keys) == 0, f"{locale}で余分な翻訳キー: {extra_keys}"
    
    def test_translation_quality_standards(self):
        """翻訳品質基準のテスト"""
        # 翻訳ファイルのパス
        translation_files = {
            "en-US": "messages/en-US.json",
            "ja-JP": "messages/ja-JP.json",
            "fr-FR": "messages/fr-FR.json"
        }
        
        # 各言語の翻訳ファイルを読み込み
        translations = {}
        for locale, file_path in translation_files.items():
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    translations[locale] = json.load(f)
        
        # 翻訳品質のチェック
        for locale, translation in translations.items():
            self._check_translation_quality(translation, locale)
    
    def _check_translation_quality(self, translations, locale):
        """翻訳品質のチェック"""
        issues = []
        
        def check_recursive(translations, prefix=""):
            for key, value in translations.items():
                full_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, dict):
                    check_recursive(value, full_key)
                else:
                    # 空の翻訳チェック
                    if not value or value.strip() == "":
                        issues.append(f"空の翻訳: {full_key}")
                    
                    # 翻訳キーがそのまま表示されていないかチェック
                    if value.startswith("auth.") or value.startswith("common."):
                        issues.append(f"翻訳キーがそのまま表示: {full_key} = {value}")
                    
                    # 英語の翻訳が日本語ファイルに混入していないかチェック
                    if locale == "ja-JP" and value.isascii() and len(value) > 3:
                        if any(word in value.lower() for word in ["the", "and", "or", "for", "with", "to", "in", "on", "at"]):
                            issues.append(f"英語の翻訳が混入: {full_key} = {value}")
                    
                    # 日本語の翻訳が英語ファイルに混入していないかチェック
                    if locale == "en-US" and not value.isascii():
                        issues.append(f"非ASCII文字が混入: {full_key} = {value}")
        
        check_recursive(translations)
        assert len(issues) == 0, f"{locale}の翻訳品質問題: {issues}"
    
    def test_ui_component_translation_coverage(self):
        """UIコンポーネントの翻訳カバレッジテスト"""
        # UIコンポーネントで使用される翻訳キーのリスト
        required_translation_keys = [
            "common.loading",
            "common.error",
            "common.success",
            "common.cancel",
            "common.save",
            "common.delete",
            "common.edit",
            "common.create",
            "common.submit",
            "common.reset",
            "common.confirm",
            "common.yes",
            "common.no",
            "navigation.home",
            "navigation.posts",
            "navigation.community",
            "navigation.profile",
            "navigation.settings",
            "navigation.help",
            "navigation.about",
            "header.title",
            "header.subtitle",
            "header.newPost",
            "header.refreshPosts",
            "posts.title",
            "posts.noPosts",
            "posts.createFirst",
            "posts.tryAgain",
            "posts.postedOn",
            "posts.createNew",
            "posts.shareThoughts",
            "posts.form.title",
            "posts.form.titlePlaceholder",
            "posts.form.content",
            "posts.form.contentPlaceholder",
            "posts.form.creating",
            "posts.form.createPost",
            "api.status",
            "api.loading",
            "api.connected",
            "api.foundPosts",
            "api.error",
            "api.errorHint",
            "api.createError",
            "welcome.title",
            "welcome.subtitle",
            "footer.copyright",
            "footer.privacy",
            "footer.terms",
            "footer.contact",
            "auth.login.title",
            "auth.login.description",
            "auth.login.email",
            "auth.login.emailPlaceholder",
            "auth.login.password",
            "auth.login.passwordPlaceholder",
            "auth.login.rememberMe",
            "auth.login.submit",
            "auth.login.loading",
            "auth.login.forgotPassword",
            "auth.login.noAccount",
            "auth.login.registerLink",
            "auth.register.title",
            "auth.register.description",
            "auth.register.firstName",
            "auth.register.firstNamePlaceholder",
            "auth.register.lastName",
            "auth.register.lastNamePlaceholder",
            "auth.register.email",
            "auth.register.emailPlaceholder",
            "auth.register.nickname",
            "auth.register.nicknamePlaceholder",
            "auth.register.primaryCondition",
            "auth.register.primaryConditionPlaceholder",
            "auth.register.password",
            "auth.register.passwordPlaceholder",
            "auth.register.confirmPassword",
            "auth.register.confirmPasswordPlaceholder",
            "auth.register.passwordMismatch",
            "auth.register.submit",
            "auth.register.haveAccount",
            "auth.register.loginLink",
            "auth.profile.title",
            "auth.profile.edit",
            "auth.profile.save",
            "auth.profile.cancel",
            "auth.profile.personalInfo",
            "auth.profile.medicalInfo",
            "auth.profile.privacySettings",
            "auth.profile.accessibilitySettings",
            "auth.logout.title",
            "auth.logout.confirm",
            "auth.logout.submit",
            "auth.external.title",
            "auth.external.description",
            "auth.external.signInWith",
            "auth.external.connecting",
            "auth.external.or",
            "auth.external.linkAccount",
            "auth.external.unlinkAccount",
            "auth.external.linkedAccounts",
            "auth.external.noLinkedAccounts",
            "auth.external.linkSuccess",
            "auth.external.unlinkSuccess",
            "auth.external.linkError",
            "auth.external.unlinkError"
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
        for key in required_translation_keys:
            if not check_key_exists(en_translations, key):
                missing_keys.append(key)
        
        assert len(missing_keys) == 0, f"UIコンポーネントで使用される翻訳キーが不足: {missing_keys}"
    
    def test_no_hardcoded_strings_in_components(self):
        """コンポーネント内にハードコードされた文字列がないことを確認"""
        # コンポーネントファイルのパス
        component_paths = [
            "src/components/auth/LoginForm.tsx",
            "src/components/auth/RegisterForm.tsx",
            "src/components/auth/UserProfile.tsx",
            "src/components/layout/Navbar.tsx",
            "src/app/[locale]/auth/page.tsx",
            "src/app/[locale]/profile/page.tsx",
            "src/app/[locale]/page.tsx"
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
            r'useTranslations\([\'"][^"\']*[\'"]\)',  # useTranslations('namespace')
            r'className=',  # CSSクラス名
            r'id=',  # HTML ID
            r'type=',  # HTML type属性
            r'name=',  # HTML name属性
            r'href=',  # HTML href属性
            r'src=',  # HTML src属性
            r'alt=',  # HTML alt属性
            r'placeholder=',  # HTML placeholder属性
            r'aria-label=',  # ARIA属性
            r'data-',  # データ属性
            r'console\.',  # console.log等
            r'import ',  # import文
            r'from ',  # from文
            r'export ',  # export文
            r'function ',  # function文
            r'const ',  # const文
            r'let ',  # let文
            r'var ',  # var文
            r'if ',  # if文
            r'else ',  # else文
            r'for ',  # for文
            r'while ',  # while文
            r'return ',  # return文
            r'throw ',  # throw文
            r'catch ',  # catch文
            r'try ',  # try文
            r'finally ',  # finally文
            r'async ',  # async文
            r'await ',  # await文
            r'Promise',  # Promise
            r'Error',  # Error
            r'Exception',  # Exception
            r'undefined',  # undefined
            r'null',  # null
            r'true',  # true
            r'false',  # false
            r'NaN',  # NaN
            r'Infinity',  # Infinity
            r'/\*',  # コメント開始
            r'\*/',  # コメント終了
            r'//',  # 行コメント
            r'#',  # ハッシュコメント
            r'<!--',  # HTMLコメント開始
            r'-->',  # HTMLコメント終了
            r'http://',  # URL
            r'https://',  # URL
            r'ftp://',  # URL
            r'file://',  # URL
            r'mailto:',  # メールURL
            r'tel:',  # 電話URL
            r'sms:',  # SMS URL
            r'data:',  # データURL
            r'blob:',  # Blob URL
            r'javascript:',  # JavaScript URL
            r'vbscript:',  # VBScript URL
            r'about:',  # About URL
            r'chrome:',  # Chrome URL
            r'moz-',  # Mozilla URL
            r'ms-',  # Microsoft URL
            r'webkit-',  # WebKit URL
            r'-webkit-',  # WebKit URL
            r'-moz-',  # Mozilla URL
            r'-ms-',  # Microsoft URL
            r'-o-',  # Opera URL
            r'rgba(',  # CSS rgba
            r'rgb(',  # CSS rgb
            r'hsl(',  # CSS hsl
            r'hsla(',  # CSS hsla
            r'calc(',  # CSS calc
            r'var(',  # CSS var
            r'url(',  # CSS url
            r'linear-gradient(',  # CSS linear-gradient
            r'radial-gradient(',  # CSS radial-gradient
            r'conic-gradient(',  # CSS conic-gradient
            r'repeating-linear-gradient(',  # CSS repeating-linear-gradient
            r'repeating-radial-gradient(',  # CSS repeating-radial-gradient
            r'repeating-conic-gradient(',  # CSS repeating-conic-gradient
            r'matrix(',  # CSS matrix
            r'matrix3d(',  # CSS matrix3d
            r'perspective(',  # CSS perspective
            r'rotate(',  # CSS rotate
            r'rotateX(',  # CSS rotateX
            r'rotateY(',  # CSS rotateY
            r'rotateZ(',  # CSS rotateZ
            r'rotate3d(',  # CSS rotate3d
            r'scale(',  # CSS scale
            r'scaleX(',  # CSS scaleX
            r'scaleY(',  # CSS scaleY
            r'scaleZ(',  # CSS scaleZ
            r'scale3d(',  # CSS scale3d
            r'skew(',  # CSS skew
            r'skewX(',  # CSS skewX
            r'skewY(',  # CSS skewY
            r'translate(',  # CSS translate
            r'translateX(',  # CSS translateX
            r'translateY(',  # CSS translateY
            r'translateZ(',  # CSS translateZ
            r'translate3d(',  # CSS translate3d
            r'cubic-bezier(',  # CSS cubic-bezier
            r'steps(',  # CSS steps
            r'ease',  # CSS ease
            r'ease-in',  # CSS ease-in
            r'ease-out',  # CSS ease-out
            r'ease-in-out',  # CSS ease-in-out
            r'linear',  # CSS linear
            r'infinite',  # CSS infinite
            r'normal',  # CSS normal
            r'reverse',  # CSS reverse
            r'alternate',  # CSS alternate
            r'alternate-reverse',  # CSS alternate-reverse
            r'forwards',  # CSS forwards
            r'backwards',  # CSS backwards
            r'both',  # CSS both
            r'none',  # CSS none
            r'auto',  # CSS auto
            r'initial',  # CSS initial
            r'inherit',  # CSS inherit
            r'unset',  # CSS unset
            r'revert',  # CSS revert
            r'important',  # CSS !important
            r'!important',  # CSS !important
            r'@media',  # CSS @media
            r'@keyframes',  # CSS @keyframes
            r'@import',  # CSS @import
            r'@charset',  # CSS @charset
            r'@namespace',  # CSS @namespace
            r'@page',  # CSS @page
            r'@supports',  # CSS @supports
            r'@document',  # CSS @document
            r'@font-face',  # CSS @font-face
            r'@viewport',  # CSS @viewport
            r'@counter-style',  # CSS @counter-style
            r'@font-feature-values',  # CSS @font-feature-values
            r'@color-profile',  # CSS @color-profile
            r'@property',  # CSS @property
            r'@layer',  # CSS @layer
            r'@scope',  # CSS @scope
            r'@container',  # CSS @container
            r'@starting-style',  # CSS @starting-style
            r'@media',  # CSS @media
            r'@keyframes',  # CSS @keyframes
            r'@import',  # CSS @import
            r'@charset',  # CSS @charset
            r'@namespace',  # CSS @namespace
            r'@page',  # CSS @page
            r'@supports',  # CSS @supports
            r'@document',  # CSS @document
            r'@font-face',  # CSS @font-face
            r'@viewport',  # CSS @viewport
            r'@counter-style',  # CSS @counter-style
            r'@font-feature-values',  # CSS @font-feature-values
            r'@color-profile',  # CSS @color-profile
            r'@property',  # CSS @property
            r'@layer',  # CSS @layer
            r'@scope',  # CSS @scope
            r'@container',  # CSS @container
            r'@starting-style',  # CSS @starting-style
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
        
        # 重要なハードコードされた文字列がないことを確認
        critical_hardcoded = [s for s in hardcoded_strings if any(word in s.lower() for word in ["login", "register", "profile", "home", "posts", "community", "welcome", "healthcare", "supporting", "platform", "account", "password", "email", "nickname", "first", "last", "name", "condition", "medical", "privacy", "accessibility", "settings", "logout", "sign", "create", "join", "connect", "challenges", "choose", "preferred", "authentication", "method", "external", "services", "link", "unlink", "success", "error", "failed", "linked", "accounts", "no", "external", "accounts", "linked", "successfully", "unlinked", "successfully", "failed", "link", "external", "account", "unlink", "external", "account"])]
        assert len(critical_hardcoded) == 0, f"重要なハードコードされた文字列が見つかりました: {critical_hardcoded}"
    
    def test_translation_key_naming_convention(self):
        """翻訳キーの命名規則のテスト"""
        # 翻訳ファイルのパス
        translation_files = {
            "en-US": "messages/en-US.json",
            "ja-JP": "messages/ja-JP.json",
            "fr-FR": "messages/fr-FR.json"
        }
        
        # 各言語の翻訳ファイルを読み込み
        translations = {}
        for locale, file_path in translation_files.items():
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    translations[locale] = json.load(f)
        
        # 翻訳キーの命名規則をチェック
        def check_naming_convention(translations, prefix=""):
            issues = []
            for key, value in translations.items():
                full_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, dict):
                    issues.extend(check_naming_convention(value, full_key))
                else:
                    # 翻訳キーの命名規則をチェック
                    if not re.match(r'^[a-zA-Z][a-zA-Z0-9]*(\.[a-zA-Z][a-zA-Z0-9]*)*$', full_key):
                        issues.append(f"命名規則に違反: {full_key}")
                    
                    # 翻訳キーがそのまま表示されていないかチェック
                    if value.startswith("auth.") or value.startswith("common."):
                        issues.append(f"翻訳キーがそのまま表示: {full_key} = {value}")
            
            return issues
        
        for locale, translation in translations.items():
            issues = check_naming_convention(translation)
            assert len(issues) == 0, f"{locale}の翻訳キー命名規則違反: {issues}"
    
    def test_translation_consistency(self):
        """翻訳の一貫性テスト"""
        # 翻訳ファイルのパス
        translation_files = {
            "en-US": "messages/en-US.json",
            "ja-JP": "messages/ja-JP.json",
            "fr-FR": "messages/fr-FR.json"
        }
        
        # 各言語の翻訳ファイルを読み込み
        translations = {}
        for locale, file_path in translation_files.items():
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    translations[locale] = json.load(f)
        
        # 翻訳の一貫性をチェック
        def check_consistency(translations, prefix=""):
            issues = []
            for key, value in translations.items():
                full_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, dict):
                    issues.extend(check_consistency(value, full_key))
                else:
                    # 翻訳の一貫性をチェック
                    if value and isinstance(value, str):
                        # 空の翻訳チェック
                        if value.strip() == "":
                            issues.append(f"空の翻訳: {full_key}")
                        
                        # 翻訳キーがそのまま表示されていないかチェック
                        if value.startswith("auth.") or value.startswith("common."):
                            issues.append(f"翻訳キーがそのまま表示: {full_key} = {value}")
                        
                        # 翻訳の一貫性をチェック
                        if value.count("{") != value.count("}"):
                            issues.append(f"プレースホルダーの不一致: {full_key} = {value}")
            
            return issues
        
        for locale, translation in translations.items():
            issues = check_consistency(translation)
            assert len(issues) == 0, f"{locale}の翻訳一貫性問題: {issues}"
    
    def test_translation_encoding(self):
        """翻訳ファイルのエンコーディングテスト"""
        # 翻訳ファイルのパス
        translation_files = {
            "en-US": "messages/en-US.json",
            "ja-JP": "messages/ja-JP.json",
            "fr-FR": "messages/fr-FR.json"
        }
        
        # 各言語の翻訳ファイルのエンコーディングをチェック
        for locale, file_path in translation_files.items():
            if os.path.exists(file_path):
                # UTF-8で読み込めることを確認
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    assert content is not None
                
                # JSONとして有効であることを確認
                with open(file_path, "r", encoding="utf-8") as f:
                    json.load(f)
    
    def test_translation_file_structure(self):
        """翻訳ファイルの構造テスト"""
        # 翻訳ファイルのパス
        translation_files = {
            "en-US": "messages/en-US.json",
            "ja-JP": "messages/ja-JP.json",
            "fr-FR": "messages/fr-FR.json"
        }
        
        # 各言語の翻訳ファイルの構造をチェック
        for locale, file_path in translation_files.items():
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    translation = json.load(f)
                
                # 翻訳ファイルが辞書であることを確認
                assert isinstance(translation, dict), f"{locale}の翻訳ファイルが辞書ではありません"
                
                # 必須のトップレベルキーが存在することを確認
                required_top_level_keys = ["common", "navigation", "header", "posts", "api", "welcome", "footer", "auth"]
                for key in required_top_level_keys:
                    assert key in translation, f"{locale}の翻訳ファイルに必須キーが不足: {key}"
                
                # 各トップレベルキーが辞書であることを確認
                for key in required_top_level_keys:
                    if key in translation:
                        assert isinstance(translation[key], dict), f"{locale}の翻訳ファイルの{key}が辞書ではありません"
    
    def test_translation_file_size(self):
        """翻訳ファイルのサイズテスト"""
        # 翻訳ファイルのパス
        translation_files = {
            "en-US": "messages/en-US.json",
            "ja-JP": "messages/ja-JP.json",
            "fr-FR": "messages/fr-FR.json"
        }
        
        # 各言語の翻訳ファイルのサイズをチェック
        for locale, file_path in translation_files.items():
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                
                # ファイルサイズが適切であることを確認（1KB以上、1MB以下）
                assert file_size > 1024, f"{locale}の翻訳ファイルが小さすぎます: {file_size} bytes"
                assert file_size < 1024 * 1024, f"{locale}の翻訳ファイルが大きすぎます: {file_size} bytes"
    
    def test_translation_file_permissions(self):
        """翻訳ファイルの権限テスト"""
        # 翻訳ファイルのパス
        translation_files = {
            "en-US": "messages/en-US.json",
            "ja-JP": "messages/ja-JP.json",
            "fr-FR": "messages/fr-FR.json"
        }
        
        # 各言語の翻訳ファイルの権限をチェック
        for locale, file_path in translation_files.items():
            if os.path.exists(file_path):
                # ファイルが読み取り可能であることを確認
                assert os.access(file_path, os.R_OK), f"{locale}の翻訳ファイルが読み取り不可能です"
                
                # ファイルが書き込み可能であることを確認
                assert os.access(file_path, os.W_OK), f"{locale}の翻訳ファイルが書き込み不可能です"
    
    def test_translation_file_backup(self):
        """翻訳ファイルのバックアップテスト"""
        # 翻訳ファイルのパス
        translation_files = {
            "en-US": "messages/en-US.json",
            "ja-JP": "messages/ja-JP.json",
            "fr-FR": "messages/fr-FR.json"
        }
        
        # 各言語の翻訳ファイルのバックアップをチェック
        for locale, file_path in translation_files.items():
            if os.path.exists(file_path):
                # バックアップファイルが存在することを確認（実装に依存）
                backup_file = f"{file_path}.backup"
                if os.path.exists(backup_file):
                    # バックアップファイルが最新であることを確認
                    original_mtime = os.path.getmtime(file_path)
                    backup_mtime = os.path.getmtime(backup_file)
                    assert backup_mtime >= original_mtime, f"{locale}の翻訳ファイルのバックアップが古いです"
    
    def test_translation_file_validation(self):
        """翻訳ファイルの検証テスト"""
        # 翻訳ファイルのパス
        translation_files = {
            "en-US": "messages/en-US.json",
            "ja-JP": "messages/ja-JP.json",
            "fr-FR": "messages/fr-FR.json"
        }
        
        # 各言語の翻訳ファイルの検証をチェック
        for locale, file_path in translation_files.items():
            if os.path.exists(file_path):
                # JSONとして有効であることを確認
                with open(file_path, "r", encoding="utf-8") as f:
                    translation = json.load(f)
                
                # 翻訳ファイルが辞書であることを確認
                assert isinstance(translation, dict), f"{locale}の翻訳ファイルが辞書ではありません"
                
                # 翻訳ファイルが空でないことを確認
                assert len(translation) > 0, f"{locale}の翻訳ファイルが空です"
                
                # 翻訳ファイルの構造が適切であることを確認
                def validate_structure(translations, prefix=""):
                    for key, value in translations.items():
                        full_key = f"{prefix}.{key}" if prefix else key
                        if isinstance(value, dict):
                            validate_structure(value, full_key)
                        else:
                            # 翻訳値が文字列であることを確認
                            assert isinstance(value, str), f"{locale}の翻訳ファイルの{full_key}が文字列ではありません"
                            
                            # 翻訳値が空でないことを確認
                            assert value.strip() != "", f"{locale}の翻訳ファイルの{full_key}が空です"
                
                validate_structure(translation)




