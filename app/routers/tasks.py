from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.events import publish_task_event
from app.storage import save_attachment

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[schemas.TaskRead])
def list_tasks(db: Session = Depends(get_db)) -> list[models.Task]:
    return list(db.scalars(select(models.Task).order_by(models.Task.created_at.desc())))


@router.get("/stats", response_model=schemas.TaskStats)
def task_stats(db: Session = Depends(get_db)) -> schemas.TaskStats:
    total = db.scalar(select(func.count()).select_from(models.Task)) or 0
    completed = (
        db.scalar(select(func.count()).select_from(models.Task).where(models.Task.completed.is_(True)))
        or 0
    )
    open_count = total - completed
    rate = (completed / total * 100.0) if total else 0.0
    return schemas.TaskStats(
        total=total,
        completed=completed,
        open=open_count,
        completion_rate=round(rate, 2),
    )


@router.post("", response_model=schemas.TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: schemas.TaskCreate,
    db: Session = Depends(get_db),
) -> models.Task:
    task = models.Task(title=payload.title, description=payload.description)
    db.add(task)
    db.commit()
    db.refresh(task)
    publish_task_event("task.created", task.id, {"title": task.title, "completed": task.completed})
    return task


@router.post("/with-attachment", response_model=schemas.TaskRead, status_code=status.HTTP_201_CREATED)
def create_task_with_attachment(
    title: str = Form(...),
    description: str | None = Form(None),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
) -> models.Task:
    path = save_attachment(file) if file and file.filename else None
    task = models.Task(title=title, description=description, attachment_path=path)
    db.add(task)
    db.commit()
    db.refresh(task)
    publish_task_event(
        "task.created",
        task.id,
        {"title": task.title, "completed": task.completed, "has_attachment": path is not None},
    )
    return task


@router.get("/{task_id}", response_model=schemas.TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)) -> models.Task:
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=schemas.TaskRead)
def update_task(
    task_id: int,
    payload: schemas.TaskUpdate,
    db: Session = Depends(get_db),
) -> models.Task:
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)
    publish_task_event("task.updated", task.id, {"completed": task.completed, "title": task.title})
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)) -> None:
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    publish_task_event("task.deleted", task_id, {})
