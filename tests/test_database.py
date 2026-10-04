"""
database.py 单元测试

使用临时数据库验证建表、种子数据与 CRUD 逻辑。
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

import database as db


@pytest.fixture()
def tmp_db(tmp_path, monkeypatch):
    """将数据库路径重定向到临时文件，测试后不影响真实数据。"""
    test_db = tmp_path / "test_fitness.db"
    monkeypatch.setattr(db, "DB_PATH", str(test_db))
    db.init_db()
    yield db
    if test_db.exists():
        test_db.unlink()


def test_seed_data(tmp_db):
    """种子数据应正确写入。"""
    foods = tmp_db.search_foods()
    exercises = tmp_db.search_exercises()
    assert len(foods) >= 20
    assert len(exercises) >= 10


def test_default_profile(tmp_db):
    """默认档案应存在。"""
    p = tmp_db.get_profile()
    assert p["gender"] in ("male", "female")
    assert p["age"] > 0


def test_update_profile(tmp_db):
    """更新档案后应能读回新值。"""
    tmp_db.update_profile("female", 25, 160, 55, "moderate", "normal", 50)
    p = tmp_db.get_profile()
    assert p["gender"] == "female"
    assert p["height_cm"] == 160
    assert p["activity_level"] == "moderate"


def test_add_and_get_diet(tmp_db):
    """饮食记录增删查。"""
    tmp_db.add_diet_record("2026-01-01", "lunch", "米饭", 200, 232)
    records = tmp_db.get_diet_records("2026-01-01")
    assert len(records) == 1
    assert records[0]["food_name"] == "米饭"
    assert records[0]["calories"] == 232

    rid = records[0]["id"]
    tmp_db.delete_diet_record(rid)
    assert len(tmp_db.get_diet_records("2026-01-01")) == 0


def test_add_and_get_exercise(tmp_db):
    """运动记录增删查。"""
    tmp_db.add_exercise_record("2026-01-01", "慢跑", 30, 280)
    records = tmp_db.get_exercise_records("2026-01-01")
    assert len(records) == 1
    assert records[0]["exercise_name"] == "慢跑"

    rid = records[0]["id"]
    tmp_db.delete_exercise_record(rid)
    assert len(tmp_db.get_exercise_records("2026-01-01")) == 0


def test_sum_calories(tmp_db):
    """热量汇总应正确。"""
    tmp_db.add_diet_record("2026-01-02", "breakfast", "鸡蛋", 50, 72)
    tmp_db.add_diet_record("2026-01-02", "lunch", "米饭", 200, 232)
    assert tmp_db.sum_diet_calories("2026-01-02") == pytest.approx(304.0)


def test_search_foods(tmp_db):
    """食物搜索过滤。"""
    results = tmp_db.search_foods("鸡")
    names = [f["name"] for f in results]
    assert any("鸡" in n for n in names)


def test_recent_days_summary(tmp_db):
    """近 N 日汇总应返回 N 条。"""
    summary = tmp_db.recent_days_summary(7)
    assert len(summary) == 7
    assert "date" in summary[0]
    assert "intake" in summary[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
