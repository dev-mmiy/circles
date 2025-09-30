"""
健康データ計算用のユーティリティ関数
"""

import math
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

@dataclass
class BMIResult:
    """BMI計算結果"""
    bmi: float
    category: str
    description: str

@dataclass
class HealthProgress:
    """健康目標の進捗"""
    current_weight: Optional[float]
    target_weight: Optional[float]
    weight_difference: Optional[float]
    progress_percentage: Optional[float]
    bmi_current: Optional[BMIResult]
    bmi_target: Optional[BMIResult]

def calculate_bmi(weight_kg: float, height_cm: float) -> BMIResult:
    """
    BMIを計算する
    
    Args:
        weight_kg: 体重（kg）
        height_cm: 身長（cm）
    
    Returns:
        BMIResult: BMI値、カテゴリ、説明
    """
    if height_cm <= 0 or weight_kg <= 0:
        raise ValueError("身長と体重は正の値である必要があります")
    
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    
    # BMIカテゴリの判定
    if bmi < 18.5:
        category = "低体重"
        description = "やせすぎの可能性があります"
    elif bmi < 25:
        category = "普通体重"
        description = "健康的な体重です"
    elif bmi < 30:
        category = "肥満（1度）"
        description = "軽度の肥満です"
    elif bmi < 35:
        category = "肥満（2度）"
        description = "中等度の肥満です"
    else:
        category = "肥満（3度）"
        description = "高度の肥満です"
    
    return BMIResult(bmi=round(bmi, 1), category=category, description=description)

def calculate_ideal_weight(height_cm: float, gender: str = "male") -> float:
    """
    理想体重を計算する（BMI 22を基準）
    
    Args:
        height_cm: 身長（cm）
        gender: 性別（"male" or "female"）
    
    Returns:
        float: 理想体重（kg）
    """
    height_m = height_cm / 100
    ideal_bmi = 22.0
    return round(ideal_bmi * (height_m ** 2), 1)

def calculate_weight_change_rate(current_weight: float, target_weight: float, days: int) -> float:
    """
    体重変化率を計算する
    
    Args:
        current_weight: 現在の体重（kg）
        target_weight: 目標体重（kg）
        days: 期間（日数）
    
    Returns:
        float: 1日あたりの体重変化率（kg/日）
    """
    if days <= 0:
        return 0.0
    
    weight_difference = target_weight - current_weight
    return round(weight_difference / days, 3)

def calculate_body_fat_mass(weight_kg: float, body_fat_percentage: float) -> float:
    """
    体脂肪量を計算する
    
    Args:
        weight_kg: 体重（kg）
        body_fat_percentage: 体脂肪率（%）
    
    Returns:
        float: 体脂肪量（kg）
    """
    return round(weight_kg * (body_fat_percentage / 100), 1)

def calculate_lean_body_mass(weight_kg: float, body_fat_percentage: float) -> float:
    """
    除脂肪体重を計算する
    
    Args:
        weight_kg: 体重（kg）
        body_fat_percentage: 体脂肪率（%）
    
    Returns:
        float: 除脂肪体重（kg）
    """
    body_fat_mass = calculate_body_fat_mass(weight_kg, body_fat_percentage)
    return round(weight_kg - body_fat_mass, 1)

def calculate_health_progress(
    current_weight: Optional[float],
    target_weight: Optional[float],
    height_cm: Optional[float],
    current_body_fat: Optional[float] = None,
    target_body_fat: Optional[float] = None
) -> HealthProgress:
    """
    健康目標の進捗を計算する
    
    Args:
        current_weight: 現在の体重（kg）
        target_weight: 目標体重（kg）
        height_cm: 身長（cm）
        current_body_fat: 現在の体脂肪率（%）
        target_body_fat: 目標体脂肪率（%）
    
    Returns:
        HealthProgress: 健康進捗情報
    """
    # BMI計算
    bmi_current = None
    bmi_target = None
    
    if current_weight and height_cm:
        bmi_current = calculate_bmi(current_weight, height_cm)
    
    if target_weight and height_cm:
        bmi_target = calculate_bmi(target_weight, height_cm)
    
    # 体重差と進捗率の計算
    weight_difference = None
    progress_percentage = None
    
    if current_weight and target_weight:
        weight_difference = round(target_weight - current_weight, 1)
        
        # 進捗率の計算（目標に向かっての進捗）
        if weight_difference != 0:
            # 理想体重からの距離で進捗を計算
            ideal_weight = calculate_ideal_weight(height_cm) if height_cm else None
            if ideal_weight:
                current_distance = abs(current_weight - ideal_weight)
                target_distance = abs(target_weight - ideal_weight)
                
                if current_distance > 0:
                    progress_percentage = round((1 - target_distance / current_distance) * 100, 1)
                    progress_percentage = max(0, min(100, progress_percentage))
    
    return HealthProgress(
        current_weight=current_weight,
        target_weight=target_weight,
        weight_difference=weight_difference,
        progress_percentage=progress_percentage,
        bmi_current=bmi_current,
        bmi_target=bmi_target
    )

