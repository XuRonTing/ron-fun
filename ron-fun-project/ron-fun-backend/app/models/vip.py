from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.db.session import Base

class VIP(Base):
    __tablename__ = "vips"

    vip_id = Column(Integer, primary_key=True, index=True)
    vip_name = Column(String(50), nullable=False, index=True)
    vip_icon = Column(String(255), nullable=True)
    vip_level = Column(Integer, nullable=False, default=0, index=True)
    vip_total_point = Column(Integer, nullable=False, default=0)
    vip_expiration = Column(DateTime, nullable=True)  # VIP过期时间，默认为null表示不过期
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False) 