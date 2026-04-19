"""
OPC Platform - Health API
健康追踪、压力管理、AI健康洞察
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional, List
from datetime import datetime, timedelta
from app.database import get_db
from app.models import HealthRecord, HealthGoal, HealthInsight, User

router = APIRouter(prefix="/api/health", tags=["Health"])

# ========== 日常签到 ==========
@router.post("/checkin")
def daily_checkin(
    user_id: int = 1,
    mood_score: int = Query(..., ge=1, le=10),
    energy_level: int = Query(..., ge=1, le=10),
    stress_level: int = Query(..., ge=1, le=10),
    work_hours: float = Query(0, ge=0, le=24),
    sleep_hours: float = Query(0, ge=0, le=24),
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """每日健康签到"""
    record = HealthRecord(
        user_id=user_id,
        record_type="daily_checkin",
        mood_score=mood_score,
        energy_level=energy_level,
        stress_level=stress_level,
        work_hours=work_hours,
        sleep_hours=sleep_hours,
        notes=notes,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    
    # 生成AI洞察
    insights = []
    if stress_level >= 8:
        insight = HealthInsight(
            user_id=user_id,
            insight_type="warning",
            title="⚠️ 压力指数偏高",
            content=f"当前压力指数为 {stress_level}/10，建议今天安排30分钟放松时间。可以试试深呼吸或短暂散步。"
        )
        db.add(insight)
        insights.append("stress_warning")
    
    if sleep_hours < 6:
        insight = HealthInsight(
            user_id=user_id,
            insight_type="recommendation",
            title="😴 睡眠不足提醒",
            content=f"昨晚只睡了 {sleep_hours} 小时。长期睡眠不足会影响创造力和决策能力，建议今晚提前休息。"
        )
        db.add(insight)
        insights.append("sleep_warning")
    
    if work_hours > 12:
        insight = HealthInsight(
            user_id=user_id,
            insight_type="warning",
            title="⏰ 工作时长过长",
            content=f"今日工作 {work_hours} 小时。OPC也需要休息，持续高强度工作可能导致倦怠。"
        )
        db.add(insight)
        insights.append("overwork_warning")
    
    if mood_score >= 8 and energy_level >= 8:
        insight = HealthInsight(
            user_id=user_id,
            insight_type="encouragement",
            title="🌟 状态绝佳！",
            content="今天状态很好！这是处理高难度任务的最佳时机。"
        )
        db.add(insight)
        insights.append("great_state")
    
    db.commit()
    
    return {
        "record_id": record.id,
        "date": record.date.isoformat(),
        "insights": insights,
        "message": "签到成功"
    }

# ========== 运动记录 ==========
@router.post("/exercise")
def log_exercise(
    user_id: int = 1,
    exercise_type: str = "other",
    duration: int = Query(..., ge=1),
    intensity: str = "moderate",
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """记录运动"""
    record = HealthRecord(
        user_id=user_id,
        record_type="exercise",
        exercise_type=exercise_type,
        exercise_duration=duration,
        exercise_intensity=intensity,
        notes=notes,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"record_id": record.id, "message": f"已记录{exercise_type}运动 {duration} 分钟"}


# ========== 健康仪表盘 ==========
@router.get("/dashboard")
def health_dashboard(user_id: int = 1, db: Session = Depends(get_db)):
    """健康仪表盘数据"""
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # 最近一次签到
    latest = db.query(HealthRecord).filter(
        HealthRecord.user_id == user_id,
        HealthRecord.record_type == "daily_checkin"
    ).order_by(desc(HealthRecord.date)).first()
    
    # 近7天数据
    week_records = db.query(HealthRecord).filter(
        HealthRecord.user_id == user_id,
        HealthRecord.record_type == "daily_checkin",
        HealthRecord.date >= week_ago
    ).all()
    
    # 近30天运动
    month_exercises = db.query(HealthRecord).filter(
        HealthRecord.user_id == user_id,
        HealthRecord.record_type == "exercise",
        HealthRecord.date >= month_ago
    ).all()
    
    # 统计
    avg_mood = sum(r.mood_score for r in week_records if r.mood_score) / max(len(week_records), 1)
    avg_stress = sum(r.stress_level for r in week_records if r.stress_level) / max(len(week_records), 1)
    avg_sleep = sum(r.sleep_hours for r in week_records if r.sleep_hours) / max(len(week_records), 1)
    avg_work = sum(r.work_hours for r in week_records if r.work_hours) / max(len(week_records), 1)
    total_exercise_min = sum(r.exercise_duration for r in month_exercises if r.exercise_duration)
    checkin_streak = len(week_records)
    
    # 未读洞察
    unread_insights = db.query(HealthInsight).filter(
        HealthInsight.user_id == user_id,
        HealthInsight.is_read == False
    ).order_by(desc(HealthInsight.created_at)).limit(5).all()
    
    # 健康评分 (0-100)
    health_score = min(100, max(0,
        int(
            (avg_mood / 10) * 25 +
            ((10 - avg_stress) / 10) * 25 +
            min(avg_sleep / 8, 1) * 25 +
            min(total_exercise_min / 150, 1) * 25
        )
    ))
    
    return {
        "health_score": health_score,
        "latest_checkin": {
            "date": latest.date.isoformat() if latest else None,
            "mood": latest.mood_score if latest else None,
            "energy": latest.energy_level if latest else None,
            "stress": latest.stress_level if latest else None,
        } if latest else None,
        "weekly_stats": {
            "avg_mood": round(avg_mood, 1),
            "avg_stress": round(avg_stress, 1),
            "avg_sleep_hours": round(avg_sleep, 1),
            "avg_work_hours": round(avg_work, 1),
            "checkin_days": checkin_streak,
        },
        "monthly_stats": {
            "total_exercise_minutes": total_exercise_min,
            "exercise_sessions": len(month_exercises),
            "exercise_goal_progress": min(100, int(total_exercise_min / 600 * 100)),
        },
        "insights": [{
            "id": i.id,
            "type": i.insight_type,
            "title": i.title,
            "content": i.content,
            "date": i.created_at.isoformat(),
        } for i in unread_insights]
    }

# ========== 历史记录 ==========
@router.get("/records")
def get_records(
    user_id: int = 1,
    record_type: Optional[str] = None,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """获取健康记录"""
    since = datetime.utcnow() - timedelta(days=days)
    query = db.query(HealthRecord).filter(
        HealthRecord.user_id == user_id,
        HealthRecord.date >= since
    )
    if record_type:
        query = query.filter(HealthRecord.record_type == record_type)
    
    records = query.order_by(desc(HealthRecord.date)).all()
    return {"records": [{
        "id": r.id,
        "type": r.record_type,
        "date": r.date.isoformat(),
        "mood": r.mood_score,
        "energy": r.energy_level,
        "stress": r.stress_level,
        "work_hours": r.work_hours,
        "sleep_hours": r.sleep_hours,
        "exercise_type": r.exercise_type,
        "exercise_duration": r.exercise_duration,
        "notes": r.notes,
    } for r in records]}

# ========== 健康目标 ==========
@router.post("/goals")
def set_goal(
    user_id: int = 1,
    goal_type: str = "sleep",
    target_value: float = 8,
    unit: str = "hours",
    db: Session = Depends(get_db)
):
    """设置健康目标"""
    # 停用同类型旧目标
    db.query(HealthGoal).filter(
        HealthGoal.user_id == user_id,
        HealthGoal.goal_type == goal_type,
        HealthGoal.is_active == True
    ).update({"is_active": False})
    
    goal = HealthGoal(
        user_id=user_id,
        goal_type=goal_type,
        target_value=target_value,
        unit=unit,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return {"goal_id": goal.id, "message": f"已设置{goal_type}目标: {target_value} {unit}"}

@router.get("/goals")
def get_goals(user_id: int = 1, db: Session = Depends(get_db)):
    goals = db.query(HealthGoal).filter(
        HealthGoal.user_id == user_id,
        HealthGoal.is_active == True
    ).all()
    return {"goals": [{
        "id": g.id,
        "type": g.goal_type,
        "target": g.target_value,
        "current": g.current_value,
        "unit": g.unit,
        "progress": round(g.current_value / g.target_value * 100, 1) if g.target_value > 0 else 0,
    } for g in goals]}

# ========== 洞察 ==========
@router.get("/insights")
def get_insights(user_id: int = 1, limit: int = 20, db: Session = Depends(get_db)):
    insights = db.query(HealthInsight).filter(
        HealthInsight.user_id == user_id
    ).order_by(desc(HealthInsight.created_at)).limit(limit).all()
    return {"insights": [{
        "id": i.id,
        "type": i.insight_type,
        "title": i.title,
        "content": i.content,
        "is_read": i.is_read,
        "date": i.created_at.isoformat(),
    } for i in insights]}

@router.put("/insights/{insight_id}/read")
def mark_insight_read(insight_id: int, db: Session = Depends(get_db)):
    insight = db.query(HealthInsight).filter(HealthInsight.id == insight_id).first()
    if not insight:
        raise HTTPException(404, "Insight not found")
    insight.is_read = True
    db.commit()
    return {"message": "Marked as read"}
