from pydantic import BaseModel
from typing import List, Optional

# ورودی کاربر
class TaskCreate(BaseModel):
    title: str
    description: str

# خروجی کامل تسک
class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    priority: str
    estimated_hours: float
    suggested_subtasks: List[str]
    is_duplicate: bool
    duplicate_warning: Optional[str] = None
    is_completed: bool = False

# خروجی گزارش روزانه
class DailySummaryResponse(BaseModel):
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    summary_markdown: str