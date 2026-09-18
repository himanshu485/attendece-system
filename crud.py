from sqlalchemy.orm import Session
import models, schemas
from auth import hash_password

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hash_password(user.password),
        role=user.role,
        roll_number=user.roll_number,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_lecture(db: Session, lecture: schemas.LectureCreate, teacher_id: int):
    db_lecture = models.Lecture(
        subject=lecture.subject,
        period_number=lecture.period_number,
        date=lecture.date,
        teacher_id=teacher_id,
    )
    db.add(db_lecture)
    db.commit()
    db.refresh(db_lecture)
    return db_lecture

def mark_attendance(db: Session, req: schemas.AttendanceMarkRequest):
    results = []
    for item in req.records:
        existing = db.query(models.Attendance).filter_by(
            lecture_id=req.lecture_id, student_id=item.student_id
        ).first()
        if existing:
            existing.status = item.status
        else:
            existing = models.Attendance(
                lecture_id=req.lecture_id,
                student_id=item.student_id,
                status=item.status,
            )
            db.add(existing)
        results.append(existing)
    db.commit()
    for r in results:
        db.refresh(r)
    return results

def get_student_attendance(db: Session, student_id: int):
    return db.query(models.Attendance).filter(models.Attendance.student_id == student_id).all()
    