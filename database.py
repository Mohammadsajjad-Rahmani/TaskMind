from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

SQLALCHEMY_DATABASE_URL = "sqlite:///./taskmind.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 1. جدول جدید کاربران
class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # ارتباط با تسک‌های مربوط به این کاربر
    tasks = relationship("TaskDB", back_populates="owner")

# 2. جدول تسک‌ها (با اضافه شدن Foreign Key)
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

    # کلید خارجی و رابطه با کاربر
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("UserDB", back_populates="tasks")

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()