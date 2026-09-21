from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base, engine

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    tasks = relationship("TaskDB", back_populates="owner")


class TaskDB(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    priority = Column(String)
    estimated_hours = Column(Float)
    suggested_subtasks = Column(String)
    is_duplicate = Column(Boolean, default=False)
    duplicate_warning = Column(String, nullable=True)
    is_completed = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("UserDB", back_populates="tasks")

# ساخت جدول‌ها
Base.metadata.create_all(bind=engine)