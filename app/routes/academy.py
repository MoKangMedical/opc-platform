"""
OPC Platform - Academy API
课程、学习路径、导师匹配、认证
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from app.database import get_db
from app.models import Course, Lesson, Enrollment, Mentor, MentorMatch, Certification, User

router = APIRouter(prefix="/api/academy", tags=["Academy"])

# ========== 课程 ==========
@router.get("/courses")
def list_courses(
    category: Optional[str] = None,
    level: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Course).filter(Course.is_published == True)
    if category:
        query = query.filter(Course.category == category)
    if level:
        query = query.filter(Course.level == level)
    if search:
        query = query.filter(Course.title.contains(search) | Course.description.contains(search))
    
    total = query.count()
    courses = query.order_by(Course.student_count.desc()).offset((page-1)*limit).limit(limit).all()
    
    return {
        "total": total,
        "page": page,
        "courses": [{
            "id": c.id,
            "title": c.title,
            "title_en": c.title_en,
            "description": c.description,
            "description_en": c.description_en,
            "cover_emoji": c.cover_emoji,
            "cover_gradient": c.cover_gradient,
            "instructor_name": c.instructor_name,
            "category": c.category,
            "level": c.level,
            "duration_hours": c.duration_hours,
            "lesson_count": c.lesson_count,
            "price": c.price,
            "tags": c.tags or [],
            "rating": c.rating,
            "student_count": c.student_count,
        } for c in courses]
    }

@router.get("/courses/{course_id}")
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(404, "Course not found")
    lessons = db.query(Lesson).filter(Lesson.course_id == course_id).order_by(Lesson.order).all()
    return {
        "id": course.id,
        "title": course.title,
        "title_en": course.title_en,
        "description": course.description,
        "description_en": course.description_en,
        "cover_emoji": course.cover_emoji,
        "instructor_name": course.instructor_name,
        "category": course.category,
        "level": course.level,
        "duration_hours": course.duration_hours,
        "price": course.price,
        "tags": course.tags or [],
        "lessons": [{
            "id": l.id,
            "title": l.title,
            "title_en": l.title_en,
            "duration_minutes": l.duration_minutes,
            "order": l.order,
            "is_free": l.is_free,
        } for l in lessons]
    }

@router.post("/courses/{course_id}/enroll")
def enroll_course(course_id: int, user_id: int = 1, db: Session = Depends(get_db)):
    existing = db.query(Enrollment).filter(
        Enrollment.user_id == user_id, Enrollment.course_id == course_id
    ).first()
    if existing:
        return {"message": "Already enrolled", "enrollment_id": existing.id}
    
    enrollment = Enrollment(user_id=user_id, course_id=course_id)
    db.add(enrollment)
    
    course = db.query(Course).filter(Course.id == course_id).first()
    if course:
        course.student_count += 1
    
    db.commit()
    db.refresh(enrollment)
    return {"message": "Enrolled successfully", "enrollment_id": enrollment.id}

@router.get("/enrollments")
def get_enrollments(user_id: int = 1, db: Session = Depends(get_db)):
    enrollments = db.query(Enrollment).filter(Enrollment.user_id == user_id).all()
    result = []
    for e in enrollments:
        course = db.query(Course).filter(Course.id == e.course_id).first()
        result.append({
            "enrollment_id": e.id,
            "course_id": e.course_id,
            "course_title": course.title if course else "Unknown",
            "progress": e.progress,
            "completed_lessons": e.completed_lessons or [],
            "started_at": e.started_at.isoformat(),
        })
    return {"enrollments": result}

@router.put("/enrollments/{enrollment_id}/progress")
def update_progress(enrollment_id: int, lesson_id: int, db: Session = Depends(get_db)):
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(404, "Enrollment not found")
    
    completed = list(set((enrollment.completed_lessons or []) + [lesson_id]))
    enrollment.completed_lessons = completed
    
    course = db.query(Course).filter(Course.id == enrollment.course_id).first()
    if course and course.lesson_count:
        enrollment.progress = round(len(completed) / course.lesson_count * 100, 1)
    
    if enrollment.progress >= 100:
        enrollment.completed_at = func.now()
    
    db.commit()
    return {"progress": enrollment.progress, "completed_lessons": completed}


# ========== 导师 ==========
@router.get("/mentors")
def list_mentors(
    skill: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Mentor).filter(Mentor.is_available == True)
    if skill:
        query = query.filter(Mentor.skills.contains([skill]))
    mentors = query.order_by(Mentor.rating.desc()).all()
    return {"mentors": [{
        "id": m.id,
        "name": m.name,
        "name_en": m.name_en,
        "title": m.title,
        "title_en": m.title_en,
        "avatar_emoji": m.avatar_emoji,
        "bio": m.bio,
        "bio_en": m.bio_en,
        "skills": m.skills or [],
        "experience_years": m.experience_years,
        "rating": m.rating,
        "total_sessions": m.total_sessions,
    } for m in mentors]}

@router.post("/mentors/{mentor_id}/match")
def request_mentor_match(mentor_id: int, user_id: int = 1, message: str = "", db: Session = Depends(get_db)):
    match = MentorMatch(user_id=user_id, mentor_id=mentor_id, message=message)
    db.add(match)
    db.commit()
    db.refresh(match)
    return {"message": "Match request sent", "match_id": match.id, "status": match.status}


# ========== 认证 ==========
@router.get("/certifications")
def list_certifications(db: Session = Depends(get_db)):
    certs = db.query(Certification).filter(Certification.is_active == True).all()
    return {"certifications": [{
        "id": c.id,
        "name": c.name,
        "name_en": c.name_en,
        "description": c.description,
        "description_en": c.description_en,
        "icon_emoji": c.icon_emoji,
        "icon_color": c.icon_color,
        "category": c.category,
        "modules_required": c.modules_required,
    } for c in certs]}


# ========== 初始化示例数据 ==========
@router.post("/seed")
def seed_academy_data(db: Session = Depends(get_db)):
    """初始化学院示例数据"""
    if db.query(Course).count() > 0:
        return {"message": "Data already exists"}
    
    courses_data = [
        {"title": "从0到1：独立创业者启动指南", "title_en": "From 0 to 1: OPC Startup Guide", "description": "从想法验证到第一个客户，完整覆盖独立创业的关键步骤", "description_en": "From idea validation to first customer", "cover_emoji": "🚀", "cover_gradient": "linear-gradient(135deg,#6366f1,#8b5cf6)", "instructor_name": "张明远", "category": "startup", "level": "beginner", "duration_hours": 6, "lesson_count": 12, "price": 0, "tags": ["创业基础", "商业模式"], "student_count": 2847},
        {"title": "AI Agent驱动的超级个体", "title_en": "AI Agent-Powered Super Individual", "description": "用AI Agent放大你的能力边界，一个人就是一支团队", "description_en": "Amplify your capabilities with AI agents", "cover_emoji": "🤖", "cover_gradient": "linear-gradient(135deg,#06b6d4,#22c55e)", "instructor_name": "王浩然", "category": "ai", "level": "intermediate", "duration_hours": 8, "lesson_count": 16, "price": 299, "tags": ["AI Agent", "自动化"], "student_count": 1523},
        {"title": "独立创业者财务与税务实操", "title_en": "OPC Finance & Tax Practice", "description": "个体工商户/一人公司财税管理，合理节税", "description_en": "Sole proprietorship finance and tax optimization", "cover_emoji": "💰", "cover_gradient": "linear-gradient(135deg,#f59e0b,#ef4444)", "instructor_name": "李思琪", "category": "finance", "level": "intermediate", "duration_hours": 5, "lesson_count": 10, "price": 199, "tags": ["财务", "税务"], "student_count": 986},
        {"title": "个人品牌打造与内容营销", "title_en": "Personal Branding & Content Marketing", "description": "建立你的个人IP，用内容获客，用信任成交", "description_en": "Build your personal brand and attract customers", "cover_emoji": "🎨", "cover_gradient": "linear-gradient(135deg,#ec4899,#8b5cf6)", "instructor_name": "陈思远", "category": "marketing", "level": "beginner", "duration_hours": 7, "lesson_count": 14, "price": 249, "tags": ["品牌", "营销"], "student_count": 2105},
        {"title": "数据驱动的商业决策", "title_en": "Data-Driven Business Decisions", "description": "用数据代替直觉，做出更聪明的商业决策", "description_en": "Replace intuition with data", "cover_emoji": "📊", "cover_gradient": "linear-gradient(135deg,#22c55e,#06b6d4)", "instructor_name": "赵一鸣", "category": "data", "level": "intermediate", "duration_hours": 4, "lesson_count": 8, "price": 199, "tags": ["数据分析", "决策"], "student_count": 1342},
        {"title": "独立创业者法律风险防范", "title_en": "Legal Risk Prevention for OPCs", "description": "合同、知识产权、劳动法——独立创业者必修法律课", "description_en": "Essential legal knowledge for OPCs", "cover_emoji": "⚖️", "cover_gradient": "linear-gradient(135deg,#a855f7,#6366f1)", "instructor_name": "刘芳", "category": "legal", "level": "all", "duration_hours": 5, "lesson_count": 10, "price": 349, "tags": ["法律", "合规"], "student_count": 756},
    ]
    
    for cd in courses_data:
        course = Course(**cd)
        db.add(course)
    
    mentors_data = [
        {"name": "张明远", "name_en": "Zhang Mingyuan", "title": "10年独立开发者", "title_en": "10yr Independent Developer", "avatar_emoji": "🎯", "bio": "从大厂离职后独立创业，服务过200+企业客户", "bio_en": "Left big tech, served 200+ enterprise clients", "skills": ["SaaS", "技术架构", "客户开发"], "experience_years": 10, "rating": 4.9, "total_sessions": 156},
        {"name": "李思琪", "name_en": "Li Siqi", "title": "5年自由咨询师", "title_en": "5yr Freelance Consultant", "avatar_emoji": "💡", "bio": "管理咨询背景，帮助50+人成功转型为OPC", "bio_en": "Helped 50+ become OPCs", "skills": ["咨询", "品牌", "定价"], "experience_years": 5, "rating": 4.8, "total_sessions": 89},
        {"name": "王浩然", "name_en": "Wang Haoran", "title": "AI创业者 · 8年经验", "title_en": "AI Entrepreneur · 8yr", "avatar_emoji": "🚀", "bio": "专注AI应用开发，打造过3个百万级产品", "bio_en": "Built 3 products with 1M+ revenue", "skills": ["AI", "产品", "增长"], "experience_years": 8, "rating": 4.9, "total_sessions": 203},
    ]
    
    for md in mentors_data:
        mentor = Mentor(**md)
        db.add(mentor)
    
    certs_data = [
        {"name": "OPC创业者认证", "name_en": "OPC Entrepreneur Certification", "description": "独立创业核心能力全面认证", "description_en": "Comprehensive OPC certification", "icon_emoji": "🏆", "icon_color": "#6366f1", "category": "comprehensive", "modules_required": 4},
        {"name": "AI Agent工程师认证", "name_en": "AI Agent Engineer Certification", "description": "AI Agent开发与应用能力认证", "description_en": "AI agent development certification", "icon_emoji": "🤖", "icon_color": "#06b6d4", "category": "technical", "modules_required": 3},
        {"name": "数据分析师认证", "name_en": "Data Analyst Certification", "description": "商业数据分析能力认证", "description_en": "Business data analysis certification", "icon_emoji": "📊", "icon_color": "#22c55e", "category": "specialized", "modules_required": 2},
        {"name": "独立咨询师认证", "name_en": "Independent Consultant Certification", "description": "独立咨询服务能力认证", "description_en": "Independent consulting certification", "icon_emoji": "💰", "icon_color": "#f59e0b", "category": "professional", "modules_required": 3},
    ]
    
    for cd in certs_data:
        cert = Certification(**cd)
        db.add(cert)
    
    db.commit()
    return {"message": "Academy data seeded", "courses": len(courses_data), "mentors": len(mentors_data), "certs": len(certs_data)}
