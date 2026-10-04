"""
健身热量记录控制推荐系统 —— 核心算法模块

包含基础代谢计算模型、每日总消耗、热量缺口算法，
以及个性化饮食与运动方案推荐逻辑。

算法说明：
1. 基础代谢率(BMR) 采用 Mifflin-St Jeor 公式（1990 年提出，公认精度较高）。
2. 每日总能量消耗(TDEE) = BMR × 活动系数。
3. 减脂热量缺口：在 TDEE 基础上扣除一定热量，形成负能量平衡。
   每日缺口 300~500 kcal，约每周减重 0.3~0.5 kg，属安全范围。
4. 运动消耗采用代谢当量(MET)法：消耗(kcal) = MET × 体重(kg) × 时长(小时)。
"""

from datetime import date
from typing import Optional


# ---------------------------------------------------------------
# 活动系数（体力活动水平，PAL）
# ---------------------------------------------------------------
ACTIVITY_LEVELS = {
    "sedentary": {"name": "久坐少动", "factor": 1.2, "desc": "几乎不运动，办公室工作"},
    "light":     {"name": "轻度活动", "factor": 1.375, "desc": "每周运动 1~3 次"},
    "moderate":  {"name": "中度活动", "factor": 1.55, "desc": "每周运动 3~5 次"},
    "high":      {"name": "高度活动", "factor": 1.725, "desc": "每周运动 6~7 次"},
    "extreme":   {"name": "极高活动", "factor": 1.9, "desc": "体力劳动或每天高强度训练"},
}

# 减脂目标与建议缺口（kcal/天）
GOAL_DEFICIT = {
    "mild":   {"name": "温和减脂", "deficit": 300, "weekly": 0.25, "desc": "每周约减 0.25 kg"},
    "normal": {"name": "标准减脂", "deficit": 500, "weekly": 0.45, "desc": "每周约减 0.45 kg"},
    "strict": {"name": "强化减脂", "deficit": 700, "weekly": 0.65, "desc": "每周约减 0.65 kg，需配合运动"},
}


def calc_bmr(gender: str, age: int, height_cm: float, weight_kg: float) -> float:
    """
    计算基础代谢率(BMR)。

    采用 Mifflin-St Jeor 公式：
      男性：BMR = 10×体重 + 6.25×身高 - 5×年龄 + 5
      女性：BMR = 10×体重 + 6.25×身高 - 5×年龄 - 161

    参数：
        gender: "male" 或 "female"
        age: 年龄（岁）
        height_cm: 身高（厘米）
        weight_kg: 体重（公斤）

    返回：BMR（千卡/天）
    """
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    if gender == "male":
        return base + 5
    elif gender == "female":
        return base - 161
    raise ValueError(f"未知性别: {gender}")


def calc_tdee(bmr: float, activity_level: str) -> float:
    """计算每日总能量消耗(TDEE) = BMR × 活动系数。"""
    if activity_level not in ACTIVITY_LEVELS:
        raise ValueError(f"未知活动水平: {activity_level}")
    return bmr * ACTIVITY_LEVELS[activity_level]["factor"]


def calc_target_intake(tdee: float, goal: str) -> float:
    """
    计算减脂目标下的每日建议摄入热量。

    目标摄入 = TDEE - 热量缺口。
    为保证健康，最低摄入不低于 1200 kcal（基础安全下限）。
    """
    if goal not in GOAL_DEFICIT:
        raise ValueError(f"未知减脂目标: {goal}")
    target = tdee - GOAL_DEFICIT[goal]["deficit"]
    return max(target, 1200.0)


def calc_exercise_calories(met: float, weight_kg: float, minutes: float) -> float:
    """
    计算一次运动的消耗热量。

    采用代谢当量(MET)法：消耗(kcal) = MET × 体重(kg) × 时长(小时)。
    """
    return met * weight_kg * (minutes / 60.0)


def calc_food_calories(calories_per_100g: float, amount_g: float) -> float:
    """根据食物每 100g 热量与摄入克数，计算摄入热量。"""
    return calories_per_100g * amount_g / 100.0


# ---------------------------------------------------------------
# 个性化方案推荐
# ---------------------------------------------------------------

def build_recommendation(
    gender: str, age: int, height_cm: float, weight_kg: float,
    activity_level: str, goal: str,
) -> dict:
    """
    综合计算并生成个性化方案。

    返回字典，包含 BMR、TDEE、目标摄入、热量缺口、
    三大营养素配比建议、运动建议等。
    """
    bmr = calc_bmr(gender, age, height_cm, weight_kg)
    tdee = calc_tdee(bmr, activity_level)
    target = calc_target_intake(tdee, goal)
    deficit = tdee - target
    goal_info = GOAL_DEFICIT[goal]
    activity_info = ACTIVITY_LEVELS[activity_level]

    # 减脂期三大营养素供能比：蛋白质 30% / 碳水 40% / 脂肪 30%
    protein_kcal = target * 0.30
    carb_kcal = target * 0.40
    fat_kcal = target * 0.30
    # 每克供能：蛋白质 4 kcal、碳水 4 kcal、脂肪 9 kcal
    protein_g = protein_kcal / 4.0
    carb_g = carb_kcal / 4.0
    fat_g = fat_kcal / 9.0

    # 蛋白质摄入按体重调整：减脂期建议 1.6~2.0 g/kg 体重
    protein_by_weight = weight_kg * 1.8

    return {
        "bmr": round(bmr, 1),
        "tdee": round(tdee, 1),
        "target_intake": round(target, 1),
        "deficit": round(deficit, 1),
        "goal_name": goal_info["name"],
        "goal_weekly": goal_info["weekly"],
        "goal_desc": goal_info["desc"],
        "activity_name": activity_info["name"],
        "activity_factor": activity_info["factor"],
        "protein_g": round(max(protein_g, protein_by_weight), 1),
        "carb_g": round(carb_g, 1),
        "fat_g": round(fat_g, 1),
        "water_ml": round(weight_kg * 40, 0),  # 建议饮水量 40ml/kg
    }


# ---------------------------------------------------------------
# 每日汇总
# ---------------------------------------------------------------

def daily_summary(target_intake: float, intake: float, burned: float) -> dict:
    """
    汇总某日的摄入、消耗与热量平衡。

    返回：摄入、消耗、目标、剩余可摄入、净摄入等。
    """
    net = intake - burned  # 净摄入（扣除运动消耗后）
    remaining = target_intake - net
    return {
        "intake": round(intake, 1),
        "burned": round(burned, 1),
        "target": round(target_intake, 1),
        "net": round(net, 1),
        "remaining": round(remaining, 1),
        "status": "达标" if -100 <= remaining <= 100 else ("超了" if remaining < -100 else "可多吃"),
    }
