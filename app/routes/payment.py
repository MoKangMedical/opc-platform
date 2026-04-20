"""
OPC Platform - 支付API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.database import get_db
from app.models import User
from app.routes.auth import get_current_user
from app.services.payment import PaymentService

router = APIRouter(prefix="/api/payment", tags=["支付"])

# ========== Pydantic模型 ==========
class CreateOrderRequest(BaseModel):
    title: str
    amount: float
    description: Optional[str] = None
    project_id: Optional[int] = None
    bid_id: Optional[int] = None
    currency: str = "CNY"

class CreatePaymentRequest(BaseModel):
    order_id: int
    payment_method: str  # alipay, wechat, bank_transfer

class ProcessPaymentRequest(BaseModel):
    payment_id: int
    third_party_id: Optional[str] = None
    third_party_status: Optional[str] = None
    third_party_response: Optional[dict] = None

class CreateRefundRequest(BaseModel):
    order_id: int
    amount: float
    reason: Optional[str] = None
    payment_id: Optional[int] = None

class ProcessRefundRequest(BaseModel):
    refund_id: int
    third_party_id: Optional[str] = None
    third_party_status: Optional[str] = None
    third_party_response: Optional[dict] = None

# ========== API端点 ==========
@router.post("/orders", summary="创建订单")
async def create_order(
    request: CreateOrderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建新订单"""
    payment_service = PaymentService(db)
    
    try:
        order = payment_service.create_order(
            user_id=current_user.id,
            title=request.title,
            amount=request.amount,
            description=request.description,
            project_id=request.project_id,
            bid_id=request.bid_id,
            currency=request.currency
        )
        
        return {
            "order_id": order.id,
            "order_no": order.order_no,
            "title": order.title,
            "amount": order.amount,
            "currency": order.currency,
            "status": order.status,
            "payment_status": order.payment_status,
            "expires_at": order.expires_at.isoformat() if order.expires_at else None,
            "created_at": order.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/orders/{order_no}", summary="获取订单详情")
async def get_order(
    order_no: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取订单详情"""
    payment_service = PaymentService(db)
    order = payment_service.get_order_by_no(order_no)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    # 检查权限
    if order.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 获取支付和退款记录
    payments = payment_service.get_order_payments(order.id)
    refunds = payment_service.get_order_refunds(order.id)
    
    return {
        "id": order.id,
        "order_no": order.order_no,
        "title": order.title,
        "description": order.description,
        "amount": order.amount,
        "currency": order.currency,
        "status": order.status,
        "payment_status": order.payment_status,
        "payment_method": order.payment_method,
        "payment_id": order.payment_id,
        "project_id": order.project_id,
        "bid_id": order.bid_id,
        "created_at": order.created_at.isoformat(),
        "updated_at": order.updated_at.isoformat(),
        "paid_at": order.paid_at.isoformat() if order.paid_at else None,
        "expires_at": order.expires_at.isoformat() if order.expires_at else None,
        "payments": payments,
        "refunds": refunds
    }

@router.get("/orders", summary="获取用户订单列表")
async def list_orders(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的订单列表"""
    payment_service = PaymentService(db)
    result = payment_service.get_user_orders(
        user_id=current_user.id,
        status=status,
        page=page,
        limit=limit
    )
    
    return result

@router.post("/payments", summary="创建支付")
async def create_payment(
    request: CreatePaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建支付记录"""
    payment_service = PaymentService(db)
    
    try:
        payment = payment_service.create_payment(
            order_id=request.order_id,
            payment_method=request.payment_method
        )
        
        return {
            "payment_id": payment.id,
            "payment_no": payment.payment_no,
            "amount": payment.amount,
            "currency": payment.currency,
            "payment_method": payment.payment_method,
            "status": payment.status,
            "created_at": payment.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/payments/process", summary="处理支付结果")
async def process_payment(
    request: ProcessPaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """处理第三方支付结果"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    payment_service = PaymentService(db)
    
    try:
        payment = payment_service.process_payment(
            payment_id=request.payment_id,
            third_party_id=request.third_party_id,
            third_party_status=request.third_party_status,
            third_party_response=request.third_party_response
        )
        
        return {
            "payment_id": payment.id,
            "payment_no": payment.payment_no,
            "status": payment.status,
            "third_party_id": payment.third_party_id,
            "paid_at": payment.paid_at.isoformat() if payment.paid_at else None
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/refunds", summary="创建退款")
async def create_refund(
    request: CreateRefundRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建退款申请"""
    payment_service = PaymentService(db)
    
    # 检查订单权限
    order = payment_service.get_order_by_no(request.order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    if order.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    try:
        refund = payment_service.create_refund(
            order_id=request.order_id,
            amount=request.amount,
            reason=request.reason,
            payment_id=request.payment_id
        )
        
        return {
            "refund_id": refund.id,
            "refund_no": refund.refund_no,
            "amount": refund.amount,
            "reason": refund.reason,
            "status": refund.status,
            "created_at": refund.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/refunds/process", summary="处理退款结果")
async def process_refund(
    request: ProcessRefundRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """处理第三方退款结果"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    payment_service = PaymentService(db)
    
    try:
        refund = payment_service.process_refund(
            refund_id=request.refund_id,
            third_party_id=request.third_party_id,
            third_party_status=request.third_party_status,
            third_party_response=request.third_party_response
        )
        
        return {
            "refund_id": refund.id,
            "refund_no": refund.refund_no,
            "status": refund.status,
            "third_party_id": refund.third_party_id,
            "processed_at": refund.processed_at.isoformat() if refund.processed_at else None
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/stats", summary="获取支付统计")
async def get_payment_stats(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取支付统计信息"""
    # 普通用户只能查看自己的统计
    if current_user.role != "admin":
        user_id = current_user.id
    
    payment_service = PaymentService(db)
    stats = payment_service.get_payment_stats(user_id=user_id)
    
    return stats
