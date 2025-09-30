"""
データバリデーション用のユーティリティ関数
"""

import re
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum

class ValidationError(Exception):
    """バリデーションエラー"""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")

class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class BloodType(Enum):
    A = "A"
    B = "B"
    AB = "AB"
    O = "O"
    UNKNOWN = "unknown"

class ActivityLevel(Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"

def validate_email(email: str) -> bool:
    """メールアドレスのバリデーション"""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone_number(phone: str) -> bool:
    """電話番号のバリデーション（日本の形式）"""
    if not phone:
        return True  # 空の場合は有効
    
    # 日本の電話番号パターン
    patterns = [
        r'^0\d{1,4}-\d{1,4}-\d{4}$',  # 固定電話
        r'^0\d{2,4}-\d{2,4}-\d{4}$',  # 携帯電話
        r'^\d{2,4}-\d{2,4}-\d{4}$',   # 市外局番なし
        r'^0\d{9,10}$',               # ハイフンなし携帯
        r'^\d{10,11}$'                # ハイフンなし固定
    ]
    
    for pattern in patterns:
        if re.match(pattern, phone):
            return True
    return False

def validate_date_format(date_str: str) -> bool:
    """日付形式のバリデーション（YYYY-MM-DD）"""
    if not date_str:
        return True  # 空の場合は有効
    
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_birth_date(birth_date: str) -> bool:
    """生年月日のバリデーション"""
    if not birth_date:
        return True  # 空の場合は有効
    
    if not validate_date_format(birth_date):
        return False
    
    try:
        birth = datetime.strptime(birth_date, '%Y-%m-%d').date()
        today = date.today()
        
        # 未来の日付は無効
        if birth >= today:
            return False
        
        # 120歳以上は無効
        age = today.year - birth.year
        if age > 120:
            return False
            
        return True
    except ValueError:
        return False

def validate_gender(gender: str) -> bool:
    """性別のバリデーション"""
    if not gender:
        return True  # 空の場合は有効
    
    valid_genders = [g.value for g in Gender]
    return gender in valid_genders

def validate_blood_type(blood_type: str) -> bool:
    """血液型のバリデーション"""
    if not blood_type:
        return True  # 空の場合は有効
    
    valid_types = [bt.value for bt in BloodType]
    return blood_type in valid_types

def validate_height(height: Optional[float]) -> bool:
    """身長のバリデーション（cm）"""
    if height is None:
        return True  # 空の場合は有効
    
    return 50.0 <= height <= 250.0

def validate_weight(weight: Optional[float]) -> bool:
    """体重のバリデーション（kg）"""
    if weight is None:
        return True  # 空の場合は有効
    
    return 20.0 <= weight <= 300.0

def validate_body_fat_percentage(body_fat: Optional[float]) -> bool:
    """体脂肪率のバリデーション（%）"""
    if body_fat is None:
        return True  # 空の場合は有効
    
    return 0.0 <= body_fat <= 50.0

def validate_activity_level(activity_level: str) -> bool:
    """活動レベルのバリデーション"""
    if not activity_level:
        return True  # 空の場合は有効
    
    valid_levels = [al.value for al in ActivityLevel]
    return activity_level in valid_levels

def validate_insurance_number(insurance_number: str) -> bool:
    """保険証番号のバリデーション"""
    if not insurance_number:
        return True  # 空の場合は有効
    
    # 数字とハイフンのみ、長さは8-12文字
    pattern = r'^[\d-]{8,12}$'
    return bool(re.match(pattern, insurance_number))

def validate_text_field(text: str, max_length: int = 1000) -> bool:
    """テキストフィールドのバリデーション"""
    if not text:
        return True  # 空の場合は有効
    
    return len(text) <= max_length

def validate_profile_data(profile_data: Dict[str, Any]) -> List[ValidationError]:
    """プロファイルデータの包括的バリデーション"""
    errors = []
    
    # 基本属性のバリデーション
    if 'email' in profile_data and profile_data['email']:
        if not validate_email(profile_data['email']):
            errors.append(ValidationError('email', '有効なメールアドレスを入力してください'))
    
    if 'birth_date' in profile_data and profile_data['birth_date']:
        if not validate_birth_date(profile_data['birth_date']):
            errors.append(ValidationError('birth_date', '有効な生年月日を入力してください'))
    
    if 'gender' in profile_data and profile_data['gender']:
        if not validate_gender(profile_data['gender']):
            errors.append(ValidationError('gender', '有効な性別を選択してください'))
    
    if 'blood_type' in profile_data and profile_data['blood_type']:
        if not validate_blood_type(profile_data['blood_type']):
            errors.append(ValidationError('blood_type', '有効な血液型を選択してください'))
    
    # 健康管理関連属性のバリデーション
    if 'height_cm' in profile_data and profile_data['height_cm'] is not None:
        if not validate_height(profile_data['height_cm']):
            errors.append(ValidationError('height_cm', '身長は50-250cmの範囲で入力してください'))
    
    if 'target_weight_kg' in profile_data and profile_data['target_weight_kg'] is not None:
        if not validate_weight(profile_data['target_weight_kg']):
            errors.append(ValidationError('target_weight_kg', '目標体重は20-300kgの範囲で入力してください'))
    
    if 'target_body_fat_percentage' in profile_data and profile_data['target_body_fat_percentage'] is not None:
        if not validate_body_fat_percentage(profile_data['target_body_fat_percentage']):
            errors.append(ValidationError('target_body_fat_percentage', '目標体脂肪率は0-50%の範囲で入力してください'))
    
    if 'activity_level' in profile_data and profile_data['activity_level']:
        if not validate_activity_level(profile_data['activity_level']):
            errors.append(ValidationError('activity_level', '有効な活動レベルを選択してください'))
    
    # 医療情報のバリデーション
    if 'medical_conditions' in profile_data and profile_data['medical_conditions']:
        if not validate_text_field(profile_data['medical_conditions'], 2000):
            errors.append(ValidationError('medical_conditions', '既往歴は2000文字以内で入力してください'))
    
    if 'medications' in profile_data and profile_data['medications']:
        if not validate_text_field(profile_data['medications'], 2000):
            errors.append(ValidationError('medications', '服用薬は2000文字以内で入力してください'))
    
    if 'allergies' in profile_data and profile_data['allergies']:
        if not validate_text_field(profile_data['allergies'], 2000):
            errors.append(ValidationError('allergies', 'アレルギーは2000文字以内で入力してください'))
    
    # 緊急連絡先・医療関係者情報のバリデーション
    if 'emergency_contact_phone' in profile_data and profile_data['emergency_contact_phone']:
        if not validate_phone_number(profile_data['emergency_contact_phone']):
            errors.append(ValidationError('emergency_contact_phone', '有効な電話番号を入力してください'))
    
    if 'doctor_phone' in profile_data and profile_data['doctor_phone']:
        if not validate_phone_number(profile_data['doctor_phone']):
            errors.append(ValidationError('doctor_phone', '有効な電話番号を入力してください'))
    
    if 'insurance_number' in profile_data and profile_data['insurance_number']:
        if not validate_insurance_number(profile_data['insurance_number']):
            errors.append(ValidationError('insurance_number', '有効な保険証番号を入力してください'))
    
    # テキストフィールドの長さチェック
    text_fields = [
        'emergency_contact_name', 'doctor_name', 'region'
    ]
    
    for field in text_fields:
        if field in profile_data and profile_data[field]:
            if not validate_text_field(profile_data[field], 100):
                errors.append(ValidationError(field, f'{field}は100文字以内で入力してください'))
    
    return errors

def format_validation_errors(errors: List[ValidationError]) -> Dict[str, str]:
    """バリデーションエラーをフォーマット"""
    return {error.field: error.message for error in errors}

if __name__ == "__main__":
    # テスト用のサンプルデータ
    test_data = {
        'email': 'test@example.com',
        'birth_date': '1990-01-01',
        'gender': 'male',
        'blood_type': 'A',
        'height_cm': 170.0,
        'target_weight_kg': 65.0,
        'activity_level': 'moderate',
        'emergency_contact_phone': '090-1234-5678',
        'insurance_number': '12345678'
    }
    
    errors = validate_profile_data(test_data)
    if errors:
        print("バリデーションエラー:")
        for error in errors:
            print(f"  {error.field}: {error.message}")
    else:
        print("バリデーション成功: すべてのデータが有効です")
