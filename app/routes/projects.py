"""
OPC Platform - Projects API (揭榜挂帅)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, func
from typing import Optional
from app.database import get_db
from app.models import Project, ProjectBid, User

router = APIRouter(prefix="/api/projects", tags=["Projects"])

@router.get("")
def list_projects(
    industry: Optional[str] = None,
    search: Optional[str] = None,
    budget_min: Optional[float] = None,
    budget_max: Optional[float] = None,
    status: str = "open",
    sort: str = "latest",
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Project).filter(Project.status == status)
    if industry:
        query = query.filter(Project.industry == industry)
    if search:
        query = query.filter(or_(
            Project.title.contains(search),
            Project.description.contains(search),
            Project.publisher_name.contains(search),
        ))
    if budget_min:
        query = query.filter(Project.budget_max >= budget_min)
    if budget_max:
        query = query.filter(Project.budget_min <= budget_max)
    
    total = query.count()
    if sort == "budget_high":
        query = query.order_by(desc(Project.budget_max))
    elif sort == "budget_low":
        query = query.order_by(Project.budget_min)
    else:
        query = query.order_by(desc(Project.created_at))
    
    projects = query.offset((page-1)*limit).limit(limit).all()
    
    return {
        "total": total,
        "page": page,
        "projects": [{
            "id": p.id,
            "title": p.title,
            "publisher_name": p.publisher_name,
            "industry": p.industry,
            "technology_field": p.technology_field,
            "budget_min": p.budget_min,
            "budget_max": p.budget_max,
            "description": p.description[:200] if p.description else "",
            "contact_person": p.contact_person,
            "status": p.status,
            "view_count": p.view_count,
            "bid_count": p.bid_count,
            "deadline": p.deadline.isoformat() if p.deadline else None,
        } for p in projects]
    }

@router.get("/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    project.view_count += 1
    db.commit()
    return {
        "id": project.id,
        "title": project.title,
        "project_code": project.project_code,
        "publisher_name": project.publisher_name,
        "contact_person": project.contact_person,
        "contact_phone": project.contact_phone,
        "contact_email": project.contact_email,
        "industry": project.industry,
        "technology_field": project.technology_field,
        "budget_min": project.budget_min,
        "budget_max": project.budget_max,
        "description": project.description,
        "requirements": project.requirements,
        "status": project.status,
        "view_count": project.view_count,
        "bid_count": project.bid_count,
        "deadline": project.deadline.isoformat() if project.deadline else None,
        "created_at": project.created_at.isoformat(),
    }

@router.get("/industries/stats")
def industry_stats(db: Session = Depends(get_db)):
    stats = db.query(
        Project.industry,
        func.count(Project.id).label("count"),
        func.sum(Project.budget_max).label("total_budget")
    ).filter(Project.status == "open").group_by(Project.industry).all()
    return {"industries": [{
        "name": s[0],
        "count": s[1],
        "total_budget": s[2] or 0,
    } for s in stats]}

@router.post("/{project_id}/bid")
def submit_bid(
    project_id: int,
    user_id: int = 1,
    proposal: str = "",
    budget_quote: float = 0,
    timeline_days: int = 30,
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    
    bid = ProjectBid(
        project_id=project_id,
        user_id=user_id,
        proposal=proposal,
        budget_quote=budget_quote,
        timeline_days=timeline_days,
    )
    db.add(bid)
    project.bid_count += 1
    db.commit()
    db.refresh(bid)
    return {"message": "Bid submitted", "bid_id": bid.id}

@router.get("/{project_id}/bids")
def get_bids(project_id: int, db: Session = Depends(get_db)):
    bids = db.query(ProjectBid).filter(ProjectBid.project_id == project_id).all()
    return {"bids": [{
        "id": b.id,
        "user_id": b.user_id,
        "proposal": b.proposal,
        "budget_quote": b.budget_quote,
        "timeline_days": b.timeline_days,
        "status": b.status,
        "created_at": b.created_at.isoformat(),
    } for b in bids]}



@router.post("/seed")
def seed_projects(db: Session = Depends(get_db)):
    if db.query(Project).count() > 0:
        return {"message": "Already seeded", "count": db.query(Project).count()}
    
    projects = [
        {"title":"海上风电场智能运维场景","publisher_name":"江苏省国信集团有限公司","contact_person":"叶兴沛","industry":"新能源","technology_field":"人工智能,物联网,大数据","budget_min":2000000,"budget_max":3000000,"description":"融合人工智能技术，在海上风电项目建设智能运维系统中对风机状态进行实时评估和远程运维，实现海上风电机组无人巡检、故障预测维护"},
        {"title":"智慧电厂全景感知与自主优化场景","publisher_name":"江苏省国信集团有限公司","contact_person":"王强","industry":"能源","technology_field":"人工智能,数字孪生,物联网","budget_min":2000000,"budget_max":3000000,"description":"部署智能传感、工业互联网平台和自主控制系统，构建AI+数字孪生电厂，涵盖燃料输送智能调度、机组参数实时监控"},
        {"title":"300MW级高温绝热压缩空气储能系统智能运行场景","publisher_name":"江苏省国信集团有限公司","contact_person":"杨正","industry":"储能","technology_field":"人工智能,故障诊断","budget_min":8000000,"budget_max":8000000,"description":"建设智能灵活调控+实时滚动优化+高精度故障诊断三位一体的全过程智能运行体系"},
        {"title":"施工安全智能监测场景","publisher_name":"江苏省国信集团有限公司","contact_person":"王毅","industry":"安全监测","technology_field":"人工智能,无人机,数字孪生","budget_min":2000000,"budget_max":3000000,"description":"利用无人机、机器狗、安全传感器等，在电厂基建工地应用智慧工地解决方案"},
        {"title":"路网营运知识工程场景","publisher_name":"江苏交通控股有限公司","contact_person":"王浩淼","industry":"交通","technology_field":"人工智能,知识图谱,大数据","budget_min":2000000,"budget_max":2000000,"description":"围绕路网运行复杂高频业务场景，聚焦多模态数据集规范建设、知识库语义对齐"},
        {"title":"路网智慧管控场景","publisher_name":"江苏交通控股有限公司","contact_person":"王浩淼","industry":"交通","technology_field":"人工智能,计算机视觉","budget_min":2000000,"budget_max":5000000,"description":"基于AI视频分析与交通流预测技术，实现路网事件自动检测、拥堵预警、应急资源智能调度"},
        {"title":"智能客服场景","publisher_name":"江苏交通控股有限公司","contact_person":"钱旻","industry":"交通","technology_field":"人工智能,大模型,NLP","budget_min":7000000,"budget_max":7000000,"description":"基于交通行业大模型优化意图识别与语义理解，构建智慧客服智能体系统"},
        {"title":"智慧收费清分与结算场景","publisher_name":"江苏交通控股有限公司","contact_person":"奚韩","industry":"交通","technology_field":"人工智能,数据分析","budget_min":24000000,"budget_max":24000000,"description":"基于智能数据分析技术以及模型算法，构建结算对账优化系统"},
        {"title":"媒体生产全链路智能协同系统","publisher_name":"江苏省广播电视集团有限公司","contact_person":"席鲁江","industry":"传媒","technology_field":"人工智能","budget_min":1000000,"budget_max":3000000,"description":"构建媒体内容生产全链路AI协同平台，实现选题策划、素材采集、内容编辑的智能化调度"},
        {"title":"机场飞行区安全风险智能监测场景","publisher_name":"东部机场集团有限公司","contact_person":"王苗苗","industry":"航空安全","technology_field":"人工智能,计算机视觉,传感器融合","budget_min":6000000,"budget_max":6000000,"description":"结合监控、雷达数据，运用多源传感融合和AI计算机视觉技术，实现跑道非法入侵、鸟击等核心风险智能识别"},
        {"title":"AI技术赋能3D服装设计场景","publisher_name":"江苏省苏豪控股集团有限公司","contact_person":"邢梦婷","industry":"纺织服装","technology_field":"人工智能,3D虚拟打样","budget_min":1500000,"budget_max":1500000,"description":"聚焦服装研发需求，智能分析市场趋势与客户画像，3D虚拟打样减少浪费"},
        {"title":"跨境电商选品数据驱动场景","publisher_name":"江苏省苏豪控股集团有限公司","contact_person":"邢梦婷","industry":"跨境电商","technology_field":"人工智能,大数据","budget_min":3600000,"budget_max":3600000,"description":"以AI赋能B2B贸易为核心，构建覆盖建站获客-内容生成-智能营销-一键通关全流程"},
        {"title":"苏豪云大模型驱动跨境电商场景","publisher_name":"江苏省苏豪控股集团有限公司","contact_person":"邢梦婷","industry":"跨境电商","technology_field":"人工智能,大模型,NLP","budget_min":5000000,"budget_max":5000000,"description":"依托自主微调的苏豪云电商垂直大模型，构建智能化内容生成与合规引擎"},
        {"title":"轮胎智能制造AI应用场景","publisher_name":"江苏省苏豪控股集团有限公司","contact_person":"邢梦婷","industry":"先进制造","technology_field":"人工智能","budget_min":1000000,"budget_max":3000000,"description":"将AI技术应用于轮胎智能制造全流程，包括工艺参数优化、质量在线检测"},
        {"title":"安全生产智能预警与管控场景","publisher_name":"江苏省苏豪控股集团有限公司","contact_person":"邢梦婷","industry":"安全监测","technology_field":"人工智能,物联网,计算机视觉","budget_min":5000000,"budget_max":5000000,"description":"融合AI视觉与物联网技术构建立体化安全防控体系，实现风险感知、研判、处置闭环"},
        {"title":"化工安全与经营智能决策场景","publisher_name":"江苏省苏豪控股集团有限公司","contact_person":"邢梦婷","industry":"化工","technology_field":"人工智能,大模型,智能感知","budget_min":470000,"budget_max":470000,"description":"融合AI算力、大模型、智能感知等技术，围绕安全可控、提质增效目标"},
        {"title":"基于数据中台的AI+智能风险管控平台","publisher_name":"江苏省苏豪控股集团有限公司","contact_person":"邢梦婷","industry":"综合管理","technology_field":"人工智能,数据中台,知识图谱","budget_min":3500000,"budget_max":3500000,"description":"融合数据中台、AI视觉模型及知识图谱技术，构建数据资产体系"},
        {"title":"智慧供应链与绿色制造场景","publisher_name":"江苏省苏豪控股集团有限公司","contact_person":"邢梦婷","industry":"供应链","technology_field":"人工智能","budget_min":2000000,"budget_max":5000000,"description":"构建AI驱动的智慧供应链管理平台，实现采购、生产、物流全链路智能化协同"},
    ]
    
    for p in projects:
        db.add(Project(**p))
    db.commit()
    return {"message": f"Seeded {len(projects)} projects", "count": len(projects)}
