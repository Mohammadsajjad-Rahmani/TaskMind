from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# مسیر دیتابیس فایل SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./taskmind.db"

# ساخت موتور دیتابیس (check_same_thread=False برای SQLite در FastAPI الزامی است)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# تعریف مدل دیتابیس (جدول tasks)
class TaskDB(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    priority = Column(String)
    estimated_hours = Column(Float)
    suggested_subtasks = Column(String)  # با کاراکتر | جدا می‌کنیم
    is_duplicate = Column(Boolean, default=False)
    duplicate_warning = Column(String, nullable=True)
    is_completed = Column(Boolean, default=False)

# ساخت جدول‌ها در صورت عدم وجود
Base.metadata.create_all(bind=engine)

# Dependency برای مدیریت اتصال‌ها در FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()