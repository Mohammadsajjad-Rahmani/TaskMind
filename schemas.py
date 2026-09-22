from pydantic import BaseModel
from typing import List, Optional

# اسکیمای ثبت‌نام
class UserCreate(BaseModel):
    username: str
    password: str

# اسکیمای خروجی کاربر
class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

# اسکیمای خروجی توکن JWT
class Token(BaseModel):
    access_token: str
    token_type: str

class TaskCreate(BaseModel):
    title: str
    description: str

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    priority: str
    estimated_hours: float
    is_duplicate: bool
    duplicate_warning: Optional[str] = None
    is_completed: bool = False

    class Config:
        from_attributes = True

class DailySummaryResponse(BaseModel):
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    summary_markdown: str