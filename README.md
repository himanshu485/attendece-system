# Student Attendance Management System

A backend service to track student attendance across 8 daily lectures, built with **FastAPI** and **PostgreSQL**. Teachers can mark students present or absent for the lectures they teach, and students can view only their own attendance records. All endpoints are secured with JWT-based, role-based authentication and tested via **Postman**.

## Features

- Role-based access control — **Teacher** and **Student** roles
- Track attendance across **8 lectures/day**, each identified by a `period_number` (1–8)
- Different teachers can own different lectures
- Teachers mark students **present** or **absent** per lecture
- Students can view **only their own** attendance history
- Passwords hashed with **bcrypt** — never stored in plain text
- JWT access tokens for stateless authentication
- PostgreSQL persistence via SQLAlchemy ORM
- Fully testable via Postman — no UI required

## Tech Stack

| Layer | Technology |
|---|---|
| Language / Framework | Python 3.12, FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Auth | JWT (python-jose), bcrypt (passlib) |
| Server | Uvicorn |
| API Testing | Postman |

## Project Structure

```
attendance-system/
├── database.py      # SQLAlchemy engine & session setup
├── models.py         # ORM models: User, Lecture, Attendance
├── schemas.py         # Pydantic request/response schemas
├── auth.py            # Password hashing, JWT creation & role guards
├── crud.py             # Database operations
├── main.py              # FastAPI route definitions
├── requirements.txt
├── .env.example
└── README.md
```

## Database Schema

**users**
| Column | Type | Notes |
|---|---|---|
| id | int, PK | |
| name | string | |
| email | string | unique |
| hashed_password | string | bcrypt hash |
| role | enum | `teacher` \| `student` |
| roll_number | string | students only |

**lectures**
| Column | Type | Notes |
|---|---|---|
| id | int, PK | |
| subject | string | |
| period_number | int | 1–8 |
| date | date | |
| teacher_id | int, FK → users.id | |

Unique constraint on `(period_number, date)` — one lecture per period per day.

**attendance**
| Column | Type | Notes |
|---|---|---|
| id | int, PK | |
| lecture_id | int, FK → lectures.id | |
| student_id | int, FK → users.id | |
| status | enum | `present` \| `absent` |

Unique constraint on `(lecture_id, student_id)` — one record per student per lecture.

## Setup Instructions

### 1. Prerequisites

- Python 3.9+
- PostgreSQL installed and running

### 2. Clone and set up the virtual environment

```bash
git clone <your-repo-url>
cd attendance-system
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Create the PostgreSQL database and user

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE attendance_db;
CREATE USER attendance_user WITH PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE attendance_db TO attendance_user;
\c attendance_db
GRANT ALL ON SCHEMA public TO attendance_user;
\q
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and fill in your own values — **never commit `.env` to GitHub**, it's already excluded via `.gitignore`.

```bash
cp .env.example .env
```

```
DATABASE_URL=postgresql://<db_user>:<db_password>@localhost:5432/attendance_db
SECRET_KEY=<generate-a-long-random-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120
```

> Generate a strong `SECRET_KEY` with: `python3 -c "import secrets; print(secrets.token_hex(32))"`

### 5. Run the server

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`, with interactive docs at `http://127.0.0.1:8000/docs`.

## API Endpoints

| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/auth/register` | Public | Register a new teacher or student |
| POST | `/auth/login` | Public | Log in and receive a JWT access token |
| GET | `/me` | Authenticated | View own profile |
| POST | `/lectures` | Teacher | Create a lecture for a period (1–8) and date |
| POST | `/attendance/mark` | Teacher | Mark present/absent for students in a lecture they own |
| GET | `/attendance/me` | Student | View own attendance records |

### Example — Register

```http
POST /auth/register
Content-Type: application/json

{
  "name": "Mr. Sharma",
  "email": "sharma@school.com",
  "password": "teacher123",
  "role": "teacher"
}
```

### Example — Login

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=sharma@school.com&password=teacher123
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Example — Create Lecture

```http
POST /lectures
Authorization: Bearer <teacher_token>
Content-Type: application/json

{
  "subject": "Mathematics",
  "period_number": 1,
  "date": "2026-09-08"
}
```

### Example — Mark Attendance

```http
POST /attendance/mark
Authorization: Bearer <teacher_token>
Content-Type: application/json

{
  "lecture_id": 1,
  "records": [
    { "student_id": 3, "status": "present" },
    { "student_id": 4, "status": "absent" }
  ]
}
```

### Example — View My Attendance

```http
GET /attendance/me
Authorization: Bearer <student_token>
```

## Testing with Postman

A ready-to-import Postman collection is included: [`Attendance_System.postman_collection.json`](./Attendance_System.postman_collection.json).

**To import:**
1. Open Postman → **Import** → select the JSON file.
2. The collection includes 3 folders: **Auth**, **Lectures**, **Attendance**.
3. Run requests top to bottom — login requests auto-save tokens into collection variables (`teacher_token`, `teacher2_token`, `student_token`), so no manual copy-pasting is required.
4. Update the `base_url` collection variable if your server runs on a different host/port than `http://127.0.0.1:8000`.

## Security Notes

- Passwords are hashed with bcrypt before storage — plain-text passwords are never persisted.
- JWT tokens expire after `ACCESS_TOKEN_EXPIRE_MINUTES` (default 120 minutes).
- Teachers can only mark attendance for lectures they created (enforced server-side).
- Students can only ever retrieve their own attendance — the `student_id` is derived from their authenticated token, never taken from client input.

## Future Enhancements

- `GET /lectures` — list the full day's schedule
- Teacher-facing endpoint to view attendance already marked for a specific lecture
- Automated test coverage via Postman scripts/Newman CLI in CI
- Attendance percentage/summary reports per student

## License

This project was built as part of a backend development task assignment.
