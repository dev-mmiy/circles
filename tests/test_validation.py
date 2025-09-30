"""
データバリデーション機能のテスト
"""

import pytest
from validation_utils import (
    validate_email, validate_phone_number, validate_birth_date,
    validate_gender, validate_blood_type, validate_height, validate_weight,
    validate_body_fat_percentage, validate_activity_level, validate_insurance_number,
    validate_profile_data, ValidationError
)

class TestValidationUtils:
    """バリデーション機能のテスト"""
    
    def test_validate_email(self):
        """メールアドレスのバリデーションテスト"""
        # 有効なメールアドレス
        assert validate_email("test@example.com") == True
        assert validate_email("user.name@domain.co.jp") == True
        assert validate_email("test+tag@example.org") == True
        
        # 無効なメールアドレス
        assert validate_email("invalid-email") == False
        assert validate_email("@example.com") == False
        assert validate_email("test@") == False
        assert validate_email("") == False
    
    def test_validate_phone_number(self):
        """電話番号のバリデーションテスト"""
        # 有効な電話番号
        assert validate_phone_number("090-1234-5678") == True
        assert validate_phone_number("03-1234-5678") == True
        assert validate_phone_number("09012345678") == True
        assert validate_phone_number("") == True  # 空は有効
        
        # 無効な電話番号
        assert validate_phone_number("123-456-789") == False
        assert validate_phone_number("abc-def-ghij") == False
        assert validate_phone_number("123456789012345") == False
    
    def test_validate_birth_date(self):
        """生年月日のバリデーションテスト"""
        # 有効な生年月日
        assert validate_birth_date("1990-01-01") == True
        assert validate_birth_date("2000-12-31") == True
        assert validate_birth_date("") == True  # 空は有効
        
        # 無効な生年月日
        assert validate_birth_date("2030-01-01") == False  # 未来の日付
        assert validate_birth_date("1800-01-01") == False  # 120歳以上
        assert validate_birth_date("invalid-date") == False
        assert validate_birth_date("1990/01/01") == False  # 不正な形式
    
    def test_validate_gender(self):
        """性別のバリデーションテスト"""
        # 有効な性別
        assert validate_gender("male") == True
        assert validate_gender("female") == True
        assert validate_gender("other") == True
        assert validate_gender("") == True  # 空は有効
        
        # 無効な性別
        assert validate_gender("invalid") == False
        assert validate_gender("MALE") == False  # 大文字は無効
    
    def test_validate_blood_type(self):
        """血液型のバリデーションテスト"""
        # 有効な血液型
        assert validate_blood_type("A") == True
        assert validate_blood_type("B") == True
        assert validate_blood_type("AB") == True
        assert validate_blood_type("O") == True
        assert validate_blood_type("unknown") == True
        assert validate_blood_type("") == True  # 空は有効
        
        # 無効な血液型
        assert validate_blood_type("X") == False
        assert validate_blood_type("a") == False  # 小文字は無効
    
    def test_validate_height(self):
        """身長のバリデーションテスト"""
        # 有効な身長
        assert validate_height(170.0) == True
        assert validate_height(150.5) == True
        assert validate_height(200.0) == True
        assert validate_height(None) == True  # 空は有効
        
        # 無効な身長
        assert validate_height(49.0) == False  # 下限以下
        assert validate_height(251.0) == False  # 上限以上
        assert validate_height(-10.0) == False  # 負の値
    
    def test_validate_weight(self):
        """体重のバリデーションテスト"""
        # 有効な体重
        assert validate_weight(65.0) == True
        assert validate_weight(50.5) == True
        assert validate_weight(100.0) == True
        assert validate_weight(None) == True  # 空は有効
        
        # 無効な体重
        assert validate_weight(19.0) == False  # 下限以下
        assert validate_weight(301.0) == False  # 上限以上
        assert validate_weight(-10.0) == False  # 負の値
    
    def test_validate_body_fat_percentage(self):
        """体脂肪率のバリデーションテスト"""
        # 有効な体脂肪率
        assert validate_body_fat_percentage(15.0) == True
        assert validate_body_fat_percentage(25.5) == True
        assert validate_body_fat_percentage(0.0) == True
        assert validate_body_fat_percentage(50.0) == True
        assert validate_body_fat_percentage(None) == True  # 空は有効
        
        # 無効な体脂肪率
        assert validate_body_fat_percentage(-1.0) == False  # 負の値
        assert validate_body_fat_percentage(51.0) == False  # 上限以上
    
    def test_validate_activity_level(self):
        """活動レベルのバリデーションテスト"""
        # 有効な活動レベル
        assert validate_activity_level("low") == True
        assert validate_activity_level("moderate") == True
        assert validate_activity_level("high") == True
        assert validate_activity_level("") == True  # 空は有効
        
        # 無効な活動レベル
        assert validate_activity_level("invalid") == False
        assert validate_activity_level("LOW") == False  # 大文字は無効
    
    def test_validate_insurance_number(self):
        """保険証番号のバリデーションテスト"""
        # 有効な保険証番号
        assert validate_insurance_number("12345678") == True
        assert validate_insurance_number("1234-5678") == True
        assert validate_insurance_number("123456789012") == True
        assert validate_insurance_number("") == True  # 空は有効
        
        # 無効な保険証番号
        assert validate_insurance_number("1234567") == False  # 短すぎる
        assert validate_insurance_number("1234567890123") == False  # 長すぎる
        assert validate_insurance_number("abc12345") == False  # 文字が含まれる
    
    def test_validate_profile_data_valid(self):
        """有効なプロファイルデータのバリデーションテスト"""
        valid_data = {
            'email': 'test@example.com',
            'birth_date': '1990-01-01',
            'gender': 'male',
            'blood_type': 'A',
            'height_cm': 170.0,
            'target_weight_kg': 65.0,
            'target_body_fat_percentage': 15.0,
            'activity_level': 'moderate',
            'emergency_contact_phone': '090-1234-5678',
            'insurance_number': '12345678'
        }
        
        errors = validate_profile_data(valid_data)
        assert len(errors) == 0
    
    def test_validate_profile_data_invalid(self):
        """無効なプロファイルデータのバリデーションテスト"""
        invalid_data = {
            'email': 'invalid-email',
            'birth_date': '2030-01-01',  # 未来の日付
            'gender': 'invalid',
            'blood_type': 'X',
            'height_cm': 300.0,  # 身長が高すぎる
            'target_weight_kg': 500.0,  # 体重が重すぎる
            'target_body_fat_percentage': 60.0,  # 体脂肪率が高すぎる
            'activity_level': 'invalid',
            'emergency_contact_phone': 'invalid-phone',
            'insurance_number': '123'  # 短すぎる
        }
        
        errors = validate_profile_data(invalid_data)
        assert len(errors) > 0
        
        # エラーフィールドの確認
        error_fields = [error.field for error in errors]
        expected_fields = [
            'email', 'birth_date', 'gender', 'blood_type', 'height_cm',
            'target_weight_kg', 'target_body_fat_percentage', 'activity_level',
            'emergency_contact_phone', 'insurance_number'
        ]
        
        for field in expected_fields:
            assert field in error_fields
    
    def test_validate_profile_data_partial(self):
        """部分的なプロファイルデータのバリデーションテスト"""
        partial_data = {
            'height_cm': 170.0,
            'activity_level': 'moderate'
        }
        
        errors = validate_profile_data(partial_data)
        assert len(errors) == 0  # 部分的なデータでも有効
    
    def test_validate_profile_data_empty(self):
        """空のプロファイルデータのバリデーションテスト"""
        empty_data = {}
        
        errors = validate_profile_data(empty_data)
        assert len(errors) == 0  # 空のデータでも有効

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
