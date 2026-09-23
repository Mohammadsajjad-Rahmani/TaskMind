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
from database import get_db, engine, Base
from ai_engine import ai_engine
from dependencies import get_current_user
import auth

Base.metadata.create_all(bind=engine)

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
    current_user: UserDB = Depends(get_current_user)
):
    # دریافت مستقیم از رابطه ORM (بدون نیاز به کوئری صریح)
    return current_user.tasks

@app.post("/tasks", response_model=TaskResponse)
def create_task(
    task: TaskCreate, 
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    full_text = f"{task.title} {task.description}"  
    priority = ai_engine.predict_priority(full_text)
    est_hours = ai_engine.predict_estimation(full_text) 
        
    # استفاده مستقیم از رابطه ORM برای چک کردن تکراری‌ها
    existing_texts = [f"{t.title} {t.description}" for t in current_user.tasks]
    is_dup, dup_warning = ai_engine.check_duplicate(full_text, existing_texts)
    
    db_task = TaskDB(
        title=task.title,
        description=task.description,
        priority=priority,
        estimated_hours=est_hours,
        is_duplicate=is_dup,
        duplicate_warning=dup_warning if is_dup else None,
        is_completed=False,
        owner=current_user  # به جای user_id=current_user.id می‌توان مستقیم خود شیء کاربر را پاس داد
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    return db_task

@app.patch("/tasks/{task_id}/toggle")
def toggle_task_status(
    task_id: int, 
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    # کوئری زدن مستقیم روی دیتابیس برای پیدا کردن یک تسک خاص و احراز مالکیت همچنان روش سریع‌تر و استانداردتری است
    db_task = db.query(TaskDB).filter(TaskDB.id == task_id, TaskDB.user_id == current_user.id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="تسک یافت نشد یا شما دسترسی ندارید.")
    
    db_task.is_completed = not db_task.is_completed
    db.commit()
    return {"message": "وضعیت با موفقیت تغییر کرد", "is_completed": db_task.is_completed}

@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int, 
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    db_task = db.query(TaskDB).filter(TaskDB.id == task_id, TaskDB.user_id == current_user.id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="تسک یافت نشد یا شما دسترسی ندارید.")
    
    db.delete(db_task)
    db.commit()
    return {"message": "تسک با موفقیت حذف شد"}

@app.get("/daily-summary", response_model=DailySummaryResponse)
def get_daily_summary(
    current_user: UserDB = Depends(get_current_user)
):
    # دسترسی مستقیم به تسک‌های کاربر از طریق شیء current_user
    tasks = current_user.tasks
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