"""
健康計算機能のテスト
"""

import pytest
from health_calculations import (
    calculate_bmi, calculate_ideal_weight, calculate_health_progress,
    get_activity_level_calories, calculate_weight_loss_plan,
    calculate_age_from_birth_date, BMIResult
)

class TestHealthCalculations:
    """健康計算機能のテスト"""
    
    def test_calculate_bmi(self):
        """BMI計算のテスト"""
        # 正常なBMI計算
        result = calculate_bmi(65.0, 170.0)
        assert isinstance(result, BMIResult)
        assert result.bmi == 22.5
        assert result.category == "普通体重"
        assert "健康的な体重" in result.description
        
        # 低体重
        result = calculate_bmi(50.0, 170.0)
        assert result.bmi == 17.3
        assert result.category == "低体重"
        
        # 肥満
        result = calculate_bmi(90.0, 170.0)
        assert result.bmi == 31.1
        assert result.category == "肥満（2度）"
    
    def test_calculate_bmi_invalid_input(self):
        """BMI計算の無効な入力テスト"""
        with pytest.raises(ValueError):
            calculate_bmi(0, 170.0)
        
        with pytest.raises(ValueError):
            calculate_bmi(65.0, 0)
        
        with pytest.raises(ValueError):
            calculate_bmi(-10.0, 170.0)
    
    def test_calculate_ideal_weight(self):
        """理想体重計算のテスト"""
        # 男性の理想体重
        ideal_weight = calculate_ideal_weight(170.0, "male")
        assert ideal_weight == 63.6
        
        # 女性の理想体重（同じ身長）
        ideal_weight = calculate_ideal_weight(170.0, "female")
        assert ideal_weight == 63.6  # BMI 22基準なので性別に関係なく同じ
    
    def test_calculate_health_progress(self):
        """健康進捗計算のテスト"""
        progress = calculate_health_progress(
            current_weight=70.0,
            target_weight=65.0,
            height_cm=170.0,
            current_body_fat=20.0,
            target_body_fat=18.0
        )
        
        assert progress.current_weight == 70.0
        assert progress.target_weight == 65.0
        assert progress.weight_difference == -5.0
        assert progress.bmi_current is not None
        assert progress.bmi_target is not None
        assert progress.bmi_current.bmi == 24.2
        assert progress.bmi_target.bmi == 22.5
    
    def test_calculate_health_progress_partial_data(self):
        """部分的なデータでの健康進捗計算テスト"""
        progress = calculate_health_progress(
            current_weight=70.0,
            target_weight=65.0,
            height_cm=170.0
        )
        
        assert progress.current_weight == 70.0
        assert progress.target_weight == 65.0
        assert progress.weight_difference == -5.0
        assert progress.bmi_current is not None
        assert progress.bmi_target is not None
    
    def test_get_activity_level_calories(self):
        """活動レベル別カロリー計算のテスト"""
        calories = get_activity_level_calories(
            weight_kg=65.0,
            height_cm=170.0,
            age=30,
            gender="male",
            activity_level="moderate"
        )
        
        assert "basal_metabolic_rate" in calories
        assert "daily_calories" in calories
        assert "activity_level" in calories
        assert "multiplier" in calories
        assert calories["activity_level"] == "moderate"
        assert calories["multiplier"] == 1.55
        assert calories["daily_calories"] > calories["basal_metabolic_rate"]
    
    def test_get_activity_level_calories_different_levels(self):
        """異なる活動レベルのカロリー計算テスト"""
        # 低活動レベル
        low_calories = get_activity_level_calories(65.0, 170.0, 30, "male", "low")
        # 高活動レベル
        high_calories = get_activity_level_calories(65.0, 170.0, 30, "male", "high")
        
        assert high_calories["daily_calories"] > low_calories["daily_calories"]
        assert high_calories["multiplier"] > low_calories["multiplier"]
    
    def test_calculate_weight_loss_plan(self):
        """減量計画計算のテスト"""
        plan = calculate_weight_loss_plan(
            current_weight=70.0,
            target_weight=65.0,
            height_cm=170.0,
            age=30,
            gender="male",
            activity_level="moderate",
            target_weeks=10
        )
        
        assert plan["current_weight"] == 70.0
        assert plan["target_weight"] == 65.0
        assert plan["weight_difference"] == -5.0
        assert plan["weekly_loss_kg"] <= 1.0  # 健康的な減量ペース
        assert plan["target_weeks"] == 10
        assert "daily_calories" in plan
        assert "target_daily_calories" in plan
        assert "recommendations" in plan
        assert len(plan["recommendations"]) > 0
    
    def test_calculate_weight_loss_plan_aggressive(self):
        """積極的な減量計画のテスト"""
        plan = calculate_weight_loss_plan(
            current_weight=80.0,
            target_weight=60.0,
            height_cm=170.0,
            age=30,
            gender="male",
            activity_level="moderate",
            target_weeks=5  # 短い期間
        )
        
        # 健康的な減量ペースに調整される
        assert plan["weekly_loss_kg"] <= 1.0
        assert plan["is_healthy_pace"] == True
    
    def test_calculate_age_from_birth_date(self):
        """生年月日からの年齢計算テスト"""
        # 1990年生まれ（2025年時点で35歳）
        age = calculate_age_from_birth_date("1990-01-01")
        assert age == 35
        
        # 2000年生まれ（2025年時点で25歳）
        age = calculate_age_from_birth_date("2000-12-31")
        assert age == 24
        
        # 無効な日付
        age = calculate_age_from_birth_date("invalid-date")
        assert age == 0
    
    def test_calculate_bmi_categories(self):
        """BMIカテゴリの境界値テスト"""
        # 各カテゴリの代表的なBMI値でテスト
        test_cases = [
            (17.0, "低体重"),      # 低体重
            (22.0, "普通体重"),     # 普通体重
            (27.0, "肥満（1度）"),  # 肥満（1度）
            (32.0, "肥満（2度）"),  # 肥満（2度）
            (37.0, "肥満（3度）")   # 肥満（3度）
        ]
        
        for expected_bmi, expected_category in test_cases:
            # BMI値から逆算して体重を計算
            height_m = 1.70
            weight_kg = expected_bmi * (height_m ** 2)
            
            result = calculate_bmi(weight_kg, 170.0)
            assert result.category == expected_category
    
    def test_health_progress_edge_cases(self):
        """健康進捗計算のエッジケーステスト"""
        # 目標体重が現在体重と同じ場合
        progress = calculate_health_progress(65.0, 65.0, 170.0)
        assert progress.weight_difference == 0.0
        
        # 目標体重が現在体重より重い場合（増量）
        progress = calculate_health_progress(60.0, 65.0, 170.0)
        assert progress.weight_difference == 5.0
        
        # 身長が未設定の場合
        progress = calculate_health_progress(70.0, 65.0, None)
        assert progress.bmi_current is None
        assert progress.bmi_target is None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
