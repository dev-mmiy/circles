"""
日時処理ユーティリティのUnit Test
"""

import pytest
from datetime import datetime, timezone
import pytz
from datetime_utils import (
    DateTimeUtils, 
    to_utc_db, 
    to_api_format, 
    to_display_format,
    get_current_local_time,
    parse_user_input
)


class TestDateTimeUtils:
    """日時処理ユーティリティのテストクラス"""
    
    def test_to_utc_db_format_with_string(self):
        """文字列からUTCデータベース形式への変換テスト"""
        # ISO形式の文字列
        result = DateTimeUtils.to_utc_db_format("2024-01-01T10:30:00", "Asia/Tokyo")
        assert result == "2024-01-01 01:30:00"  # JSTからUTCに変換
        
        # 標準形式の文字列
        result = DateTimeUtils.to_utc_db_format("2024-01-01 10:30:00", "Asia/Tokyo")
        assert result == "2024-01-01 01:30:00"
    
    def test_to_utc_db_format_with_datetime(self):
        """datetimeオブジェクトからUTCデータベース形式への変換テスト"""
        dt = datetime(2024, 1, 1, 10, 30, 0)
        result = DateTimeUtils.to_utc_db_format(dt, "Asia/Tokyo")
        assert result == "2024-01-01 01:30:00"
    
    def test_to_api_format(self):
        """データベース形式からAPI形式への変換テスト"""
        # データベース形式の文字列
        result = DateTimeUtils.to_api_format("2024-01-01 10:30:00")
        assert result == "2024-01-01T10:30:00"
        
        # datetimeオブジェクト
        dt = datetime(2024, 1, 1, 10, 30, 0)
        result = DateTimeUtils.to_api_format(dt)
        assert result == "2024-01-01T10:30:00"
    
    def test_to_display_format_japanese(self):
        """日本語表示形式への変換テスト"""
        result = DateTimeUtils.to_display_format(
            "2024-01-01 10:30:00", 
            "Asia/Tokyo", 
            "ja-JP"
        )
        assert result == "2024年01月01日 19:30"  # UTCからJSTに変換
    
    def test_to_display_format_english(self):
        """英語表示形式への変換テスト"""
        result = DateTimeUtils.to_display_format(
            "2024-01-01 10:30:00", 
            "America/New_York", 
            "en-US"
        )
        assert result == "2024/01/01 05:30"  # UTCからESTに変換
    
    def test_get_current_local_time(self):
        """現在のローカル時間取得テスト"""
        result = DateTimeUtils.get_current_local_time("Asia/Tokyo")
        # 形式の確認（具体的な値は実行時によって変わる）
        assert "T" in result
        assert len(result) == 16  # YYYY-MM-DDTHH:MM
        assert result.count("-") == 2
        assert result.count(":") == 1
    
    def test_parse_user_input(self):
        """ユーザー入力の解析テスト"""
        result = DateTimeUtils.parse_user_input("2024-01-01T10:30", "Asia/Tokyo")
        assert result == "2024-01-01T10:30:00"
        
        result = DateTimeUtils.parse_user_input("2024-01-01T10:30:00", "Asia/Tokyo")
        assert result == "2024-01-01T10:30:00"


class TestDateTimeUtilsShortcuts:
    """日時処理ユーティリティのショートカット関数のテスト"""
    
    def test_to_utc_db_shortcut(self):
        """to_utc_db関数のテスト"""
        result = to_utc_db("2024-01-01T10:30:00", "Asia/Tokyo")
        assert result == "2024-01-01 01:30:00"
    
    def test_to_api_format_shortcut(self):
        """to_api_format関数のテスト"""
        result = to_api_format("2024-01-01 10:30:00")
        assert result == "2024-01-01T10:30:00"
    
    def test_to_display_format_shortcut(self):
        """to_display_format関数のテスト"""
        result = to_display_format("2024-01-01 10:30:00", "Asia/Tokyo", "ja-JP")
        assert result == "2024年01月01日 19:30"
    
    def test_get_current_local_time_shortcut(self):
        """get_current_local_time関数のテスト"""
        result = get_current_local_time("Asia/Tokyo")
        assert "T" in result
        assert len(result) == 16
    
    def test_parse_user_input_shortcut(self):
        """parse_user_input関数のテスト"""
        result = parse_user_input("2024-01-01T10:30", "Asia/Tokyo")
        assert result == "2024-01-01T10:30:00"


class TestDateTimeUtilsEdgeCases:
    """日時処理のエッジケーステスト"""
    
    def test_timezone_conversion_edge_cases(self):
        """タイムゾーン変換のエッジケース"""
        # 夏時間の境界
        result = DateTimeUtils.to_utc_db_format("2024-03-10T02:30:00", "America/New_York")
        # 結果は夏時間の開始により変わる可能性があるため、形式のみ確認
        assert "2024-03-10" in result
        
        # 年末年始
        result = DateTimeUtils.to_utc_db_format("2024-12-31T23:30:00", "Asia/Tokyo")
        assert result == "2024-12-31 14:30:00"
    
    def test_invalid_input_handling(self):
        """無効な入力の処理テスト"""
        with pytest.raises(ValueError):
            DateTimeUtils.to_utc_db_format("invalid-date", "UTC")
        
        with pytest.raises(ValueError):
            DateTimeUtils.to_api_format("invalid-format")
    
    def test_timezone_handling(self):
        """タイムゾーン処理のテスト"""
        # UTC入力
        result = DateTimeUtils.to_utc_db_format("2024-01-01T10:30:00Z", "UTC")
        assert result == "2024-01-01 10:30:00"
        
        # 異なるタイムゾーン
        result = DateTimeUtils.to_utc_db_format("2024-01-01T10:30:00", "Europe/London")
        assert result == "2024-01-01 10:30:00"  # 冬時間なのでUTCと同じ


if __name__ == "__main__":
    pytest.main([__file__])
