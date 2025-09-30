"""
日時形式の統一ユーティリティ
データベース、API、フロントエンド間での日時形式を統一する
"""

from datetime import datetime, timezone
from typing import Optional, Union
import pytz


class DateTimeUtils:
    """日時形式の統一管理クラス"""
    
    # データベース保存形式（UTC）
    DB_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    # API送信形式（ISO 8601）
    API_FORMAT = "%Y-%m-%dT%H:%M:%S"
    
    # フロントエンド表示形式
    DISPLAY_FORMAT = "%Y/%m/%d %H:%M"
    
    @staticmethod
    def to_utc_db_format(dt: Union[str, datetime], user_timezone: str = "UTC") -> str:
        """
        任意の日時をUTCのデータベース形式に変換
        
        Args:
            dt: 日時（文字列またはdatetimeオブジェクト）
            user_timezone: ユーザーのタイムゾーン
            
        Returns:
            UTC形式の文字列 (YYYY-MM-DD HH:MM:SS)
        """
        if isinstance(dt, str):
            # 文字列をdatetimeに変換
            if 'T' in dt:
                # ISO形式の場合
                if dt.endswith('Z'):
                    dt = dt[:-1]  # Zを削除
                if dt.count(':') == 1:
                    dt += ':00'  # 秒がない場合は追加
                parsed_dt = datetime.fromisoformat(dt)
            else:
                # 標準形式の場合
                parsed_dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
        else:
            parsed_dt = dt
        
        # タイムゾーン情報がない場合はユーザータイムゾーンを設定
        if parsed_dt.tzinfo is None:
            user_tz = pytz.timezone(user_timezone)
            parsed_dt = user_tz.localize(parsed_dt)
        
        # UTCに変換
        utc_dt = parsed_dt.astimezone(timezone.utc)
        
        return utc_dt.strftime(DateTimeUtils.DB_FORMAT)
    
    @staticmethod
    def to_api_format(dt: Union[str, datetime]) -> str:
        """
        データベース形式をAPI形式に変換
        
        Args:
            dt: データベース形式の日時文字列またはdatetimeオブジェクト
            
        Returns:
            ISO 8601形式の文字列 (YYYY-MM-DDTHH:MM:SS)
        """
        if isinstance(dt, str):
            # データベース形式をdatetimeに変換
            parsed_dt = datetime.strptime(dt, DateTimeUtils.DB_FORMAT)
            # UTCとして扱う
            parsed_dt = parsed_dt.replace(tzinfo=timezone.utc)
        else:
            parsed_dt = dt
        
        return parsed_dt.strftime(DateTimeUtils.API_FORMAT)
    
    @staticmethod
    def to_display_format(dt: Union[str, datetime], user_timezone: str = "UTC", locale: str = "ja-JP") -> str:
        """
        データベース形式を表示形式に変換
        
        Args:
            dt: データベース形式の日時文字列またはdatetimeオブジェクト
            user_timezone: ユーザーのタイムゾーン
            locale: ロケール
            
        Returns:
            表示用の日時文字列
        """
        if isinstance(dt, str):
            # データベース形式をdatetimeに変換
            parsed_dt = datetime.strptime(dt, DateTimeUtils.DB_FORMAT)
            # UTCとして扱う
            parsed_dt = parsed_dt.replace(tzinfo=timezone.utc)
        else:
            parsed_dt = dt
        
        # ユーザーのタイムゾーンに変換
        user_tz = pytz.timezone(user_timezone)
        local_dt = parsed_dt.astimezone(user_tz)
        
        # ロケールに応じた形式で表示
        if locale.startswith('ja'):
            return local_dt.strftime("%Y年%m月%d日 %H:%M")
        else:
            return local_dt.strftime("%Y/%m/%d %H:%M")
    
    @staticmethod
    def get_current_local_time(user_timezone: str = "UTC") -> str:
        """
        現在のローカル時間をAPI形式で取得
        
        Args:
            user_timezone: ユーザーのタイムゾーン
            
        Returns:
            ISO 8601形式の現在時刻
        """
        user_tz = pytz.timezone(user_timezone)
        now = datetime.now(user_tz)
        return now.strftime(DateTimeUtils.API_FORMAT)
    
    @staticmethod
    def parse_user_input(user_input: str, user_timezone: str = "UTC") -> str:
        """
        ユーザー入力（datetime-local）をAPI形式に変換
        
        Args:
            user_input: ユーザー入力（YYYY-MM-DDTHH:MM形式）
            user_timezone: ユーザーのタイムゾーン
            
        Returns:
            ISO 8601形式の文字列
        """
        # datetime-localの形式をdatetimeに変換
        parsed_dt = datetime.fromisoformat(user_input)
        
        # タイムゾーン情報がない場合はユーザータイムゾーンを設定
        if parsed_dt.tzinfo is None:
            user_tz = pytz.timezone(user_timezone)
            parsed_dt = user_tz.localize(parsed_dt)
        
        return parsed_dt.strftime(DateTimeUtils.API_FORMAT)


# 便利な関数
def to_utc_db(dt: Union[str, datetime], user_timezone: str = "UTC") -> str:
    """UTCデータベース形式への変換（ショートカット）"""
    return DateTimeUtils.to_utc_db_format(dt, user_timezone)


def to_api_format(dt: Union[str, datetime]) -> str:
    """API形式への変換（ショートカット）"""
    return DateTimeUtils.to_api_format(dt)


def to_display_format(dt: Union[str, datetime], user_timezone: str = "UTC", locale: str = "ja-JP") -> str:
    """表示形式への変換（ショートカット）"""
    return DateTimeUtils.to_display_format(dt, user_timezone, locale)


def get_current_local_time(user_timezone: str = "UTC") -> str:
    """現在のローカル時間取得（ショートカット）"""
    return DateTimeUtils.get_current_local_time(user_timezone)


def parse_user_input(user_input: str, user_timezone: str = "UTC") -> str:
    """ユーザー入力の解析（ショートカット）"""
    return DateTimeUtils.parse_user_input(user_input, user_timezone)
