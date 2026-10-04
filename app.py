"""
健身热量记录控制推荐系统 —— Flask 主应用

启动方式：
    pip install -r requirements.txt
    python app.py
然后浏览器访问 http://127.0.0.1:5000
"""

from datetime import date

from flask import Flask, render_template, request, redirect, url_for, jsonify, abort

import algorithms as algo
import database as db

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

# 启动时初始化数据库（幂等：建表 + 空库写入种子数据）
db.init_db()


# ---------------------------------------------------------------
# 页面路由
# ---------------------------------------------------------------

@app.route("/")
def index():
    """首页/仪表盘：展示今日摄入、消耗、热量平衡与近7日趋势。"""
    profile = db.get_profile()
    today = date.today().isoformat()
    intake = db.sum_diet_calories(today)
    burned = db.sum_exercise_calories(today)

    rec = algo.build_recommendation(
        profile.get("gender", "male"),
        profile.get("age", 22),
        profile.get("height_cm", 170),
        profile.get("weight_kg", 65),
        profile.get("activity_level", "sedentary"),
        profile.get("goal", "normal"),
    )
    summary = algo.daily_summary(rec["target_intake"], intake, burned)
    trend = db.recent_days_summary(7)

    return render_template(
        "index.html",
        profile=profile,
        rec=rec,
        summary=summary,
        trend=trend,
        today=today,
    )


@app.route("/diet", methods=["GET"])
def diet():
    """饮食记录页：展示食物库与今日饮食记录。"""
    today = date.today().isoformat()
    foods = db.search_foods()
    records = db.get_diet_records(today)
    total = db.sum_diet_calories(today)
    return render_template(
        "diet.html", foods=foods, records=records, total=total, today=today
    )


@app.route("/exercise", methods=["GET"])
def exercise():
    """运动记录页：展示运动库与今日运动记录。"""
    today = date.today().isoformat()
    exercises = db.search_exercises()
    records = db.get_exercise_records(today)
    total = db.sum_exercise_calories(today)
    return render_template(
        "exercise.html", exercises=exercises, records=records, total=total, today=today
    )


@app.route("/recommend")
def recommend():
    """方案推荐页：根据个人档案生成个性化饮食运动方案。"""
    profile = db.get_profile()
    rec = algo.build_recommendation(
        profile.get("gender", "male"),
        profile.get("age", 22),
        profile.get("height_cm", 170),
        profile.get("weight_kg", 65),
        profile.get("activity_level", "sedentary"),
        profile.get("goal", "normal"),
    )
    return render_template("recommend.html", profile=profile, rec=rec)


@app.route("/profile", methods=["GET", "POST"])
def profile():
    """个人档案页：查看/编辑基础信息。"""
    if request.method == "POST":
        db.update_profile(
            gender=request.form.get("gender", "male"),
            age=int(request.form.get("age", 22)),
            height_cm=float(request.form.get("height_cm", 170)),
            weight_kg=float(request.form.get("weight_kg", 65)),
            activity_level=request.form.get("activity_level", "sedentary"),
            goal=request.form.get("goal", "normal"),
            target_weight=float(request.form.get("target_weight", 60) or 60),
        )
        return redirect(url_for("recommend"))
    profile = db.get_profile()
    return render_template("profile.html", profile=profile)


# ---------------------------------------------------------------
# API 路由（前端 AJAX 调用）
# ---------------------------------------------------------------

@app.route("/api/profile", methods=["GET"])
def api_profile():
    return jsonify(db.get_profile())


@app.route("/api/foods")
def api_foods():
    kw = request.args.get("q", "")
    return jsonify(db.search_foods(kw))


@app.route("/api/exercises")
def api_exercises():
    kw = request.args.get("q", "")
    return jsonify(db.search_exercises(kw))


@app.route("/api/diet", methods=["POST"])
def api_add_diet():
    """新增饮食记录。参数：food_id, amount_g, record_date（可选，默认今天）。"""
    data = request.get_json(force=True)
    food = db.get_food_by_id(int(data.get("food_id", 0)))
    if not food:
        return jsonify({"error": "食物不存在"}), 404
    amount_g = float(data.get("amount_g", 0))
    calories = algo.calc_food_calories(food["calories_per_100g"], amount_g)
    record_date = data.get("record_date", date.today().isoformat())
    db.add_diet_record(
        record_date=record_date,
        meal_type=data.get("meal_type", "lunch"),
        food_name=food["name"],
        amount_g=amount_g,
        calories=calories,
    )
    return jsonify({"ok": True, "calories": round(calories, 1)})


@app.route("/api/exercise", methods=["POST"])
def api_add_exercise():
    """新增运动记录。参数：exercise_id, minutes, record_date（可选）。"""
    data = request.get_json(force=True)
    ex = db.get_exercise_by_id(int(data.get("exercise_id", 0)))
    if not ex:
        return jsonify({"error": "运动不存在"}), 404
    minutes = float(data.get("minutes", 0))
    profile = db.get_profile()
    calories = algo.calc_exercise_calories(ex["met"], profile.get("weight_kg", 65), minutes)
    record_date = data.get("record_date", date.today().isoformat())
    db.add_exercise_record(
        record_date=record_date,
        exercise_name=ex["name"],
        minutes=minutes,
        calories=calories,
    )
    return jsonify({"ok": True, "calories": round(calories, 1)})


@app.route("/api/diet/<int:record_id>", methods=["DELETE"])
def api_delete_diet(record_id):
    db.delete_diet_record(record_id)
    return jsonify({"ok": True})


@app.route("/api/exercise/<int:record_id>", methods=["DELETE"])
def api_delete_exercise(record_id):
    db.delete_exercise_record(record_id)
    return jsonify({"ok": True})


@app.route("/api/recommend", methods=["GET"])
def api_recommend():
    profile = db.get_profile()
    rec = algo.build_recommendation(
        profile.get("gender", "male"),
        profile.get("age", 22),
        profile.get("height_cm", 170),
        profile.get("weight_kg", 65),
        profile.get("activity_level", "sedentary"),
        profile.get("goal", "normal"),
    )
    return jsonify(rec)


@app.route("/api/summary/<record_date>")
def api_summary(record_date):
    intake = db.sum_diet_calories(record_date)
    burned = db.sum_exercise_calories(record_date)
    profile = db.get_profile()
    rec = algo.build_recommendation(
        profile.get("gender", "male"),
        profile.get("age", 22),
        profile.get("height_cm", 170),
        profile.get("weight_kg", 65),
        profile.get("activity_level", "sedentary"),
        profile.get("goal", "normal"),
    )
    summary = algo.daily_summary(rec["target_intake"], intake, burned)
    summary.update({"intake": intake, "burned": burned})
    return jsonify(summary)


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
