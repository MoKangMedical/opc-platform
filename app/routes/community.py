"""
OPC Platform - Community API (OPC交流社区)
帖子、评论、点赞、私信
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import Optional
from app.database import get_db
from app.models import CommunityPost, Comment, Message, User

router = APIRouter(prefix="/api/community", tags=["Community"])

# ========== 帖子 ==========
@router.get("/posts")
def list_posts(
    post_type: Optional[str] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,
    sort: str = "latest",
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(CommunityPost)
    if post_type:
        query = query.filter(CommunityPost.post_type == post_type)
    if search:
        query = query.filter(CommunityPost.title.contains(search) | CommunityPost.content.contains(search))
    
    total = query.count()
    if sort == "hot":
        query = query.order_by(desc(CommunityPost.like_count))
    elif sort == "comments":
        query = query.order_by(desc(CommunityPost.comment_count))
    else:
        query = query.order_by(desc(CommunityPost.is_pinned), desc(CommunityPost.created_at))
    
    posts = query.offset((page-1)*limit).limit(limit).all()
    return {
        "total": total, "page": page,
        "posts": [{
            "id": p.id, "title": p.title, "content": p.content[:300],
            "post_type": p.post_type, "tags": p.tags or [],
            "like_count": p.like_count, "comment_count": p.comment_count, "view_count": p.view_count,
            "is_pinned": p.is_pinned, "created_at": p.created_at.isoformat(),
            "author_id": p.author_id,
        } for p in posts]
    }

@router.get("/posts/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
    if not post:
        raise HTTPException(404, "Post not found")
    post.view_count += 1
    db.commit()
    comments = db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at).all()
    return {
        "id": post.id, "title": post.title, "content": post.content,
        "post_type": post.post_type, "tags": post.tags or [],
        "like_count": post.like_count, "comment_count": post.comment_count, "view_count": post.view_count,
        "author_id": post.author_id, "created_at": post.created_at.isoformat(),
        "comments": [{
            "id": c.id, "content": c.content, "author_id": c.author_id,
            "parent_id": c.parent_id, "like_count": c.like_count,
            "created_at": c.created_at.isoformat(),
        } for c in comments]
    }

@router.post("/posts")
def create_post(
    author_id: int = 1,
    title: str = "",
    content: str = "",
    post_type: str = "discussion",
    tags: list = [],
    db: Session = Depends(get_db)
):
    post = CommunityPost(author_id=author_id, title=title, content=content, post_type=post_type, tags=tags)
    db.add(post)
    db.commit()
    db.refresh(post)
    return {"id": post.id, "message": "Post created"}

@router.post("/posts/{post_id}/like")
def like_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
    if not post:
        raise HTTPException(404, "Post not found")
    post.like_count += 1
    db.commit()
    return {"like_count": post.like_count}

# ========== 评论 ==========
@router.post("/posts/{post_id}/comments")
def create_comment(
    post_id: int,
    author_id: int = 1,
    content: str = "",
    parent_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    post = db.query(CommunityPost).filter(CommunityPost.id == post_id).first()
    if not post:
        raise HTTPException(404, "Post not found")
    comment = Comment(post_id=post_id, author_id=author_id, content=content, parent_id=parent_id)
    db.add(comment)
    post.comment_count += 1
    db.commit()
    db.refresh(comment)
    return {"id": comment.id, "message": "Comment added"}

@router.post("/comments/{comment_id}/like")
def like_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(404, "Comment not found")
    comment.like_count += 1
    db.commit()
    return {"like_count": comment.like_count}

# ========== 私信 ==========
@router.get("/messages")
def get_messages(user_id: int = 1, db: Session = Depends(get_db)):
    messages = db.query(Message).filter(
        (Message.sender_id == user_id) | (Message.receiver_id == user_id)
    ).order_by(desc(Message.created_at)).limit(50).all()
    return {"messages": [{
        "id": m.id, "sender_id": m.sender_id, "receiver_id": m.receiver_id,
        "content": m.content, "is_read": m.is_read, "created_at": m.created_at.isoformat(),
    } for m in messages]}

@router.post("/messages")
def send_message(
    sender_id: int = 1,
    receiver_id: int = 1,
    content: str = "",
    db: Session = Depends(get_db)
):
    msg = Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return {"id": msg.id, "message": "Message sent"}

@router.get("/messages/unread-count")
def unread_count(user_id: int = 1, db: Session = Depends(get_db)):
    count = db.query(Message).filter(
        Message.receiver_id == user_id, Message.is_read == False
    ).count()
    return {"unread": count}

# ========== 统计 ==========
@router.get("/stats")
def community_stats(db: Session = Depends(get_db)):
    total_posts = db.query(CommunityPost).count()
    total_comments = db.query(Comment).count()
    total_users = db.query(User).count()
    active_posts_7d = db.query(CommunityPost).count()  # simplified
    return {
        "total_posts": total_posts,
        "total_comments": total_comments,
        "total_users": total_users,
        "active_posts_7d": active_posts_7d,
    }
