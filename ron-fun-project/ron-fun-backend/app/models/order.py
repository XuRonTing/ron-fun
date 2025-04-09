from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False, index=True)
    order_status = Column(Integer, nullable=False, default=1, index=True)  # 1：待支付 2：已支付 3：已取消
    order_time = Column(DateTime, nullable=True)  # 订单支付时间
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关联关系
    user = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders") 