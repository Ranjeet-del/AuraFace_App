import traceback
import json
from app.database import SessionLocal
from app.routes.student_routes import get_my_attendance
from app.models import Student
from fastapi.encoders import jsonable_encoder

db = SessionLocal()
s = db.query(Student).filter(Student.roll_no=="23CSE706").first()
user = {"id": s.user_id, "username": s.name, "role": "student"}

try:
    res = get_my_attendance(db, user)
    print("SUCCESS")
    print(json.dumps(jsonable_encoder(res)[:2]))
except Exception as e:
    print("ERROR:")
    traceback.print_exc()
