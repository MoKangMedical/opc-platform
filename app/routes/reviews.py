"""
OPC Platform - 评价系统 API (from opc-marketplace)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models import Review, User

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])


class ReviewCreate(BaseModel):
    reviewer_id: int
    reviewee_id: int
    project_id: Optional[int] = None
    rating: float
    content: Optional[str] = None
    quality_score: Optional[float] = None
    communication_score: Optional[float] = None
    timeliness_score: Optional[float] = None
    professionalism_score: Optional[float] = None


@router.post("/")
def create_review(data: ReviewCreate, db: Session = Depends(get_db)):
    """提交评价"""
    if data.rating < 1 or data.rating > 5:
        raise HTTPException(status_code=400, detail="评分范围为1-5")

    review = Review(
        reviewer_id=data.reviewer_id,
        reviewee_id=data.reviewee_id,
        project_id=data.project_id,
        rating=data.rating,
        content=data.content,
        quality_score=data.quality_score,
        communication_score=data.communication_score,
        timeliness_score=data.timeliness_score,
        professionalism_score=data.professionalism_score,
    )
    db.add(review)

    reviewee = db.query(User).filter(User.id == data.reviewee_id).first()
    if reviewee:
        total = (reviewee.rating or 5.0) * (reviewee.rating_count or 0) + data.rating
        reviewee.rating_count = (reviewee.rating_count or 0) + 1
        reviewee.rating = round(total / reviewee.rating_count, 1)

    db.commit()

    return {"message": "评价提交成功", "review_id": review.id, "new_rating": reviewee.rating if reviewee else None}


@router.get("/user/{user_id}")
def get_user_reviews(
    user_id: int,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """获取用户的评价列表"""
    reviews = db.query(Review).filter(
        Review.reviewee_id == user_id
    ).order_by(Review.created_at.desc()).offset(offset).limit(limit).all()

    response = []
    for r in reviews:
        reviewer = db.query(User).filter(User.id == r.reviewer_id).first()
        response.append({
            "id": r.id,
            "reviewer_name": reviewer.display_name if reviewer else "匿名",
            "rating": r.rating,
            "content": r.content,
            "quality_score": r.quality_score,
            "communication_score": r.communication_score,
            "timeliness_score": r.timeliness_score,
            "professionalism_score": r.professionalism_score,
            "created_at": r.created_at.isoformat(),
        })

    return response


@router.get("/stats/{user_id}")
def get_review_stats(user_id: int, db: Session = Depends(get_db)):
    """获取用户评价统计"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    avg_scores = db.query(
        func.avg(Review.quality_score),
        func.avg(Review.communication_score),
        func.avg(Review.timeliness_score),
        func.avg(Review.professionalism_score),
    ).filter(Review.reviewee_id == user_id).first()

    return {
        "user_id": user_id,
        "overall_rating": user.rating,
        "total_reviews": user.rating_count,
        "avg_quality": round(avg_scores[0] or 0, 1),
        "avg_communication": round(avg_scores[1] or 0, 1),
        "avg_timeliness": round(avg_scores[2] or 0, 1),
        "avg_professionalism": round(avg_scores[3] or 0, 1),
    }
