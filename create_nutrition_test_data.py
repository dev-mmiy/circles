#!/usr/bin/env python3
"""
栄養管理機能のテストデータ作成スクリプト
"""

import os
import sys
from sqlmodel import Session, create_engine, SQLModel
from nutrition_models import *
from datetime import datetime, date
from decimal import Decimal

def create_nutrition_test_data():
    """栄養管理のテストデータを作成"""
    print("🍎 栄養管理テストデータを作成中...")
    
    # データベース接続
    database_url = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    engine = create_engine(database_url, echo=False, connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        # 1. 疾患別栄養要件を作成
        print("📋 疾患別栄養要件を作成中...")
        disease_requirements = [
            # 心不全
            {
                "disease_type": DiseaseType.HEART_FAILURE,
                "nutrient_type": NutrientType.SODIUM,
                "daily_target_max": Decimal("2.0"),  # 2g/日以下
                "unit": "g",
                "description": "心不全患者の塩分制限",
                "is_critical": True
            },
            {
                "disease_type": DiseaseType.HEART_FAILURE,
                "nutrient_type": NutrientType.POTASSIUM,
                "daily_target_min": Decimal("3.5"),  # 3.5g/日以上
                "daily_target_max": Decimal("5.0"),  # 5.0g/日以下
                "unit": "g",
                "description": "心不全患者のカリウム管理",
                "is_critical": True
            },
            # 糖尿病
            {
                "disease_type": DiseaseType.DIABETES,
                "nutrient_type": NutrientType.CARBOHYDRATE,
                "daily_target_max": Decimal("130"),  # 130g/日以下
                "unit": "g",
                "description": "糖尿病患者の炭水化物制限",
                "is_critical": True
            },
            {
                "disease_type": DiseaseType.DIABETES,
                "nutrient_type": NutrientType.SUGAR,
                "daily_target_max": Decimal("25"),  # 25g/日以下
                "unit": "g",
                "description": "糖尿病患者の糖質制限",
                "is_critical": True
            },
            # 腎疾患
            {
                "disease_type": DiseaseType.KIDNEY_DISEASE,
                "nutrient_type": NutrientType.PHOSPHORUS,
                "daily_target_max": Decimal("0.8"),  # 0.8g/日以下
                "unit": "g",
                "description": "腎疾患患者のリン制限",
                "is_critical": True
            },
            {
                "disease_type": DiseaseType.KIDNEY_DISEASE,
                "nutrient_type": NutrientType.POTASSIUM,
                "daily_target_max": Decimal("2.0"),  # 2.0g/日以下
                "unit": "g",
                "description": "腎疾患患者のカリウム制限",
                "is_critical": True
            }
        ]
        
        for req_data in disease_requirements:
            existing = session.query(DiseaseNutritionRequirement).filter(
                DiseaseNutritionRequirement.disease_type == req_data["disease_type"],
                DiseaseNutritionRequirement.nutrient_type == req_data["nutrient_type"]
            ).first()
            
            if not existing:
                requirement = DiseaseNutritionRequirement(**req_data)
                session.add(requirement)
        
        session.commit()
        print("✅ 疾患別栄養要件を作成しました")
        
        # 2. サンプルメニューを作成
        print("🍽️ サンプルメニューを作成中...")
        sample_menus = [
            {
                "name": "白米（1膳）",
                "description": "精白米のご飯1膳分",
                "serving_size": "1膳（150g）",
                "nutrients": [
                    {"nutrient_type": NutrientType.CALORIES, "amount": Decimal("252"), "unit": "kcal"},
                    {"nutrient_type": NutrientType.CARBOHYDRATE, "amount": Decimal("55.2"), "unit": "g"},
                    {"nutrient_type": NutrientType.PROTEIN, "amount": Decimal("3.8"), "unit": "g"},
                    {"nutrient_type": NutrientType.SODIUM, "amount": Decimal("0.001"), "unit": "g"}
                ]
            },
            {
                "name": "味噌汁（具なし）",
                "description": "具なしの味噌汁1杯",
                "serving_size": "1杯（150ml）",
                "nutrients": [
                    {"nutrient_type": NutrientType.CALORIES, "amount": Decimal("25"), "unit": "kcal"},
                    {"nutrient_type": NutrientType.SODIUM, "amount": Decimal("1.2"), "unit": "g"},
                    {"nutrient_type": NutrientType.PROTEIN, "amount": Decimal("1.5"), "unit": "g"}
                ]
            },
            {
                "name": "焼き魚（サバ）",
                "description": "サバの塩焼き1切れ",
                "serving_size": "1切れ（80g）",
                "nutrients": [
                    {"nutrient_type": NutrientType.CALORIES, "amount": Decimal("247"), "unit": "kcal"},
                    {"nutrient_type": NutrientType.PROTEIN, "amount": Decimal("20.8"), "unit": "g"},
                    {"nutrient_type": NutrientType.FAT, "amount": Decimal("17.2"), "unit": "g"},
                    {"nutrient_type": NutrientType.SODIUM, "amount": Decimal("0.3"), "unit": "g"},
                    {"nutrient_type": NutrientType.POTASSIUM, "amount": Decimal("0.32"), "unit": "g"}
                ]
            },
            {
                "name": "野菜炒め",
                "description": "キャベツ、人参、ピーマンの炒め物",
                "serving_size": "1人分（100g）",
                "nutrients": [
                    {"nutrient_type": NutrientType.CALORIES, "amount": Decimal("45"), "unit": "kcal"},
                    {"nutrient_type": NutrientType.CARBOHYDRATE, "amount": Decimal("8.5"), "unit": "g"},
                    {"nutrient_type": NutrientType.PROTEIN, "amount": Decimal("1.8"), "unit": "g"},
                    {"nutrient_type": NutrientType.FAT, "amount": Decimal("0.5"), "unit": "g"},
                    {"nutrient_type": NutrientType.SODIUM, "amount": Decimal("0.2"), "unit": "g"},
                    {"nutrient_type": NutrientType.POTASSIUM, "amount": Decimal("0.25"), "unit": "g"}
                ]
            },
            {
                "name": "バナナ",
                "description": "中サイズのバナナ1本",
                "serving_size": "1本（100g）",
                "nutrients": [
                    {"nutrient_type": NutrientType.CALORIES, "amount": Decimal("86"), "unit": "kcal"},
                    {"nutrient_type": NutrientType.CARBOHYDRATE, "amount": Decimal("22.8"), "unit": "g"},
                    {"nutrient_type": NutrientType.SUGAR, "amount": Decimal("12.2"), "unit": "g"},
                    {"nutrient_type": NutrientType.POTASSIUM, "amount": Decimal("0.36"), "unit": "g"},
                    {"nutrient_type": NutrientType.FIBER, "amount": Decimal("1.1"), "unit": "g"}
                ]
            },
            {
                "name": "ヨーグルト（無糖）",
                "description": "無糖ヨーグルト1カップ",
                "serving_size": "1カップ（100g）",
                "nutrients": [
                    {"nutrient_type": NutrientType.CALORIES, "amount": Decimal("62"), "unit": "kcal"},
                    {"nutrient_type": NutrientType.PROTEIN, "amount": Decimal("3.6"), "unit": "g"},
                    {"nutrient_type": NutrientType.FAT, "amount": Decimal("3.0"), "unit": "g"},
                    {"nutrient_type": NutrientType.CARBOHYDRATE, "amount": Decimal("4.6"), "unit": "g"},
                    {"nutrient_type": NutrientType.CALCIUM, "amount": Decimal("0.12"), "unit": "g"}
                ]
            }
        ]
        
        created_menus = []
        for menu_data in sample_menus:
            existing = session.query(Menu).filter(Menu.name == menu_data["name"]).first()
            if not existing:
                # メニュー作成
                menu = Menu(
                    name=menu_data["name"],
                    description=menu_data["description"],
                    serving_size=menu_data["serving_size"]
                )
                session.add(menu)
                session.flush()  # IDを取得
                
                # 栄養素情報を追加
                for nutrient_data in menu_data["nutrients"]:
                    nutrient = MenuNutrient(
                        menu_id=menu.id,
                        nutrient_type=nutrient_data["nutrient_type"],
                        amount=nutrient_data["amount"],
                        unit=nutrient_data["unit"]
                    )
                    session.add(nutrient)
                
                created_menus.append(menu)
        
        session.commit()
        print(f"✅ {len(created_menus)}個のサンプルメニューを作成しました")
        
        # 3. サンプルユーザープロフィールを作成
        print("👤 サンプルユーザープロフィールを作成中...")
        sample_profiles = [
            {
                "user_id": 1,  # テストユーザーID
                "disease_types": [DiseaseType.HEART_FAILURE],
                "daily_calorie_target": Decimal("1800"),
                "weight_kg": Decimal("65.0"),
                "height_cm": Decimal("170.0"),
                "activity_level": "moderate"
            },
            {
                "user_id": 2,  # テストユーザーID
                "disease_types": [DiseaseType.DIABETES],
                "daily_calorie_target": Decimal("1600"),
                "weight_kg": Decimal("70.0"),
                "height_cm": Decimal("165.0"),
                "activity_level": "low"
            },
            {
                "user_id": 3,  # テストユーザーID
                "disease_types": [DiseaseType.KIDNEY_DISEASE],
                "daily_calorie_target": Decimal("2000"),
                "weight_kg": Decimal("60.0"),
                "height_cm": Decimal("160.0"),
                "activity_level": "moderate"
            }
        ]
        
        for profile_data in sample_profiles:
            existing = session.query(UserNutritionProfile).filter(
                UserNutritionProfile.user_id == profile_data["user_id"]
            ).first()
            
            if not existing:
                profile = UserNutritionProfile(**profile_data)
                session.add(profile)
        
        session.commit()
        print("✅ サンプルユーザープロフィールを作成しました")
        
        # 4. サンプル食事記録を作成
        print("🍴 サンプル食事記録を作成中...")
        sample_meal_logs = [
            {
                "log_date": date.today(),
                "meal_type": MealType.BREAKFAST,
                "menu_id": 1,  # 白米
                "quantity": Decimal("1.0"),
                "notes": "朝食のご飯"
            },
            {
                "log_date": date.today(),
                "meal_type": MealType.BREAKFAST,
                "menu_id": 2,  # 味噌汁
                "quantity": Decimal("1.0"),
                "notes": "朝食の味噌汁"
            },
            {
                "log_date": date.today(),
                "meal_type": MealType.LUNCH,
                "menu_id": 3,  # 焼き魚
                "quantity": Decimal("1.0"),
                "notes": "昼食の主菜"
            },
            {
                "log_date": date.today(),
                "meal_type": MealType.LUNCH,
                "menu_id": 4,  # 野菜炒め
                "quantity": Decimal("1.0"),
                "notes": "昼食の副菜"
            },
            {
                "log_date": date.today(),
                "meal_type": MealType.SNACK,
                "menu_id": 5,  # バナナ
                "quantity": Decimal("1.0"),
                "notes": "午後の間食"
            }
        ]
        
        for meal_data in sample_meal_logs:
            meal_log = MealLog(**meal_data)
            session.add(meal_log)
        
        session.commit()
        print("✅ サンプル食事記録を作成しました")
        
        return {
            "disease_requirements": len(disease_requirements),
            "menus": len(created_menus),
            "profiles": len(sample_profiles),
            "meal_logs": len(sample_meal_logs)
        }


def print_nutrition_test_info():
    """栄養管理テストデータの情報を表示"""
    print("\n" + "="*60)
    print("🍎 栄養管理機能テストデータ")
    print("="*60)
    
    print("\n📋 作成されたデータ:")
    print("• 疾患別栄養要件: 心不全、糖尿病、腎疾患の管理項目")
    print("• サンプルメニュー: 白米、味噌汁、焼き魚、野菜炒め、バナナ、ヨーグルト")
    print("• ユーザープロフィール: 3つの疾患タイプ別プロフィール")
    print("• 食事記録: 今日のサンプル食事記録")
    
    print("\n🔗 API エンドポイント:")
    print("• GET /nutrition/menus - メニュー一覧")
    print("• POST /nutrition/menus - メニュー作成")
    print("• GET /nutrition/meal-logs - 食事記録一覧")
    print("• POST /nutrition/meal-logs - 食事記録作成")
    print("• GET /nutrition/daily-summary/{user_id}/{date} - 日別栄養サマリー")
    print("• GET /nutrition/nutrition-analysis/{user_id}/{date} - 栄養分析")
    
    print("\n📊 管理可能な栄養素:")
    print("• カロリー、タンパク質、脂質、炭水化物")
    print("• 塩分（ナトリウム）、カリウム、リン")
    print("• カルシウム、鉄、食物繊維、糖質")
    
    print("\n🏥 対応疾患:")
    print("• 心不全: 塩分・カリウム管理")
    print("• 糖尿病: 炭水化物・糖質管理")
    print("• 腎疾患: リン・カリウム管理")
    print("• 高血圧: 塩分管理")
    
    print("\n" + "="*60)


def main():
    """メイン関数"""
    print("🚀 Healthcare Community Platform - 栄養管理テストデータ作成")
    
    # 環境変数の設定
    os.environ.setdefault("DATABASE_URL", "sqlite:///./app.db")
    
    try:
        # テストデータ作成
        result = create_nutrition_test_data()
        
        if result:
            print_nutrition_test_info()
            print(f"\n✅ 栄養管理テストデータの作成が完了しました")
            print(f"   - 疾患別栄養要件: {result['disease_requirements']}件")
            print(f"   - メニュー: {result['menus']}件")
            print(f"   - ユーザープロフィール: {result['profiles']}件")
            print(f"   - 食事記録: {result['meal_logs']}件")
        else:
            print("❌ 栄養管理テストデータの作成に失敗しました")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
