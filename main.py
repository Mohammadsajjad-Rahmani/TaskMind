from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

# ایمپورت مدل‌های دیتابیس
from models import UserDB, TaskDB

# ایمپورت اسکیمارهای پایدانتیک
from schemas import (
    UserCreate, 
    UserResponse, 
    Token, 
    TaskCreate, 
    TaskResponse, 
    DailySummaryResponse
)

# ایمپورت دیتابیس
from database import get_db
from ai_engine import ai_engine
from dependencies import get_current_user
import auth

app = FastAPI(title="TaskMind API with Auth", version="3.2.0")

# ----------------- 🔐 احراز هویت -----------------

@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.username == user_data.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="این نام کاربری قبلا ثبت شده است.")
    
    hashed_pwd = auth.hash_password(user_data.password)
    new_user = UserDB(username=user_data.username, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="نام کاربری یا رمز عبور اشتباه است."
        )
    
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# ----------------- 📋 مدیریت تسک‌ها (محافظت شده) -----------------

@app.get("/tasks", response_model=List[TaskResponse])
def get_tasks(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    # دریافت تسک‌های اختصاصی کاربر جاری
    tasks = db.query(TaskDB).filter(TaskDB.user_id == current_user.id).all()
    result = []
    for t in tasks:
        subtasks_list = t.suggested_subtasks.split("|") if t.suggested_subtasks else []
        result.append(TaskResponse(
            id=t.id,
            title=t.title,
            description=t.description,
            priority=t.priority,
            estimated_hours=t.estimated_hours,
            suggested_subtasks=subtasks_list,
            is_duplicate=t.is_duplicate,
            duplicate_warning=t.duplicate_warning,
            is_completed=t.is_completed
        ))
    return result

@app.post("/tasks", response_model=TaskResponse)
def create_task(
    task: TaskCreate, 
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    full_text = f"{task.title} {task.description}"  
    priority = ai_engine.predict_priority(full_text)
    est_hours = ai_engine.predict_estimation(full_text) 
    subtasks = ai_engine.decompose_task(task.title, full_text)
        
    # بررسی تکراری بودن فقط در میان تسک‌های همین کاربر
    user_tasks = db.query(TaskDB).filter(TaskDB.user_id == current_user.id).all()
    existing_texts = [f"{t.title} {t.description}" for t in user_tasks]
    is_dup, dup_warning = ai_engine.check_duplicate(full_text, existing_texts)
    
    subtasks_str = "|".join(subtasks)
    
    db_task = TaskDB(
        title=task.title,
        description=task.description,
        priority=priority,
        estimated_hours=est_hours,
        suggested_subtasks=subtasks_str,
        is_duplicate=is_dup,
        duplicate_warning=dup_warning if is_dup else None,
        is_completed=False,
        user_id=current_user.id  # ذخیره شناسه کاربر مالک
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    return TaskResponse(
        id=db_task.id,
        title=db_task.title,
        description=db_task.description,
        priority=db_task.priority,
        estimated_hours=db_task.estimated_hours,
        suggested_subtasks=subtasks,
        is_duplicate=db_task.is_duplicate,
        duplicate_warning=db_task.duplicate_warning,
        is_completed=db_task.is_completed
    )

@app.patch("/tasks/{task_id}/toggle")
def toggle_task_status(
    task_id: int, 
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    # اطمینان از اینکه تسک متعلق به کاربر جاری است
    db_task = db.query(TaskDB).filter(TaskDB.id == task_id, TaskDB.user_id == current_user.id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found or unauthorized")
    
    db_task.is_completed = not db_task.is_completed
    db.commit()
    return {"message": "Status updated", "is_completed": db_task.is_completed}

@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int, 
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    db_task = db.query(TaskDB).filter(TaskDB.id == task_id, TaskDB.user_id == current_user.id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found or unauthorized")
    
    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted successfully"}

@app.get("/daily-summary", response_model=DailySummaryResponse)
def get_daily_summary(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    tasks = db.query(TaskDB).filter(TaskDB.user_id == current_user.id).all()
    total = len(tasks)
    completed = sum(1 for t in tasks if t.is_completed)
    pending = total - completed
    
    summary_md = f"### 📊 گزارش خلاصه روزانه ({current_user.username})\n"
    summary_md += f"- **کل تسک‌ها:** {total}\n"
    summary_md += f"- **تکمیل شده:** {completed} ✅\n"
    summary_md += f"- **در انتظار انجام:** {pending} ⏳\n\n"
    summary_md += "#### لیست تسک‌های باقی‌مانده:\n"
    for t in tasks:
        if not t.is_completed:
            summary_md += f"- [{t.priority}] **{t.title}** (~{t.estimated_hours}h)\n"
            
    return DailySummaryResponse(
        total_tasks=total,
        completed_tasks=completed,
        pending_tasks=pending,
        summary_markdown=summary_md
    )