from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.ext.declarative import declared_attr

class Base:
    """
    所有模型的基类，包含公共属性和方法
    """
    
    # 使用类名小写复数形式作为表名
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"
    
    # 主键ID，自增
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    
    # 通用时间戳字段
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 软删除标记
    is_deleted = Column(Boolean, default=False, comment="是否删除")
    
    @classmethod
    def get_by_id(cls, db, id):
        """
        根据ID获取记录
        
        Args:
            db: 数据库会话
            id: 记录ID
            
        Returns:
            模型实例或None
        """
        return db.query(cls).filter(cls.id == id, cls.is_deleted == False).first()
    
    @classmethod
    def get_all(cls, db, skip=0, limit=100):
        """
        获取所有记录
        
        Args:
            db: 数据库会话
            skip: 跳过记录数
            limit: 限制返回记录数
            
        Returns:
            记录列表
        """
        return db.query(cls).filter(cls.is_deleted == False).offset(skip).limit(limit).all()
    
    def save(self, db):
        """
        保存当前记录
        
        Args:
            db: 数据库会话
            
        Returns:
            模型实例
        """
        db.add(self)
        db.commit()
        db.refresh(self)
        return self
    
    def update(self, db, **kwargs):
        """
        更新当前记录
        
        Args:
            db: 数据库会话
            **kwargs: 要更新的字段
            
        Returns:
            模型实例
        """
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.updated_at = datetime.now()
        db.commit()
        db.refresh(self)
        return self
    
    def delete(self, db):
        """
        软删除当前记录
        
        Args:
            db: 数据库会话
            
        Returns:
            模型实例
        """
        self.is_deleted = True
        self.updated_at = datetime.now()
        db.commit()
        return self
    
    def hard_delete(self, db):
        """
        硬删除当前记录
        
        Args:
            db: 数据库会话
            
        Returns:
            None
        """
        db.delete(self)
        db.commit()
        return None 