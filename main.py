from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import TaskCreate, TaskResponse, DailySummaryResponse
from ai_engine import ai_engine
from database import get_db, TaskDB
from typing import List

app = FastAPI(title="TaskMind API", version="3.1.0")

@app.get("/tasks", response_model=List[TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(TaskDB).all()
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
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    full_text = f"{task.title} {task.description}"  
    priority = ai_engine.predict_priority(full_text)
    est_hours = ai_engine.predict_estimation(full_text) 
    subtasks = ai_engine.decompose_task(task.title, full_text)
        
    all_db_tasks = db.query(TaskDB).all()
    existing_texts = [f"{t.title} {t.description}" for t in all_db_tasks]
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
        is_completed=False
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
def toggle_task_status(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db_task.is_completed = not db_task.is_completed
    db.commit()
    return {"message": "Status updated", "is_completed": db_task.is_completed}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted successfully"}

@app.get("/daily-summary", response_model=DailySummaryResponse)
def get_daily_summary(db: Session = Depends(get_db)):
    tasks = db.query(TaskDB).all()
    total = len(tasks)
    completed = sum(1 for t in tasks if t.is_completed)
    pending = total - completed
    
    summary_md = f"### 📊 گزارش خلاصه روزانه (Daily Summary)\n"
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