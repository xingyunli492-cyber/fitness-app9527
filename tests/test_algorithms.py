"""
algorithms.py 单元测试

覆盖基础代谢、TDEE、目标摄入、运动消耗、食物热量、推荐方案与每日汇总。
采用 pytest，语句覆盖率目标 ≥ 90%。
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

import algorithms as algo


# ---------------------------------------------------------------
# calc_bmr：基础代谢率
# ---------------------------------------------------------------
class TestCalcBmr:
    def test_male(self):
        # 男：10*70 + 6.25*175 - 5*25 + 5 = 1673.75
        assert algo.calc_bmr("male", 25, 175, 70) == pytest.approx(1673.75)

    def test_female(self):
        # 女：10*55 + 6.25*160 - 5*25 - 161 = 1264.0
        assert algo.calc_bmr("female", 25, 160, 55) == pytest.approx(1264.0)

    def test_invalid_gender(self):
        with pytest.raises(ValueError):
            algo.calc_bmr("other", 25, 175, 70)


# ---------------------------------------------------------------
# calc_tdee：每日总消耗
# ---------------------------------------------------------------
class TestCalcTdee:
    def test_sedentary(self):
        assert algo.calc_tdee(1500, "sedentary") == pytest.approx(1800.0)

    def test_moderate(self):
        assert algo.calc_tdee(1500, "moderate") == pytest.approx(2325.0)

    def test_invalid_level(self):
        with pytest.raises(ValueError):
            algo.calc_tdee(1500, "unknown")


# ---------------------------------------------------------------
# calc_target_intake：目标摄入
# ---------------------------------------------------------------
class TestCalcTargetIntake:
    def test_normal(self):
        assert algo.calc_target_intake(2300, "normal") == pytest.approx(1800.0)

    def test_safety_floor(self):
        # 1500 - 700 = 800，低于下限 1200，应保护为 1200
        assert algo.calc_target_intake(1500, "strict") == pytest.approx(1200.0)

    def test_invalid_goal(self):
        with pytest.raises(ValueError):
            algo.calc_target_intake(2000, "unknown")


# ---------------------------------------------------------------
# calc_exercise_calories：运动消耗
# ---------------------------------------------------------------
class TestCalcExerciseCalories:
    def test_running(self):
        # 8 MET × 70kg × 0.5h = 280
        assert algo.calc_exercise_calories(8, 70, 30) == pytest.approx(280.0)

    def test_zero_minutes(self):
        assert algo.calc_exercise_calories(8, 70, 0) == 0


# ---------------------------------------------------------------
# calc_food_calories：食物热量
# ---------------------------------------------------------------
class TestCalcFoodCalories:
    def test_rice(self):
        # 116 kcal/100g × 200g = 232
        assert algo.calc_food_calories(116, 200) == pytest.approx(232.0)

    def test_zero_amount(self):
        assert algo.calc_food_calories(116, 0) == 0


# ---------------------------------------------------------------
# build_recommendation：推荐方案
# ---------------------------------------------------------------
class TestBuildRecommendation:
    def test_standard_male(self):
        rec = algo.build_recommendation("male", 22, 175, 80, "light", "normal")
        # BMR = 10*80 + 6.25*175 - 5*22 + 5 = 1788.75
        assert rec["bmr"] == pytest.approx(1788.75, abs=0.1)
        # TDEE = 1788.75 * 1.375 ≈ 2459.5
        assert rec["tdee"] == pytest.approx(2459.5, abs=0.1)
        # 目标摄入 = 2459.5 - 500 ≈ 1959.5
        assert rec["target_intake"] == pytest.approx(1959.5, abs=0.1)
        assert rec["deficit"] == pytest.approx(500.0, abs=0.1)
        assert rec["protein_g"] > 0
        assert rec["carb_g"] > 0
        assert rec["fat_g"] > 0
        assert rec["water_ml"] > 0

    def test_protein_by_weight(self):
        # 蛋白质按 1.8g/kg 修正：80kg → 144g，应大于按 30% 供能算出的值
        rec = algo.build_recommendation("male", 22, 175, 80, "light", "normal")
        assert rec["protein_g"] >= 144.0 - 0.1


# ---------------------------------------------------------------
# daily_summary：每日汇总
# ---------------------------------------------------------------
class TestDailySummary:
    def test_balanced(self):
        s = algo.daily_summary(2000, 1500, 400)
        # net = 1100, remaining = 900
        assert s["net"] == pytest.approx(1100.0)
        assert s["remaining"] == pytest.approx(900.0)
        assert s["status"] == "可多吃"

    def test_over(self):
        s = algo.daily_summary(2000, 2500, 200)
        assert s["remaining"] < -100
        assert s["status"] == "超了"

    def test_on_target(self):
        s = algo.daily_summary(2000, 1900, 0)
        assert s["status"] == "达标"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
