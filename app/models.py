"""
OPC Platform - 数据库模型
"""
import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum

# ========== 用户系统 ==========
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    display_name = Column(String(100))
    avatar_url = Column(String(500))
    bio = Column(Text)
    role = Column(String(20), default="user")  # user, mentor, admin
    skills = Column(JSON, default=list)  # ["AI", "SaaS", "Consulting"]
    location = Column(String(100))
    website = Column(String(500))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    enrollments = relationship("Enrollment", back_populates="user")
    health_records = relationship("HealthRecord", back_populates="user")
    messages_sent = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    messages_received = relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver")
    agent_profiles = relationship("AgentProfile", back_populates="user")


# ========== OPC学院 ==========
class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    title_en = Column(String(200))
    description = Column(Text)
    description_en = Column(Text)
    cover_emoji = Column(String(10), default="📖")
    cover_gradient = Column(String(100), default="linear-gradient(135deg,#6366f1,#8b5cf6)")
    instructor_name = Column(String(100))
    category = Column(String(50))  # startup, ai, finance, marketing, legal, data
    level = Column(String(20))  # beginner, intermediate, advanced
    duration_hours = Column(Float)
    lesson_count = Column(Integer)
    price = Column(Float, default=0)
    currency = Column(String(10), default="CNY")
    tags = Column(JSON, default=list)
    rating = Column(Float, default=0)
    student_count = Column(Integer, default=0)
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    lessons = relationship("Lesson", back_populates="course", order_by="Lesson.order")
    enrollments = relationship("Enrollment", back_populates="course")


class Lesson(Base):
    __tablename__ = "lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String(200), nullable=False)
    title_en = Column(String(200))
    content = Column(Text)  # Markdown content
    video_url = Column(String(500))
    duration_minutes = Column(Integer)
    order = Column(Integer, default=0)
    is_free = Column(Boolean, default=False)
    
    course = relationship("Course", back_populates="lessons")


class Enrollment(Base):
    __tablename__ = "enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    progress = Column(Float, default=0)  # 0-100
    completed_lessons = Column(JSON, default=list)  # [1, 3, 5]
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")


class Mentor(Base):
    __tablename__ = "mentors"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String(100), nullable=False)
    name_en = Column(String(100))
    title = Column(String(200))
    title_en = Column(String(200))
    avatar_emoji = Column(String(10), default="🎯")
    bio = Column(Text)
    bio_en = Column(Text)
    skills = Column(JSON, default=list)
    experience_years = Column(Integer)
    hourly_rate = Column(Float, default=0)
    rating = Column(Float, default=5.0)
    total_sessions = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)
    specialties = Column(JSON, default=list)


class MentorMatch(Base):
    __tablename__ = "mentor_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mentor_id = Column(Integer, ForeignKey("mentors.id"), nullable=False)
    status = Column(String(20), default="pending")  # pending, accepted, rejected, completed
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Certification(Base):
    __tablename__ = "certifications"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    name_en = Column(String(200))
    description = Column(Text)
    description_en = Column(Text)
    icon_emoji = Column(String(10), default="🏆")
    icon_color = Column(String(20), default="#6366f1")
    category = Column(String(50))
    modules_required = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)


# ========== OPC健康 ==========
class HealthRecord(Base):
    __tablename__ = "health_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    record_type = Column(String(30))  # daily_checkin, exercise, sleep, stress
    
    # 日常签到
    mood_score = Column(Integer, nullable=True)  # 1-10
    energy_level = Column(Integer, nullable=True)  # 1-10
    stress_level = Column(Integer, nullable=True)  # 1-10
    work_hours = Column(Float, nullable=True)
    sleep_hours = Column(Float, nullable=True)
    
    # 运动
    exercise_type = Column(String(50), nullable=True)
    exercise_duration = Column(Integer, nullable=True)  # minutes
    exercise_intensity = Column(String(20), nullable=True)  # light, moderate, intense
    
    # 自由记录
    notes = Column(Text, nullable=True)
    tags = Column(JSON, default=list)
    
    user = relationship("User", back_populates="health_records")


class HealthGoal(Base):
    __tablename__ = "health_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal_type = Column(String(30))  # sleep, exercise, stress, work_life_balance
    target_value = Column(Float)
    current_value = Column(Float, default=0)
    unit = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class HealthInsight(Base):
    __tablename__ = "health_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    insight_type = Column(String(30))  # warning, recommendation, encouragement
    title = Column(String(200))
    content = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# ========== 揭榜挂帅 (项目) ==========
class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    project_code = Column(String(50))
    publisher_name = Column(String(200))
    contact_person = Column(String(100))
    contact_phone = Column(String(50))
    contact_email = Column(String(100))
    industry = Column(String(50))
    technology_field = Column(String(200))
    budget_min = Column(Float, default=0)
    budget_max = Column(Float, default=0)
    description = Column(Text)
    requirements = Column(Text)
    deadline = Column(DateTime, nullable=True)
    status = Column(String(20), default="open")  # open, in_progress, completed, closed
    view_count = Column(Integer, default=0)
    bid_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    bids = relationship("ProjectBid", back_populates="project")


class ProjectBid(Base):
    __tablename__ = "project_bids"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    proposal = Column(Text)
    budget_quote = Column(Float)
    timeline_days = Column(Integer)
    status = Column(String(20), default="pending")  # pending, accepted, rejected
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    project = relationship("Project", back_populates="bids")


# ========== 社区 (OPC交流) ==========
class CommunityPost(Base):
    __tablename__ = "community_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(300))
    content = Column(Text, nullable=False)
    post_type = Column(String(30))  # discussion, question, share, collaboration
    tags = Column(JSON, default=list)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    is_pinned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("community_posts.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    like_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# ========== A2A 超级个体 ==========
class AgentProfile(Base):
    __tablename__ = "agent_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    avatar_emoji = Column(String(10), default="🤖")
    agent_type = Column(String(30))  # hunter, architect, assistant, analyst
    description = Column(Text)
    skills = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    config = Column(JSON, default=dict)  # Agent-specific configuration
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="agent_profiles")


class AgentMessage(Base):
    __tablename__ = "agent_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    from_agent_id = Column(Integer, ForeignKey("agent_profiles.id"), nullable=False)
    to_agent_id = Column(Integer, ForeignKey("agent_profiles.id"), nullable=True)
    message_type = Column(String(30))  # task, response, notification, match
    content = Column(Text, nullable=False)
    metadata_ = Column("metadata", JSON, default=dict)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# ========== 消息系统 ==========
class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    sender = relationship("User", foreign_keys=[sender_id], back_populates="messages_sent")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="messages_received")
