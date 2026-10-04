"""
健身热量记录控制推荐系统 —— 数据层

使用 SQLite 作为本地持久化存储，通过标准库 sqlite3 访问，
不依赖任何 ORM，便于课程答辩讲解与本地部署。

数据库文件默认位于项目根目录 fitness.db，首次运行时自动建表并写入种子数据。
"""

import os
import sqlite3
from datetime import date, datetime
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fitness.db")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS user_profile (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    gender          TEXT NOT NULL DEFAULT 'male',      -- male / female
    age             INTEGER NOT NULL DEFAULT 22,
    height_cm       REAL NOT NULL DEFAULT 170,
    weight_kg       REAL NOT NULL DEFAULT 65,
    activity_level  TEXT NOT NULL DEFAULT 'sedentary', -- 活动水平
    goal            TEXT NOT NULL DEFAULT 'normal',    -- 减脂目标
    target_weight   REAL,                              -- 目标体重(kg)
    updated_at      TEXT
);

CREATE TABLE IF NOT EXISTS foods (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    name             TEXT NOT NULL,
    category         TEXT NOT NULL,                    -- 主食/肉蛋/蔬果/乳制品/零食/饮品
    calories_per_100g REAL NOT NULL,                   -- 每100g热量(kcal)
    protein_per_100g REAL DEFAULT 0,                   -- 每100g蛋白质(g)
    fat_per_100g     REAL DEFAULT 0,
    carb_per_100g    REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS exercises (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT NOT NULL,
    met     REAL NOT NULL                              -- 代谢当量
);

CREATE TABLE IF NOT EXISTS diet_records (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    record_date TEXT NOT NULL,                         -- YYYY-MM-DD
    meal_type   TEXT NOT NULL,                         -- breakfast/lunch/dinner/snack
    food_name   TEXT NOT NULL,
    amount_g    REAL NOT NULL,                         -- 摄入克数
    calories    REAL NOT NULL                          -- 摄入热量(kcal)
);

CREATE TABLE IF NOT EXISTS exercise_records (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    record_date TEXT NOT NULL,
    exercise_name TEXT NOT NULL,
    minutes     REAL NOT NULL,                         -- 时长(分钟)
    calories    REAL NOT NULL                          -- 消耗热量(kcal)
);
"""


def get_conn() -> sqlite3.Connection:
    """获取数据库连接，启用外键并返回 Row 工厂。"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """初始化数据库：建表 + 写入种子数据（若为空）。"""
    conn = get_conn()
    try:
        conn.executescript(_SCHEMA)
        conn.commit()
        # 仅在空库时写入种子数据
        if conn.execute("SELECT COUNT(*) FROM foods").fetchone()[0] == 0:
            _seed_foods(conn)
        if conn.execute("SELECT COUNT(*) FROM exercises").fetchone()[0] == 0:
            _seed_exercises(conn)
        if conn.execute("SELECT COUNT(*) FROM user_profile").fetchone()[0] == 0:
            conn.execute(
                "INSERT INTO user_profile (gender, age, height_cm, weight_kg, activity_level, goal, target_weight, updated_at) "
                "VALUES ('male', 22, 170, 65, 'sedentary', 'normal', 60, ?)",
                (datetime.now().isoformat(),),
            )
        conn.commit()
    finally:
        conn.close()


def _seed_foods(conn: sqlite3.Connection) -> None:
    """写入常见食物库（每100g 热量/蛋白质/脂肪/碳水）。"""
    foods = [
        # 主食
        ("米饭", "主食", 116, 2.6, 0.3, 25.9),
        ("馒头", "主食", 223, 7.0, 1.1, 47.0),
        ("面条(煮)", "主食", 110, 3.9, 0.4, 22.2),
        ("全麦面包", "主食", 246, 10.0, 3.4, 41.0),
        ("燕麦片", "主食", 367, 15.0, 6.7, 61.0),
        ("红薯", "主食", 90, 1.1, 0.2, 20.7),
        # 肉蛋
        ("鸡胸肉", "肉蛋", 133, 19.4, 5.0, 2.5),
        ("鸡蛋", "肉蛋", 144, 13.3, 8.8, 2.8),
        ("瘦牛肉", "肉蛋", 106, 20.2, 2.3, 1.2),
        ("猪瘦肉", "肉蛋", 143, 20.3, 6.2, 1.5),
        ("三文鱼", "肉蛋", 139, 17.2, 7.8, 0.0),
        # 蔬果
        ("西兰花", "蔬果", 36, 4.1, 0.6, 4.3),
        ("生菜", "蔬果", 15, 1.4, 0.2, 2.0),
        ("番茄", "蔬果", 20, 0.9, 0.2, 4.0),
        ("苹果", "蔬果", 53, 0.2, 0.2, 13.7),
        ("香蕉", "蔬果", 93, 1.4, 0.2, 22.0),
        # 乳制品
        ("牛奶(全脂)", "乳制品", 65, 3.2, 3.6, 4.9),
        ("酸奶(原味)", "乳制品", 72, 2.5, 2.7, 9.3),
        # 零食饮品
        ("可乐", "饮品", 43, 0.0, 0.0, 10.6),
        ("薯片", "零食", 548, 6.0, 37.6, 49.2),
        ("坚果(混合)", "零食", 607, 20.0, 50.0, 20.0),
    ]
    conn.executemany(
        "INSERT INTO foods (name, category, calories_per_100g, protein_per_100g, fat_per_100g, carb_per_100g) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        foods,
    )


def _seed_exercises(conn: sqlite3.Connection) -> None:
    """写入常见运动库（MET 代谢当量，参考《身体活动纲要》）。"""
    exercises = [
        ("快走(6km/h)", 4.3),
        ("慢跑(8km/h)", 8.0),
        ("跑步(10km/h)", 10.0),
        ("骑自行车(休闲)", 4.0),
        ("跳绳", 12.0),
        ("游泳(自由泳)", 8.0),
        ("篮球", 6.5),
        ("羽毛球", 5.5),
        ("力量训练", 5.0),
        ("瑜伽", 2.5),
        ("爬楼梯", 8.0),
        ("HIIT高强度间歇", 11.0),
    ]
    conn.executemany("INSERT INTO exercises (name, met) VALUES (?, ?)", exercises)


# ---------------------------------------------------------------
# 用户档案 CRUD
# ---------------------------------------------------------------

def get_profile() -> dict:
    conn = get_conn()
    try:
        row = conn.execute("SELECT * FROM user_profile ORDER BY id LIMIT 1").fetchone()
        return dict(row) if row else {}
    finally:
        conn.close()


def update_profile(gender: str, age: int, height_cm: float, weight_kg: float,
                   activity_level: str, goal: str, target_weight: float) -> None:
    conn = get_conn()
    try:
        conn.execute(
            "UPDATE user_profile SET gender=?, age=?, height_cm=?, weight_kg=?, "
            "activity_level=?, goal=?, target_weight=?, updated_at=? WHERE id=1",
            (gender, age, height_cm, weight_kg, activity_level, goal, target_weight,
             datetime.now().isoformat()),
        )
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------
# 记录 CRUD
# ---------------------------------------------------------------

def add_diet_record(record_date: str, meal_type: str, food_name: str,
                    amount_g: float, calories: float) -> None:
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO diet_records (record_date, meal_type, food_name, amount_g, calories) "
            "VALUES (?, ?, ?, ?, ?)",
            (record_date, meal_type, food_name, amount_g, calories),
        )
        conn.commit()
    finally:
        conn.close()


def add_exercise_record(record_date: str, exercise_name: str,
                        minutes: float, calories: float) -> None:
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO exercise_records (record_date, exercise_name, minutes, calories) "
            "VALUES (?, ?, ?, ?)",
            (record_date, exercise_name, minutes, calories),
        )
        conn.commit()
    finally:
        conn.close()


def get_diet_records(record_date: str) -> list:
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM diet_records WHERE record_date=? ORDER BY id DESC",
            (record_date,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_exercise_records(record_date: str) -> list:
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM exercise_records WHERE record_date=? ORDER BY id DESC",
            (record_date,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def delete_diet_record(record_id: int) -> None:
    conn = get_conn()
    try:
        conn.execute("DELETE FROM diet_records WHERE id=?", (record_id,))
        conn.commit()
    finally:
        conn.close()


def delete_exercise_record(record_id: int) -> None:
    conn = get_conn()
    try:
        conn.execute("DELETE FROM exercise_records WHERE id=?", (record_id,))
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------
# 食物 / 运动库查询
# ---------------------------------------------------------------

def search_foods(keyword: str = "") -> list:
    conn = get_conn()
    try:
        if keyword:
            rows = conn.execute(
                "SELECT * FROM foods WHERE name LIKE ? ORDER BY category, name",
                (f"%{keyword}%",),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM foods ORDER BY category, name").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def search_exercises(keyword: str = "") -> list:
    conn = get_conn()
    try:
        if keyword:
            rows = conn.execute(
                "SELECT * FROM exercises WHERE name LIKE ? ORDER BY name",
                (f"%{keyword}%",),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM exercises ORDER BY name").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_food_by_id(food_id: int) -> Optional[dict]:
    conn = get_conn()
    try:
        row = conn.execute("SELECT * FROM foods WHERE id=?", (food_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_exercise_by_id(exercise_id: int) -> Optional[dict]:
    conn = get_conn()
    try:
        row = conn.execute("SELECT * FROM exercises WHERE id=?", (exercise_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


# ---------------------------------------------------------------
# 统计
# ---------------------------------------------------------------

def sum_diet_calories(record_date: str) -> float:
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT COALESCE(SUM(calories), 0) AS s FROM diet_records WHERE record_date=?",
            (record_date,),
        ).fetchone()
        return row["s"]
    finally:
        conn.close()


def sum_exercise_calories(record_date: str) -> float:
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT COALESCE(SUM(calories), 0) AS s FROM exercise_records WHERE record_date=?",
            (record_date,),
        ).fetchone()
        return row["s"]
    finally:
        conn.close()


def recent_days_summary(days: int = 7) -> list:
    """返回最近 N 天的摄入/消耗汇总，供图表展示。"""
    conn = get_conn()
    try:
        result = []
        today = date.today()
        for i in range(days - 1, -1, -1):
            d = today.fromordinal(today.toordinal() - i).isoformat()
            intake = conn.execute(
                "SELECT COALESCE(SUM(calories),0) FROM diet_records WHERE record_date=?", (d,)
            ).fetchone()[0]
            burned = conn.execute(
                "SELECT COALESCE(SUM(calories),0) FROM exercise_records WHERE record_date=?", (d,)
            ).fetchone()[0]
            result.append({"date": d, "intake": round(intake, 1), "burned": round(burned, 1)})
        return result
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    print("数据库初始化完成，路径：", DB_PATH)
