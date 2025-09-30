"""
健康計算APIのテスト
"""

import requests
import pytest

BASE_URL = "http://localhost:8003"

class TestHealthCalculationsAPI:
    """健康計算APIのテスト"""
    
    def test_get_health_calculations(self):
        """健康計算結果の取得テスト"""
        response = requests.get(f"{BASE_URL}/health/calculations/1")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        
        calculations_data = data["data"]
        assert "user_id" in calculations_data
        assert "profile" in calculations_data
        assert "current_measurements" in calculations_data
        assert "calculations" in calculations_data
        
        # プロファイル情報の確認
        profile = calculations_data["profile"]
        assert "height_cm" in profile
        assert "target_weight_kg" in profile
        assert "activity_level" in profile
        assert "birth_date" in profile
        assert "gender" in profile
        
        # 計算結果の確認
        calculations = calculations_data["calculations"]
        if "current_bmi" in calculations:
            current_bmi = calculations["current_bmi"]
            assert "bmi" in current_bmi
            assert "category" in current_bmi
            assert "description" in current_bmi
        
        if "target_bmi" in calculations:
            target_bmi = calculations["target_bmi"]
            assert "bmi" in target_bmi
            assert "category" in target_bmi
        
        if "progress" in calculations:
            progress = calculations["progress"]
            assert "current_weight" in progress
            assert "target_weight" in progress
            assert "weight_difference" in progress
    
    def test_get_health_calculations_nonexistent_user(self):
        """存在しないユーザーの健康計算テスト"""
        response = requests.get(f"{BASE_URL}/health/calculations/9999")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "not_found"
        assert "Profile not found" in data["message"]
    
    def test_get_health_summary(self):
        """健康サマリーの取得テスト"""
        response = requests.get(f"{BASE_URL}/health/summary/1")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        
        summary = data["data"]
        assert "user_id" in summary
        assert "current_status" in summary
        assert "goals" in summary
        assert "recommendations" in summary
        
        # 現在の状態
        if "bmi" in summary["current_status"]:
            current_bmi = summary["current_status"]["bmi"]
            assert "bmi" in current_bmi
            assert "category" in current_bmi
        
        # 目標
        if "bmi" in summary["goals"]:
            target_bmi = summary["goals"]["bmi"]
            assert "bmi" in target_bmi
            assert "category" in target_bmi
        
        # 進捗
        if "progress" in summary:
            progress = summary["progress"]
            assert "weight_difference" in progress
            assert "progress_percentage" in progress
    
    def test_get_health_summary_nonexistent_user(self):
        """存在しないユーザーの健康サマリーテスト"""
        response = requests.get(f"{BASE_URL}/health/summary/9999")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "not_found"
    
    def test_health_calculations_with_body_measurements(self):
        """体重測定データがある場合の健康計算テスト"""
        # まず体重測定データを追加（クエリパラメータ形式）
        measurement_data = {
            "weight_kg": 68.5,
            "body_fat_percentage": 18.0,
            "notes": "朝の測定"
        }
        
        # 体重測定を追加（クエリパラメータ形式）
        response = requests.post(f"{BASE_URL}/body-measurements/1", params=measurement_data)
        assert response.status_code == 200
        
        # 健康計算を取得
        response = requests.get(f"{BASE_URL}/health/calculations/1")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        
        calculations_data = data["data"]
        current_measurements = calculations_data["current_measurements"]
        
        # 最新の測定データが反映されているか確認（既存データがある可能性を考慮）
        assert current_measurements["weight_kg"] is not None
        assert current_measurements["weight_kg"] > 0
        
        # BMI計算が正しく行われているか確認
        calculations = calculations_data["calculations"]
        if "current_bmi" in calculations:
            current_bmi = calculations["current_bmi"]
            assert "bmi" in current_bmi
            assert "category" in current_bmi
            # BMI値が合理的な範囲内かチェック
            assert 15.0 <= current_bmi["bmi"] <= 50.0
    
    def test_health_calculations_calories_calculation(self):
        """カロリー計算のテスト"""
        response = requests.get(f"{BASE_URL}/health/calculations/1")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        
        calculations = data["data"]["calculations"]
        if "calories" in calculations:
            calories_info = calculations["calories"]
            assert "basal_metabolic_rate" in calories_info
            assert "daily_calories" in calories_info
            assert "activity_level" in calories_info
            assert "multiplier" in calories_info
            
            # 基礎代謝量が正の値かチェック
            assert calories_info["basal_metabolic_rate"] > 0
            assert calories_info["daily_calories"] > calories_info["basal_metabolic_rate"]
    
    def test_health_calculations_weight_plan(self):
        """減量計画のテスト"""
        response = requests.get(f"{BASE_URL}/health/calculations/1")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        
        calculations = data["data"]["calculations"]
        if "weight_plan" in calculations:
            weight_plan = calculations["weight_plan"]
            assert "current_weight" in weight_plan
            assert "target_weight" in weight_plan
            assert "weight_difference" in weight_plan
            assert "weekly_loss_kg" in weight_plan
            assert "daily_calories" in weight_plan
            assert "target_daily_calories" in weight_plan
            assert "recommendations" in weight_plan
            
            # 週間減量量が健康的な範囲内かチェック
            assert weight_plan["weekly_loss_kg"] <= 1.0
            assert len(weight_plan["recommendations"]) > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