def get_activity_level_calories(weight_kg: float, height_cm: float, age: int, gender: str, activity_level: str) -> Dict[str, float]:
    """
    活動レベルに基づく必要カロリーを計算する
    
    Args:
        weight_kg: 体重（kg）
        height_cm: 身長（cm）
        age: 年齢
        gender: 性別
        activity_level: 活動レベル（"low", "moderate", "high"）
    
    Returns:
        Dict[str, float]: 基礎代謝量と必要カロリー
    """
    # 基礎代謝量の計算（ハリス・ベネディクト式）
    if gender == "male":
        bmr = 88.362 + (13.397 * weight_kg) + (4.799 * height_cm) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight_kg) + (3.098 * height_cm) - (4.330 * age)
    
    # 活動レベル係数
    activity_multipliers = {
        "low": 1.2,      # ほとんど運動しない
        "moderate": 1.55, # 適度な運動
        "high": 1.725     # 激しい運動
    }
    
    multiplier = activity_multipliers.get(activity_level, 1.2)
    daily_calories = round(bmr * multiplier)
    
    return {
        "basal_metabolic_rate": round(bmr),
        "daily_calories": daily_calories,
        "activity_level": activity_level,
        "multiplier": multiplier
    }

def calculate_weight_loss_plan(
    current_weight: float,
    target_weight: float,
    height_cm: float,
    age: int,
    gender: str,
    activity_level: str,
    target_weeks: int = 12
) -> Dict[str, Any]:
    """
    減量計画を計算する
    
    Args:
        current_weight: 現在の体重（kg）
        target_weight: 目標体重（kg）
        height_cm: 身長（cm）
        age: 年齢
        gender: 性別
        activity_level: 活動レベル
        target_weeks: 目標期間（週）
    
    Returns:
        Dict[str, Any]: 減量計画の詳細
    """
    weight_difference = target_weight - current_weight
    weekly_loss = abs(weight_difference) / target_weeks
    
    # 健康的な減量ペース（週0.5-1kg）
    if weekly_loss > 1.0:
        recommended_weeks = math.ceil(abs(weight_difference) / 1.0)
        weekly_loss = 1.0
    elif weekly_loss < 0.5:
        recommended_weeks = math.ceil(abs(weight_difference) / 0.5)
        weekly_loss = 0.5
    
    # 必要カロリーの計算
    calories_info = get_activity_level_calories(current_weight, height_cm, age, gender, activity_level)
    
    # 減量に必要なカロリー不足
    daily_deficit = (weekly_loss * 7700) / 7  # 1kg脂肪 = 7700kcal
    target_calories = max(1200, calories_info["daily_calories"] - daily_deficit)
    
    return {
        "current_weight": current_weight,
        "target_weight": target_weight,
        "weight_difference": round(weight_difference, 1),
        "weekly_loss_kg": round(weekly_loss, 1),
        "target_weeks": target_weeks,
        "daily_calories": calories_info["daily_calories"],
        "target_daily_calories": round(target_calories),
        "daily_deficit": round(daily_deficit),
        "is_healthy_pace": 0.5 <= weekly_loss <= 1.0,
        "recommendations": _get_weight_loss_recommendations(weekly_loss)
    }

def _get_weight_loss_recommendations(weekly_loss: float) -> List[str]:
    """減量ペースに基づく推奨事項"""
    recommendations = []
    
    if weekly_loss > 1.0:
        recommendations.append("減量ペースが速すぎます。週0.5-1kg程度に調整することをお勧めします。")
    elif weekly_loss < 0.5:
        recommendations.append("より積極的な減量が可能です。運動量を増やすか、食事制限を強化してください。")
    else:
        recommendations.append("健康的な減量ペースです。このペースを維持してください。")
    
    if weekly_loss > 0:
        recommendations.append("定期的な運動とバランスの取れた食事を心がけてください。")
        recommendations.append("水分補給を十分に行い、十分な睡眠を取ってください。")
    
    return recommendations

def calculate_age_from_birth_date(birth_date: str) -> int:
    """
    生年月日から年齢を計算する
    
    Args:
        birth_date: 生年月日（YYYY-MM-DD形式）
    
    Returns:
        int: 年齢
    """
    try:
        birth = datetime.strptime(birth_date, '%Y-%m-%d').date()
        today = date.today()
        age = today.year - birth.year
        
        # 誕生日がまだ来ていない場合は1歳引く
        if (today.month, today.day) < (birth.month, birth.day):
            age -= 1
        
        return age
    except ValueError:
        return 0

if __name__ == "__main__":
    # テスト用のサンプル計算
    print("=== 健康計算テスト ===")
    
    # BMI計算テスト
    bmi_result = calculate_bmi(65.0, 170.0)
    print(f"BMI: {bmi_result.bmi} ({bmi_result.category})")
    
    # 理想体重計算
    ideal_weight = calculate_ideal_weight(170.0)
    print(f"理想体重: {ideal_weight}kg")
    
    # 健康進捗計算
    progress = calculate_health_progress(70.0, 65.0, 170.0, 20.0, 18.0)
    print(f"体重差: {progress.weight_difference}kg")
    print(f"進捗率: {progress.progress_percentage}%")
    
    # 活動レベル別カロリー計算
    calories = get_activity_level_calories(65.0, 170.0, 30, "male", "moderate")
    print(f"必要カロリー: {calories['daily_calories']}kcal/日")
