import enum
from sqlalchemy import Column, Integer, String, Enum, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base

class RoleEnum(str, enum.Enum):
    teacher = "teacher"
    student = "student"

class AttendanceStatus(str, enum.Enum):
    present = "present"
    absent = "absent"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)

    # if role == student
    roll_number = Column(String, unique=True, nullable=True)

    lectures_taught = relationship("Lecture", back_populates="teacher")
    attendance_records = relationship("Attendance", back_populates="student")


class Lecture(Base):
    __tablename__ = "lectures"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, nullable=False)
    period_number = Column(Integer, nullable=False)   # 1 to 8
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)

    __table_args__ = (
        UniqueConstraint("period_number", "date", name="uq_period_date"),
    )

    teacher = relationship("User", back_populates="lectures_taught")
    attendance_records = relationship("Attendance", back_populates="lecture")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    lecture_id = Column(Integer, ForeignKey("lectures.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(AttendanceStatus), nullable=False)

    __table_args__ = (
        UniqueConstraint("lecture_id", "student_id", name="uq_lecture_student"),
    )

    lecture = relationship("Lecture", back_populates="attendance_records")
    student = relationship("User", back_populates="attendance_records")