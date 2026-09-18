from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional, List
from models import RoleEnum, AttendanceStatus

# ---------- Auth ----------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: RoleEnum
    roll_number: Optional[str] = None

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: RoleEnum
    roll_number: Optional[str] = None

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

# ---------- Lecture ----------
class LectureCreate(BaseModel):
    subject: str
    period_number: int   # 1-8
    date: date

class LectureOut(BaseModel):
    id: int
    subject: str
    period_number: int
    date: date
    teacher_id: int

    class Config:
        orm_mode = True

# ---------- Attendance ----------
class AttendanceMarkItem(BaseModel):
    student_id: int
    status: AttendanceStatus

class AttendanceMarkRequest(BaseModel):
    lecture_id: int
    records: List[AttendanceMarkItem]

class AttendanceOut(BaseModel):
    id: int
    lecture_id: int
    student_id: int
    status: AttendanceStatus

    class Config:
        orm_mode = True