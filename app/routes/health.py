"""
OPC Health - 完整健康管理系统
参考 Keep 模式: 活动/打卡/排行榜/成就/挑战
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, text
from typing import Optional, List
from datetime import datetime, timedelta, date
import json
import calendar

from app.database import get_db
from app.models import HealthRecord, HealthGoal, HealthInsight, User

router = APIRouter(prefix="/api/health", tags=["Health"])

# ========== 活动类型定义 ==========
ACTIVITY_TYPES = {
    "running": {"name": "跑步", "emoji": "🏃", "cal_per_min": 10, "unit": "km"},
    "walking": {"name": "健走", "emoji": "🚶", "cal_per_min": 5, "unit": "km"},
    "cycling": {"name": "骑行", "emoji": "🚴", "cal_per_min": 8, "unit": "km"},
    "swimming": {"name": "游泳", "emoji": "🏊", "cal_per_min": 11, "unit": "min"},
    "gym": {"name": "健身", "emoji": "💪", "cal_per_min": 7, "unit": "min"},
    "yoga": {"name": "瑜伽", "emoji": "🧘", "cal_per_min": 4, "unit": "min"},
    "hiit": {"name": "HIIT", "emoji": "⚡", "cal_per_min": 13, "unit": "min"},
    "basketball": {"name": "篮球", "emoji": "🏀", "cal_per_min": 9, "unit": "min"},
    "football": {"name": "足球", "emoji": "⚽", "cal_per_min": 10, "unit": "min"},
    "badminton": {"name": "羽毛球", "emoji": "🏸", "cal_per_min": 7, "unit": "min"},
    "tennis": {"name": "网球", "emoji": "🎾", "cal_per_min": 8, "unit": "min"},
    "climbing": {"name": "攀岩", "emoji": "🧗", "cal_per_min": 9, "unit": "min"},
    "skating": {"name": "滑冰", "emoji": "⛸️", "cal_per_min": 7, "unit": "min"},
    "dance": {"name": "舞蹈", "emoji": "💃", "cal_per_min": 6, "unit": "min"},
    "boxing": {"name": "拳击", "emoji": "🥊", "cal_per_min": 12, "unit": "min"},
    "rowing": {"name": "划船", "emoji": "🚣", "cal_per_min": 8, "unit": "min"},
    "skiing": {"name": "滑雪", "emoji": "⛷️", "cal_per_min": 9, "unit": "min"},
    "hiking": {"name": "徒步", "emoji": "🥾", "cal_per_min": 6, "unit": "km"},
    "stretching": {"name": "拉伸", "emoji": "🤸", "cal_per_min": 3, "unit": "min"},
    "meditation": {"name": "冥想", "emoji": "🧠", "cal_per_min": 1, "unit": "min"},
}

# ========== 每日打卡 ==========
@router.post("/checkin")
def daily_checkin(
    user_id: int = 1,
    mood: int = Query(..., ge=1, le=10, description="心情 1-10"),
    energy: int = Query(..., ge=1, le=10, description="精力 1-10"),
    stress: int = Query(..., ge=1, le=10, description="压力 1-10"),
    sleep_hours: float = Query(0, ge=0, le=24),
    sleep_quality: int = Query(5, ge=1, le=10, description="睡眠质量"),
    water_ml: int = Query(0, ge=0, description="饮水量ml"),
    steps: int = Query(0, ge=0, description="步数"),
    weight_kg: float = Query(0, ge=0),
    work_hours: float = Query(0, ge=0, le=24),
    notes: str = "",
    tags: str = "",
    db: Session = Depends(get_db)
):
    """每日健康打卡 - Keep风格全面记录"""
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    
    record = HealthRecord(
        user_id=user_id,
        record_type="daily_checkin",
        mood_score=mood,
        energy_level=energy,
        stress_level=stress,
        sleep_hours=sleep_hours,
        notes=notes,
        tags=tag_list,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    
    # 计算连续打卡天数
    streak = calc_streak(db, user_id)
    
    # 自动生成洞察
    insights = generate_insights(db, user_id, mood, stress, sleep_hours, water_ml, steps)
    
    # 计算今日得分
    daily_score = calc_daily_score(mood, energy, stress, sleep_hours, sleep_quality, water_ml, steps)
    
    return {
        "record_id": record.id,
        "date": record.date.isoformat(),
        "streak": streak,
        "daily_score": daily_score,
        "insights": insights,
        "message": f"打卡成功！已连续打卡{streak}天 🔥",
    }

# ========== 运动记录 ==========
@router.post("/activity")
def log_activity(
    user_id: int = 1,
    activity_type: str = "running",
    duration_min: int = Query(..., ge=1),
    distance_km: float = Query(0, ge=0),
    calories: int = Query(0, ge=0),
    intensity: str = "moderate",
    heart_rate_avg: int = Query(0, ge=0),
    notes: str = "",
    db: Session = Depends(get_db)
):
    """记录运动活动"""
    if activity_type not in ACTIVITY_TYPES:
        raise HTTPException(400, f"Unknown activity type: {activity_type}")
    
    act = ACTIVITY_TYPES[activity_type]
    if calories == 0:
        calories = int(duration_min * act["cal_per_min"])
    
    record = HealthRecord(
        user_id=user_id,
        record_type="exercise",
        exercise_type=activity_type,
        exercise_duration=duration_min,
        exercise_intensity=intensity,
        notes=json.dumps({
            "distance_km": distance_km,
            "calories": calories,
            "heart_rate_avg": heart_rate_avg,
            "activity_name": act["name"],
        }),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    
    return {
        "record_id": record.id,
        "activity": act["name"],
        "emoji": act["emoji"],
        "duration": duration_min,
        "calories": calories,
        "message": f"{act['emoji']} {act['name']} {duration_min}分钟，消耗{calories}卡路里",
    }

# ========== 健康仪表盘 ==========
@router.get("/dashboard")
def health_dashboard(user_id: int = 1, db: Session = Depends(get_db)):
    """Keep风格健康仪表盘"""
    now = datetime.utcnow()
    today = now.date()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # 今日数据
    today_records = db.query(HealthRecord).filter(
        HealthRecord.user_id == user_id,
        HealthRecord.record_type == "daily_checkin",
        func.date(HealthRecord.date) == today,
    ).all()
    
    today_checkin = today_records[-1] if today_records else None
    
    # 本周运动
    week_exercises = db.query(HealthRecord).filter(
        HealthRecord.user_id == user_id,
        HealthRecord.record_type == "exercise",
        HealthRecord.date >= week_ago,
    ).all()
    
    # 本月运动
    month_exercises = db.query(HealthRecord).filter(
        HealthRecord.user_id == user_id,
        HealthRecord.record_type == "exercise",
        HealthRecord.date >= month_ago,
    ).all()
    
    # 近7天打卡
    week_checkins = db.query(HealthRecord).filter(
        HealthRecord.user_id == user_id,
        HealthRecord.record_type == "daily_checkin",
        HealthRecord.date >= week_ago,
    ).all()
    
    # 统计
    total_exercise_min = sum(r.exercise_duration for r in month_exercises if r.exercise_duration)
    total_calories = 0
    for r in month_exercises:
        if r.notes:
            try:
                info = json.loads(r.notes)
                total_calories += info.get("calories", 0)
            except:
                pass
    
    exercise_days = len(set(r.date.date() for r in month_exercises))
    streak = calc_streak(db, user_id)
    
    avg_mood = sum(r.mood_score for r in week_checkins if r.mood_score) / max(len(week_checkins), 1)
    avg_stress = sum(r.stress_level for r in week_checkins if r.stress_level) / max(len(week_checkins), 1)
    avg_sleep = sum(r.sleep_hours for r in week_checkins if r.sleep_hours) / max(len(week_checkins), 1)
    
    # 健康评分
    health_score = min(100, max(0, int(
        (avg_mood / 10) * 20 +
        ((10 - avg_stress) / 10) * 20 +
        min(avg_sleep / 8, 1) * 20 +
        min(total_exercise_min / 600, 1) * 20 +
        min(streak / 7, 1) * 20
    )))
    
    # 今日得分
    daily_score = 0
    if today_checkin:
        daily_score = calc_daily_score(
            today_checkin.mood_score or 5,
            today_checkin.energy_level or 5,
            today_checkin.stress_level or 5,
            today_checkin.sleep_hours or 7,
            5, 0, 0
        )
    
    # 最近洞察
    insights = db.query(HealthInsight).filter(
        HealthInsight.user_id == user_id,
    ).order_by(desc(HealthInsight.created_at)).limit(5).all()
    
    # 运动类型分布
    type_dist = {}
    for r in month_exercises:
        t = r.exercise_type or "other"
        type_dist[t] = type_dist.get(t, 0) + (r.exercise_duration or 0)
    
    return {
        "health_score": health_score,
        "daily_score": daily_score,
        "streak": streak,
        "today": {
            "checked_in": today_checkin is not None,
            "mood": today_checkin.mood_score if today_checkin else None,
            "energy": today_checkin.energy_level if today_checkin else None,
            "stress": today_checkin.stress_level if today_checkin else None,
            "sleep_hours": today_checkin.sleep_hours if today_checkin else None,
        },
        "weekly": {
            "avg_mood": round(avg_mood, 1),
            "avg_stress": round(avg_stress, 1),
            "avg_sleep": round(avg_sleep, 1),
            "exercise_min": sum(r.exercise_duration for r in week_exercises if r.exercise_duration),
            "checkin_days": len(week_checkins),
            "exercise_days": len(set(r.date.date() for r in week_exercises)),
        },
        "monthly": {
            "total_exercise_min": total_exercise_min,
            "total_calories": total_calories,
            "exercise_days": exercise_days,
            "exercise_goal_progress": min(100, int(total_exercise_min / 600 * 100)),
        },
        "activity_distribution": [
            {"type": t, "name": ACTIVITY_TYPES.get(t, {}).get("name", t), "emoji": ACTIVITY_TYPES.get(t, {}).get("emoji", "🏃"), "minutes": m}
            for t, m in sorted(type_dist.items(), key=lambda x: -x[1])[:6]
        ],
        "insights": [{
            "id": i.id, "type": i.insight_type, "title": i.title, "content": i.content, "date": i.created_at.isoformat(),
        } for i in insights],
    }

# ========== 排行榜 ==========
@router.get("/leaderboard")
def leaderboard(
    metric: str = Query("exercise_min", regex="^(exercise_min|streak|calories|checkin_days)$"),
    period: str = Query("week", regex="^(week|month|all)$"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """健康排行榜"""
    if period == "week":
        since = datetime.utcnow() - timedelta(days=7)
    elif period == "month":
        since = datetime.utcnow() - timedelta(days=30)
    else:
        since = datetime(2020, 1, 1)
    
    # 获取所有用户的运动数据
    results = []
    users = db.query(HealthRecord.user_id).filter(
        HealthRecord.date >= since
    ).distinct().all()
    
    for (uid,) in users:
        exercises = db.query(HealthRecord).filter(
            HealthRecord.user_id == uid,
            HealthRecord.record_type == "exercise",
            HealthRecord.date >= since,
        ).all()
        
        checkins = db.query(HealthRecord).filter(
            HealthRecord.user_id == uid,
            HealthRecord.record_type == "daily_checkin",
            HealthRecord.date >= since,
        ).all()
        
        total_min = sum(r.exercise_duration for r in exercises if r.exercise_duration)
        total_cal = 0
        for r in exercises:
            if r.notes:
                try:
                    total_cal += json.loads(r.notes).get("calories", 0)
                except:
                    pass
        
        streak = calc_streak(db, uid)
        checkin_days = len(set(r.date.date() for r in checkins))
        
        results.append({
            "user_id": uid,
            "user_name": f"OPC用户{uid}",
            "avatar_emoji": ["🔬","🏗️","🌱","🛡️","🚢","💡","📊","🎯"][uid % 8],
            "exercise_min": total_min,
            "calories": total_cal,
            "streak": streak,
            "checkin_days": checkin_days,
        })
    
    # 排序
    results.sort(key=lambda x: x.get(metric, 0), reverse=True)
    
    # 添加排名
    for i, r in enumerate(results[:limit]):
        r["rank"] = i + 1
        r["badge"] = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}"
    
    return {"leaderboard": results[:limit], "metric": metric, "period": period}

# ========== 活动类型列表 ==========
@router.get("/activities")
def list_activities():
    """获取所有运动类型"""
    return {"activities": [
        {"id": k, "name": v["name"], "emoji": v["emoji"], "cal_per_min": v["cal_per_min"], "unit": v["unit"]}
        for k, v in ACTIVITY_TYPES.items()
    ]}

# ========== 运动记录列表 ==========
@router.get("/activities/history")
def activity_history(
    user_id: int = 1,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """运动历史"""
    since = datetime.utcnow() - timedelta(days=days)
    records = db.query(HealthRecord).filter(
        HealthRecord.user_id == user_id,
        HealthRecord.record_type == "exercise",
        HealthRecord.date >= since,
    ).order_by(desc(HealthRecord.date)).all()
    
    result = []
    for r in records:
        info = {}
        if r.notes:
            try: info = json.loads(r.notes)
            except: pass
        
        act = ACTIVITY_TYPES.get(r.exercise_type, {})
        result.append({
            "id": r.id,
            "type": r.exercise_type,
            "name": act.get("name", r.exercise_type),
            "emoji": act.get("emoji", "🏃"),
            "duration": r.exercise_duration,
            "intensity": r.exercise_intensity,
            "calories": info.get("calories", 0),
            "distance": info.get("distance_km", 0),
            "date": r.date.isoformat(),
        })
    
    return {"activities": result}

# ========== 每日挑战 ==========
CHALLENGES = [
    {"id": "water", "name": "喝够8杯水", "emoji": "💧", "target": 2000, "unit": "ml", "points": 10},
    {"id": "steps", "name": "走够10000步", "emoji": "👣", "target": 10000, "unit": "步", "points": 15},
    {"id": "exercise30", "name": "运动30分钟", "emoji": "🏃", "target": 30, "unit": "分钟", "points": 20},
    {"id": "sleep8", "name": "睡够8小时", "emoji": "😴", "target": 8, "unit": "小时", "points": 15},
    {"id": "meditate", "name": "冥想10分钟", "emoji": "🧠", "target": 10, "unit": "分钟", "points": 10},
    {"id": "stretch", "name": "拉伸15分钟", "emoji": "🤸", "target": 15, "unit": "分钟", "points": 10},
    {"id": "no_stress", "name": "压力值低于5", "emoji": "😌", "target": 5, "unit": "分", "points": 15},
    {"id": "mood8", "name": "心情值高于8", "emoji": "😊", "target": 8, "unit": "分", "points": 10},
]

@router.get("/challenges")
def get_challenges(user_id: int = 1, db: Session = Depends(get_db)):
    """每日挑战"""
    today = datetime.utcnow().date()
    
    today_checkin = db.query(HealthRecord).filter(
        HealthRecord.user_id == user_id,
        HealthRecord.record_type == "daily_checkin",
        func.date(HealthRecord.date) == today,
    ).first()
    
    today_exercises = db.query(HealthRecord).filter(
        HealthRecord.user_id == user_id,
        HealthRecord.record_type == "exercise",
        func.date(HealthRecord.date) == today,
    ).all()
    
    total_exercise_min = sum(r.exercise_duration for r in today_exercises if r.exercise_duration)
    
    results = []
    for c in CHALLENGES:
        progress = 0
        completed = False
        
        if c["id"] == "water" and today_checkin:
            pass  # 需要额外记录
        elif c["id"] == "steps" and today_checkin:
            pass
        elif c["id"] == "exercise30":
            progress = total_exercise_min
            completed = total_exercise_min >= 30
        elif c["id"] == "sleep8" and today_checkin:
            progress = today_checkin.sleep_hours or 0
            completed = progress >= 8
        elif c["id"] == "no_stress" and today_checkin:
            progress = 10 - (today_checkin.stress_level or 5)
            completed = (today_checkin.stress_level or 10) <= 5
        elif c["id"] == "mood8" and today_checkin:
            progress = today_checkin.mood_score or 0
            completed = progress >= 8
        
        results.append({**c, "progress": progress, "completed": completed})
    
    completed_count = sum(1 for r in results if r["completed"])
    total_points = sum(r["points"] for r in results if r["completed"])
    
    return {"challenges": results, "completed": completed_count, "total": len(results), "points": total_points}

# ========== 成就系统 ==========
ACHIEVEMENTS = [
    {"id": "first_checkin", "name": "初次打卡", "emoji": "🌟", "desc": "完成第一次健康打卡", "condition": "checkin_count >= 1"},
    {"id": "streak3", "name": "三日坚持", "emoji": "🔥", "desc": "连续打卡3天", "condition": "streak >= 3"},
    {"id": "streak7", "name": "一周达人", "emoji": "💎", "desc": "连续打卡7天", "condition": "streak >= 7"},
    {"id": "streak30", "name": "月度冠军", "emoji": "👑", "desc": "连续打卡30天", "condition": "streak >= 30"},
    {"id": "exercise10", "name": "运动新手", "emoji": "🏃", "desc": "累计运动10次", "condition": "exercise_count >= 10"},
    {"id": "exercise50", "name": "运动达人", "emoji": "💪", "desc": "累计运动50次", "condition": "exercise_count >= 50"},
    {"id": "exercise100", "name": "健身狂人", "emoji": "🏆", "desc": "累计运动100次", "condition": "exercise_count >= 100"},
    {"id": "calories1000", "name": "千卡挑战", "emoji": "🔥", "desc": "单日消耗1000卡路里", "condition": "daily_cal >= 1000"},
    {"id": "early_bird", "name": "早起鸟儿", "emoji": "🐦", "desc": "连续7天在7点前打卡", "condition": "early_streak >= 7"},
    {"id": "all_rounder", "name": "全能选手", "emoji": "🎯", "desc": "尝试5种不同运动", "condition": "activity_types >= 5"},
    {"id": "water_master", "name": "水王", "emoji": "💧", "desc": "单日饮水2500ml+", "condition": "daily_water >= 2500"},
    {"id": "zen_master", "name": "禅修大师", "emoji": "🧘", "desc": "累计冥想500分钟", "condition": "meditation_min >= 500"},
]

@router.get("/achievements")
def get_achievements(user_id: int = 1, db: Session = Depends(get_db)):
    """成就系统"""
    # 计算用户数据
    total_checkins = db.query(HealthRecord).filter(
        HealthRecord.user_id == user_id, HealthRecord.record_type == "daily_checkin"
    ).count()
    
    total_exercises = db.query(HealthRecord).filter(
        HealthRecord.user_id == user_id, HealthRecord.record_type == "exercise"
    ).count()
    
    streak = calc_streak(db, user_id)
    
    exercise_types = db.query(HealthRecord.exercise_type).filter(
        HealthRecord.user_id == user_id, HealthRecord.record_type == "exercise"
    ).distinct().count()
    
    earned = []
    locked = []
    
    for a in ACHIEVEMENTS:
        earned_flag = False
        if "checkin_count" in a["condition"]:
            earned_flag = total_checkins >= int(a["condition"].split(">=")[1])
        elif "streak" in a["condition"]:
            earned_flag = streak >= int(a["condition"].split(">=")[1])
        elif "exercise_count" in a["condition"]:
            earned_flag = total_exercises >= int(a["condition"].split(">=")[1])
        elif "activity_types" in a["condition"]:
            earned_flag = exercise_types >= int(a["condition"].split(">=")[1])
        
        if earned_flag:
            earned.append(a)
        else:
            locked.append(a)
    
    return {"earned": earned, "locked": locked, "total_earned": len(earned), "total": len(ACHIEVEMENTS)}

# ========== 健康数据图表 ==========
@router.get("/charts")
def health_charts(
    user_id: int = 1,
    days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db)
):
    """健康数据图表"""
    since = datetime.utcnow() - timedelta(days=days)
    
    records = db.query(HealthRecord).filter(
        HealthRecord.user_id == user_id,
        HealthRecord.date >= since,
    ).order_by(HealthRecord.date).all()
    
    # 按日聚合
    daily = {}
    for r in records:
        d = r.date.date().isoformat()
        if d not in daily:
            daily[d] = {"date": d, "mood": [], "stress": [], "sleep": [], "exercise_min": 0, "calories": 0}
        
        if r.record_type == "daily_checkin":
            if r.mood_score: daily[d]["mood"].append(r.mood_score)
            if r.stress_level: daily[d]["stress"].append(r.stress_level)
            if r.sleep_hours: daily[d]["sleep"].append(r.sleep_hours)
        elif r.record_type == "exercise":
            daily[d]["exercise_min"] += r.exercise_duration or 0
            if r.notes:
                try: daily[d]["calories"] += json.loads(r.notes).get("calories", 0)
                except: pass
    
    chart_data = []
    for d in sorted(daily.keys()):
        v = daily[d]
        chart_data.append({
            "date": d,
            "mood": round(sum(v["mood"]) / len(v["mood"]), 1) if v["mood"] else None,
            "stress": round(sum(v["stress"]) / len(v["stress"]), 1) if v["stress"] else None,
            "sleep": round(sum(v["sleep"]) / len(v["sleep"]), 1) if v["sleep"] else None,
            "exercise_min": v["exercise_min"],
            "calories": v["calories"],
        })
    
    return {"charts": chart_data}

# ========== 工具函数 ==========
def calc_streak(db, user_id):
    """计算连续打卡天数"""
    today = datetime.utcnow().date()
    streak = 0
    check_date = today
    
    while True:
        record = db.query(HealthRecord).filter(
            HealthRecord.user_id == user_id,
            HealthRecord.record_type == "daily_checkin",
            func.date(HealthRecord.date) == check_date,
        ).first()
        
        if record:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            if check_date == today:
                check_date -= timedelta(days=1)
                continue
            break
    
    return streak

def calc_daily_score(mood, energy, stress, sleep_hours, sleep_quality, water_ml, steps):
    """计算每日健康得分"""
    score = 0
    score += (mood / 10) * 25
    score += (energy / 10) * 15
    score += ((10 - stress) / 10) * 20
    score += min(sleep_hours / 8, 1) * 20
    score += min(steps / 10000, 1) * 10
    score += min(water_ml / 2000, 1) * 10
    return min(100, int(score))

def generate_insights(db, user_id, mood, stress, sleep_hours, water_ml, steps):
    """生成健康洞察"""
    insights = []
    if stress >= 8:
        insights.append({"type": "warning", "title": "⚠️ 压力指数偏高", "content": f"当前压力{stress}/10，建议做10分钟冥想或散步放松"})
    if sleep_hours < 6:
        insights.append({"type": "warning", "title": "😴 睡眠不足", "content": f"只睡了{sleep_hours}小时，长期不足会影响创造力"})
    if mood >= 8:
        insights.append({"type": "encouragement", "title": "🌟 状态极佳！", "content": "心情很棒！这是处理高难度任务的最佳时机"})
    if steps >= 10000:
        insights.append({"type": "encouragement", "title": "👣 万步达成！", "content": f"今日{steps}步，超额完成目标！"})
    return insights
