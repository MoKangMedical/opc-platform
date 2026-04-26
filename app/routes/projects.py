"""
OPC Platform - Projects API (揭榜挂帅)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, func
from typing import Optional
from app.database import get_db
from app.models import Project, ProjectBid, User
from app.routes.auth import get_current_user

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
    proposal: str = "",
    budget_quote: float = 0,
    timeline_days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    
    bid = ProjectBid(
        project_id=project_id,
        user_id=user_id,
        user_id=current_user.id,
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
