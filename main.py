from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

import models, schemas, crud
from database import engine, get_db
from auth import verify_password, create_access_token, require_teacher, require_student, get_current_user

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Student Attendance System")

# ---------- AUTH ----------
@app.post("/auth/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, user)

@app.post("/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

# ---------- TEACHER ----------
@app.post("/lectures", response_model=schemas.LectureOut)
def create_lecture(
    lecture: schemas.LectureCreate,
    db: Session = Depends(get_db),
    teacher: models.User = Depends(require_teacher),
):
    if not (1 <= lecture.period_number <= 8):
        raise HTTPException(status_code=400, detail="period_number must be 1-8")
    return crud.create_lecture(db, lecture, teacher.id)

@app.post("/attendance/mark", response_model=List[schemas.AttendanceOut])
def mark_attendance(
    req: schemas.AttendanceMarkRequest,
    db: Session = Depends(get_db),
    teacher: models.User = Depends(require_teacher),
):
    lecture = db.query(models.Lecture).filter(models.Lecture.id == req.lecture_id).first()
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    if lecture.teacher_id != teacher.id:
        raise HTTPException(status_code=403, detail="You do not teach this lecture")
    return crud.mark_attendance(db, req)

# ---------- STUDENT ----------
@app.get("/attendance/me", response_model=List[schemas.AttendanceOut])
def view_my_attendance(
    db: Session = Depends(get_db),
    student: models.User = Depends(require_student),
):
    return crud.get_student_attendance(db, student.id)

@app.get("/me", response_model=schemas.UserOut)
def read_my_profile(user: models.User = Depends(get_current_user)):
    return user