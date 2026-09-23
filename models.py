from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # اضافه شدن cascade برای حذف تسک‌های کاربر پس از حذف کاربر
    tasks = relationship("TaskDB", back_populates="owner", cascade="all, delete-orphan")


class TaskDB(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    priority = Column(String, default="Medium")  # مقدار پیش‌فرض
    estimated_hours = Column(Float, default=1.0)
    
    # فیلدهای هوش مصنوعی
    is_duplicate = Column(Boolean, default=False)
    duplicate_warning = Column(String, nullable=True)
    
    # وضعیت تسک
    is_completed = Column(Boolean, default=False)
    
    # کلید خارجی و رابطه
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("UserDB", back_populates="tasks")