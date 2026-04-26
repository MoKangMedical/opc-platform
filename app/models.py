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



# ========== 聊天室系统 =========
class ChatRoom(Base):
    """聊天室 - 支持多人实时聊天和Agent参与"""
    __tablename__ = "chat_rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    room_type = Column(String(20), default="public")  # public, private, agent_hybrid
    max_members = Column(Integer, default=50)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    members = relationship("ChatRoomMember", back_populates="room")
    messages = relationship("ChatMessage", back_populates="room")


class ChatRoomMember(Base):
    """聊天室成员"""
    __tablename__ = "chat_room_members"
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    agent_id = Column(Integer, ForeignKey("agent_profiles.id"), nullable=True)  # Agent成员
    role = Column(String(20), default="member")  # owner, admin, member, agent
    joined_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    room = relationship("ChatRoom", back_populates="members")


class ChatMessage(Base):
    """聊天消息 - 支持人和Agent发送"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False)
    sender_type = Column(String(10), nullable=False)  # user, agent, system
    sender_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    sender_agent_id = Column(Integer, ForeignKey("agent_profiles.id"), nullable=True)
    sender_name = Column(String(100))  # 显示名称
    content = Column(Text, nullable=False)
    message_type = Column(String(20), default="text")  # text, system, agent_response
    metadata_ = Column("metadata", JSON, default=dict)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    room = relationship("ChatRoom", back_populates="messages")


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


# ========== 订单和支付系统 ==========
class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    bid_id = Column(Integer, ForeignKey("project_bids.id"), nullable=True)
    
    # 订单信息
    title = Column(String(300), nullable=False)
    description = Column(Text)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="CNY")
    
    # 订单状态
    status = Column(String(20), default="pending")  # pending, paid, processing, completed, cancelled, refunded
    payment_status = Column(String(20), default="unpaid")  # unpaid, paid, refunded
    
    # 支付信息
    payment_method = Column(String(50))  # alipay, wechat, bank_transfer
    payment_id = Column(String(100))  # 第三方支付平台ID
    paid_at = Column(DateTime, nullable=True)
    
    # 时间信息
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    # 关系
    user = relationship("User", backref="orders")
    project = relationship("Project", backref="orders")
    bid = relationship("ProjectBid", backref="order")
    payments = relationship("Payment", back_populates="order")


class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    payment_no = Column(String(50), unique=True, nullable=False, index=True)
    
    # 支付信息
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="CNY")
    payment_method = Column(String(50))  # alipay, wechat, bank_transfer
    
    # 第三方支付信息
    third_party_id = Column(String(100))  # 第三方支付平台交易ID
    third_party_status = Column(String(50))  # 第三方支付平台状态
    third_party_response = Column(JSON, default=dict)  # 第三方支付平台响应
    
    # 支付状态
    status = Column(String(20), default="pending")  # pending, success, failed, refunded
    
    # 时间信息
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)
    refunded_at = Column(DateTime, nullable=True)
    
    # 关系
    order = relationship("Order", back_populates="payments")


class Refund(Base):
    __tablename__ = "refunds"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=True)
    refund_no = Column(String(50), unique=True, nullable=False, index=True)
    
    # 退款信息
    amount = Column(Float, nullable=False)
    reason = Column(Text)
    
    # 第三方退款信息
    third_party_id = Column(String(100))  # 第三方退款ID
    third_party_status = Column(String(50))
    third_party_response = Column(JSON, default=dict)
    
    # 退款状态
    status = Column(String(20), default="pending")  # pending, processing, success, failed
    
    # 时间信息
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # 关系
    order = relationship("Order", backref="refunds")
    payment = relationship("Payment", backref="refunds")


class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    invoice_no = Column(String(50), unique=True, nullable=False, index=True)
    
    # 发票信息
    title = Column(String(200), nullable=False)
    tax_no = Column(String(50))  # 税号
    amount = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0)
    total_amount = Column(Float, nullable=False)
    
    # 发票类型
    type = Column(String(20))  # personal, company
    category = Column(String(20))  # electronic, paper
    
    # 发票状态
    status = Column(String(20), default="pending")  # pending, issued, sent, cancelled
    
    # 开票信息
    company_name = Column(String(200))
    company_address = Column(String(500))
    company_phone = Column(String(50))
    bank_name = Column(String(200))
    bank_account = Column(String(50))
    
    # 时间信息
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    issued_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    
    # 关系
    order = relationship("Order", backref="invoices")
