"""
OPC Platform - 支付服务
"""
import uuid
import time
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Dict, Optional

from app.models import Order, Payment, Refund, User, Project, ProjectBid

class PaymentService:
    """支付服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_order_no(self) -> str:
        """生成订单号"""
        timestamp = int(time.time() * 1000)
        random_str = uuid.uuid4().hex[:8].upper()
        return f"OPC{timestamp}{random_str}"
    
    def generate_payment_no(self) -> str:
        """生成支付流水号"""
        timestamp = int(time.time() * 1000)
        random_str = uuid.uuid4().hex[:8].upper()
        return f"PAY{timestamp}{random_str}"
    
    def generate_refund_no(self) -> str:
        """生成退款单号"""
        timestamp = int(time.time() * 1000)
        random_str = uuid.uuid4().hex[:8].upper()
        return f"REF{timestamp}{random_str}"
    
    def create_order(
        self,
        user_id: int,
        title: str,
        amount: float,
        description: str = None,
        project_id: int = None,
        bid_id: int = None,
        currency: str = "CNY"
    ) -> Order:
        """创建订单"""
        order = Order(
            order_no=self.generate_order_no(),
            user_id=user_id,
            project_id=project_id,
            bid_id=bid_id,
            title=title,
            description=description,
            amount=amount,
            currency=currency,
            status="pending",
            payment_status="unpaid",
            expires_at=datetime.utcnow() + timedelta(hours=24)  # 24小时过期
        )
        
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        
        return order
    
    def create_payment(
        self,
        order_id: int,
        payment_method: str,
        amount: float = None
    ) -> Payment:
        """创建支付记录"""
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError("订单不存在")
        
        if order.payment_status == "paid":
            raise ValueError("订单已支付")
        
        payment = Payment(
            order_id=order_id,
            payment_no=self.generate_payment_no(),
            amount=amount or order.amount,
            currency=order.currency,
            payment_method=payment_method,
            status="pending"
        )
        
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        
        return payment
    
    def process_payment(
        self,
        payment_id: int,
        third_party_id: str = None,
        third_party_status: str = None,
        third_party_response: dict = None
    ) -> Payment:
        """处理支付结果"""
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise ValueError("支付记录不存在")
        
        # 更新支付信息
        payment.third_party_id = third_party_id
        payment.third_party_status = third_party_status
        payment.third_party_response = third_party_response or {}
        
        # 根据第三方状态更新支付状态
        if third_party_status in ["success", "TRADE_SUCCESS", "TRADE_FINISHED"]:
            payment.status = "success"
            payment.paid_at = datetime.utcnow()
            
            # 更新订单状态
            order = payment.order
            order.payment_status = "paid"
            order.status = "paid"
            order.paid_at = datetime.utcnow()
            order.payment_id = third_party_id
            
            # 如果是项目投标，更新投标状态
            if order.bid_id:
                bid = self.db.query(ProjectBid).filter(ProjectBid.id == order.bid_id).first()
                if bid:
                    bid.status = "accepted"
        
        elif third_party_status in ["failed", "TRADE_CLOSED"]:
            payment.status = "failed"
        
        self.db.commit()
        self.db.refresh(payment)
        
        return payment
    
    def create_refund(
        self,
        order_id: int,
        amount: float,
        reason: str = None,
        payment_id: int = None
    ) -> Refund:
        """创建退款"""
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError("订单不存在")
        
        if order.payment_status != "paid":
            raise ValueError("订单未支付，无法退款")
        
        if amount > order.amount:
            raise ValueError("退款金额不能超过订单金额")
        
        refund = Refund(
            order_id=order_id,
            payment_id=payment_id,
            refund_no=self.generate_refund_no(),
            amount=amount,
            reason=reason,
            status="pending"
        )
        
        self.db.add(refund)
        self.db.commit()
        self.db.refresh(refund)
        
        return refund
    
    def process_refund(
        self,
        refund_id: int,
        third_party_id: str = None,
        third_party_status: str = None,
        third_party_response: dict = None
    ) -> Refund:
        """处理退款结果"""
        refund = self.db.query(Refund).filter(Refund.id == refund_id).first()
        if not refund:
            raise ValueError("退款记录不存在")
        
        # 更新退款信息
        refund.third_party_id = third_party_id
        refund.third_party_status = third_party_status
        refund.third_party_response = third_party_response or {}
        
        # 根据第三方状态更新退款状态
        if third_party_status in ["success", "REFUND_SUCCESS"]:
            refund.status = "success"
            refund.processed_at = datetime.utcnow()
            
            # 更新订单状态
            order = refund.order
            if refund.amount >= order.amount:
                order.payment_status = "refunded"
                order.status = "refunded"
            
            # 更新支付状态
            if refund.payment_id:
                payment = refund.payment
                payment.status = "refunded"
                payment.refunded_at = datetime.utcnow()
        
        elif third_party_status in ["failed", "REFUND_FAILED"]:
            refund.status = "failed"
        
        self.db.commit()
        self.db.refresh(refund)
        
        return refund
    
    def get_order_by_no(self, order_no: str) -> Optional[Order]:
        """根据订单号获取订单"""
        return self.db.query(Order).filter(Order.order_no == order_no).first()
    
    def get_user_orders(
        self,
        user_id: int,
        status: str = None,
        page: int = 1,
        limit: int = 20
    ) -> Dict:
        """获取用户订单列表"""
        query = self.db.query(Order).filter(Order.user_id == user_id)
        
        if status:
            query = query.filter(Order.status == status)
        
        total = query.count()
        orders = query.order_by(Order.created_at.desc()).offset((page-1)*limit).limit(limit).all()
        
        return {
            "total": total,
            "page": page,
            "limit": limit,
            "orders": [{
                "id": order.id,
                "order_no": order.order_no,
                "title": order.title,
                "amount": order.amount,
                "currency": order.currency,
                "status": order.status,
                "payment_status": order.payment_status,
                "payment_method": order.payment_method,
                "created_at": order.created_at.isoformat(),
                "paid_at": order.paid_at.isoformat() if order.paid_at else None,
            } for order in orders]
        }
    
    def get_order_payments(self, order_id: int) -> list:
        """获取订单的支付记录"""
        payments = self.db.query(Payment).filter(Payment.order_id == order_id).all()
        
        return [{
            "id": payment.id,
            "payment_no": payment.payment_no,
            "amount": payment.amount,
            "currency": payment.currency,
            "payment_method": payment.payment_method,
            "status": payment.status,
            "third_party_id": payment.third_party_id,
            "created_at": payment.created_at.isoformat(),
            "paid_at": payment.paid_at.isoformat() if payment.paid_at else None,
        } for payment in payments]
    
    def get_order_refunds(self, order_id: int) -> list:
        """获取订单的退款记录"""
        refunds = self.db.query(Refund).filter(Refund.order_id == order_id).all()
        
        return [{
            "id": refund.id,
            "refund_no": refund.refund_no,
            "amount": refund.amount,
            "reason": refund.reason,
            "status": refund.status,
            "third_party_id": refund.third_party_id,
            "created_at": refund.created_at.isoformat(),
            "processed_at": refund.processed_at.isoformat() if refund.processed_at else None,
        } for refund in refunds]
    
    def get_payment_stats(self, user_id: int = None) -> Dict:
        """获取支付统计信息"""
        query = self.db.query(Order)
        
        if user_id:
            query = query.filter(Order.user_id == user_id)
        
        total_orders = query.count()
        paid_orders = query.filter(Order.payment_status == "paid").count()
        total_amount = query.filter(Order.payment_status == "paid").with_entities(
            func.sum(Order.amount)
        ).scalar() or 0
        
        refunded_amount = self.db.query(func.sum(Refund.amount)).filter(
            Refund.status == "success"
        ).scalar() or 0
        
        return {
            "total_orders": total_orders,
            "paid_orders": paid_orders,
            "unpaid_orders": total_orders - paid_orders,
            "total_amount": total_amount,
            "refunded_amount": refunded_amount,
            "net_amount": total_amount - refunded_amount
        }
