from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime
from pydantic import BaseModel
from app.database import get_db
from app.database import get_db
from app.models import Attendance, ClassSchedule, User, SectionMetadata, ProctorMeeting, Student
from sqlalchemy import func
from app.auth import admin_or_teacher, teacher_only, get_current_user, hash_password
from app.auth import admin_or_teacher, teacher_only, get_current_user, hash_password
from app.routes.admin_timetable import success_response, error_response
from app.schemas import ProctorMeetingCreate, ProctorMeetingOut
from typing import List, Optional

router = APIRouter(prefix="/teacher", tags=["Teacher"])

class PasswordChange(BaseModel):
    new_password: str

@router.post("/change-password")
def change_password(
    req: PasswordChange,
    db: Session = Depends(get_db),
    user=Depends(get_current_user) # Changed from teacher_only to debug
):
    print(f"DEBUG: change_password called by user: {user['username']}, role: {user['role']}")
    
    # Allow teachers, admins, and students to change their own password using this endpoint
    if user["role"] not in ["teacher", "admin", "student"]:
        raise HTTPException(status_code=403, detail=f"Access denied. Current role: {user['role']}")

    db_user = db.query(User).filter(User.username == user["username"]).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Optional: If admin wants to use this, we could allow it, but let's stick to teacher for now and just debug.
    
    db_user.password = hash_password(req.new_password) # IMPORTANT: Hash the password! The previous code did NOT hash it!
    db.commit()
    return {"message": "Password updated successfully"}

@router.get("/dashboard-data")
def teacher_dashboard_data(
    db: Session = Depends(get_db),
    user=Depends(admin_or_teacher)
):
    # Get current user object
    db_user = db.query(User).filter(User.id == user["id"]).first()
    
    # Check if Class Teacher
    ct_section = db.query(SectionMetadata).filter(SectionMetadata.class_teacher_id == user["id"]).first()
    is_class_teacher = ct_section is not None
    
    my_class = None
    if is_class_teacher:
        my_class = {
            "department": ct_section.department,
            "year": ct_section.year,
            "section": ct_section.section
        }
    
    # Existing logic
    # total_assigned_subjects, pending_attendance_today, assigned_subjects (list)
    # I will adapt this to match the TeacherAnalyticsDTO.kt expectation
    
    # Mocking subjects for now based on what's in ClassSchedule or Subject table
    from app.models import Subject, Student
    
    # If Admin, show ALL subjects (or maybe distinct ones?)
    if user["role"] == "admin":
         subjects_db = db.query(Subject).all()
    else:
         subjects_db = db.query(Subject).filter(Subject.teacher_id == user["id"]).all()
    
    assigned_subjects = []
    for s in subjects_db:
        # Real student count
        s_count = db.query(Student).filter(
            Student.department == s.department,
            Student.year == s.year,
            Student.section == s.section
        ).count()
        
        # Real last attendance
        last_date = db.query(func.max(Attendance.date)).filter(Attendance.subject == str(s.id)).scalar()
        
        assigned_subjects.append({
            "id": str(s.id),
            "name": s.name,
            "department": s.department,
            "year": s.year,
            "semester": s.semester,
            "section": s.section,
            "studentCount": s_count, 
            "lastAttendance": str(last_date) if last_date else None
        })

    # Calculate real pending today
    today_date = date.today()
    today_day_name = today_date.strftime("%A")
    
    if user["role"] == "admin":
        schedule_today = db.query(ClassSchedule).filter(ClassSchedule.day_of_week == today_day_name).all()
    else:
        schedule_today = db.query(ClassSchedule).filter(
            ClassSchedule.teacher_id == user["id"],
            ClassSchedule.day_of_week == today_day_name
        ).all()
        
    unique_subjects_today = set([sch.subject for sch in schedule_today])
    pending_today = 0
    for subj_id in unique_subjects_today:
        has_att = db.query(Attendance).filter(
            Attendance.subject == subj_id,
            Attendance.date == today_date
        ).first() is not None
        if not has_att:
            pending_today += 1

    return {
        "totalAssignedSubjects": len(assigned_subjects),
        "pendingAttendanceToday": pending_today,
        "assignedSubjects": assigned_subjects,
        "isHod": bool(db_user.is_hod),
        "hodDepartment": db_user.hod_department,
        "isClassTeacher": is_class_teacher,
        "myClass": my_class
    }

@router.get("/timetable")
def get_my_timetable(
    db: Session = Depends(get_db),
    user=Depends(admin_or_teacher)
):
    from app.models import User
    teacher = db.query(User).filter(User.id == user["id"]).first()
    t_name = teacher.full_name or teacher.username if teacher else user["username"]
    
    schedule = db.query(ClassSchedule).filter(ClassSchedule.teacher_id == user["id"]).all()
    
    results = []
    for s in schedule:
        s_name = s.subject # Default
        from app.models import Subject
        from sqlalchemy import or_
        subj_name_clean = s.subject.strip()
        subj = db.query(Subject).filter(
            or_(
                func.lower(Subject.name) == func.lower(subj_name_clean),
                func.lower(Subject.id) == func.lower(subj_name_clean)
            )
        ).first()
        if subj: s_name = subj.name

        results.append({
            "id": s.id,
            "department": s.department,
            "year": s.year,
            "semester": s.semester,
            "section": s.section,
            "day": s.day_of_week,
            "time": s.time_slot,
            "subject": s.subject,
            "subjectName": s_name,
            "status": s.status,
            "requestReason": s.request_reason,
            "teacher": t_name,
            "period": s.period,
            "room": s.room,
            "date": str(s.date) if s.date else None
         })
    return results

@router.get("/debug/subjects")
def debug_subjects(
    db: Session = Depends(get_db),
    user=Depends(admin_or_teacher)
):
    """Debug endpoint to see all subjects and their teachers"""
    from app.models import Subject, User
    subjects = db.query(Subject).all()
    
    result = []
    for subj in subjects:
        teacher_name = "Not Assigned"
        if subj.teacher_id:
            teacher = db.query(User).filter(User.id == subj.teacher_id).first()
            if teacher:
                teacher_name = teacher.full_name or teacher.username
        
        result.append({
            "id": subj.id,
            "name": subj.name,
            "teacher_id": subj.teacher_id,
            "teacher_name": teacher_name,
            "department": subj.department,
            "year": subj.year,
            "semester": subj.semester,
            "section": subj.section
        })
    
    return result

class MakeupClassCreate(BaseModel):
    date: date
    time_slot: str # "11:00-12:00"
    subject_id: str
    department: str
    year: int
    semester: int
    section: str
    room: str = None
    reason: str = None

@router.post("/schedule/makeup")
def create_makeup_class(
    req: MakeupClassCreate,
    db: Session = Depends(get_db),
    user=Depends(teacher_only)
):
    # Verify time format
    try:
        start, end = req.time_slot.split("-")
        datetime.strptime(start.strip(), "%H:%M")
        datetime.strptime(end.strip(), "%H:%M")
    except:
        raise HTTPException(400, "Invalid time_slot format. Use HH:MM-HH:MM")
        
    # Check for conflicts (Optional but good)
    existing = db.query(ClassSchedule).filter(
        ClassSchedule.date == req.date,
        ClassSchedule.time_slot == req.time_slot,
        ClassSchedule.room == req.room
    ).first()
    
    if existing and req.room:
        raise HTTPException(400, f"Room {req.room} is already booked at this time.")

    # Create Schedule Entry
    # day_of_week is derived from date for reference, but date field is key
    day_name = req.date.strftime("%A")
    
    new_slot = ClassSchedule(
        department=req.department,
        year=req.year,
        semester=req.semester,
        section=req.section,
        day_of_week=day_name,
        time_slot=req.time_slot,
        subject=req.subject_id,
        teacher_id=user["id"],
        period="Extra", 
        room=req.room,
        date=req.date,
        status="PENDING",
        request_reason=req.reason
    )
    db.add(new_slot)
    db.commit()
    
    db.commit()
    
    return success_response({"id": new_slot.id}, "Make-up class requested successfully. Pending approval.")

# --- Proctor Meetings ---

@router.post("/proctor/meeting", response_model=ProctorMeetingOut)
def add_proctor_meeting(req: ProctorMeetingCreate, db: Session = Depends(get_db), current_user: dict = Depends(teacher_only)):
    meeting = ProctorMeeting(
        teacher_id=current_user["id"],
        student_id=req.student_id,
        date=req.date,
        remarks=req.remarks,
        action_taken=req.action_taken
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting

@router.get("/proctor/meetings", response_model=List[ProctorMeetingOut])
def get_proctor_meetings(student_id: Optional[int] = None, db: Session = Depends(get_db), current_user: dict = Depends(teacher_only)):
    query = db.query(ProctorMeeting).filter(ProctorMeeting.teacher_id == current_user["id"])
    if student_id:
        query = query.filter(ProctorMeeting.student_id == student_id)
        
    meetings = query.all()
    # Enrich with student name
    # Enrich with student name
    for m in meetings:
        if m.student: m.student_name = m.student.name
    return meetings

# --- Section Messaging ---
# --- Section Messaging ---
from fastapi import BackgroundTasks
from app import firebase_utils
from app.schemas import SectionMessageCreate, SentMessageOut
from app.models import SentMessage, Notification

@router.get("/sent-messages", response_model=List[SentMessageOut])
def get_sent_messages(
    db: Session = Depends(get_db),
    user: dict = Depends(teacher_only)
):
    # Only get messages sent by THIS teacher
    sent_msgs = db.query(SentMessage).filter(SentMessage.sender_id == user["id"]).order_by(SentMessage.created_at.desc()).all()
    
    results = []
    for msg in sent_msgs:
        # Count notifications
        total = db.query(Notification).filter(Notification.sent_message_id == msg.id).count()
        read = db.query(Notification).filter(Notification.sent_message_id == msg.id, Notification.is_read == True).count()
        
        results.append(SentMessageOut(
            id=msg.id, content=msg.content, target_group=msg.target_group, created_at=msg.created_at,
            read_count=read, total_count=total
        ))
    return results

@router.post("/section/message")
def send_section_message(
    msg: SectionMessageCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: dict = Depends(teacher_only)
):
    # Determine Sender Name
    # Need to query User again to get full_name if not in token, but auth func usually returns token payload or dict.
    # Assuming user dict has 'full_name' or we query.
    sender_user = db.query(User).filter(User.id == user["id"]).first()
    sender_name = sender_user.full_name or sender_user.username if sender_user else "Teacher"

    # Determine Target Group
    target_desc = ""
    students = []
    
    if msg.student_id:
        # Specific Student
        student = db.query(Student).filter(Student.id == msg.student_id).first()
        if not student: raise HTTPException(404, "Student not found")
        target_desc = f"{student.name} ({student.roll_no})"
        students = [student]
    else:
        # Check if dept/year/section provided
        dept = msg.department
        year = msg.year
        sec = msg.section
        
        # Fallback to Class Teacher Section if not provided but user is CT
        if not dept:
             ct_section = db.query(SectionMetadata).filter(SectionMetadata.class_teacher_id == user["id"]).first()
             if ct_section:
                 dept = ct_section.department
                 year = ct_section.year
                 sec = ct_section.section
        
        if not dept or not year or not sec:
            raise HTTPException(400, "Please specify department, year, and section.")
            
        target_desc = f"{dept} {year} {sec}"
        students = db.query(Student).filter(
            Student.department == dept,
            Student.year == year,
            Student.section == sec
        ).all()
        
    if not students: return {"message": "No students found in target group", "recipient_count": 0}

    # Create SentMessage Record
    sent_msg = SentMessage(
        sender_id=user["id"],
        content=msg.message,
        target_group=target_desc,
        created_at=datetime.utcnow()
    )
    db.add(sent_msg)
    db.commit()
    db.refresh(sent_msg)
    
    # Create Notifications
    notifs = []
    tokens = []
    
    for student in students:
        if student.user_id:
            notifs.append(Notification(
                user_id=student.user_id,
                title=f"Message from {sender_name}",
                message=msg.message,
                created_at=datetime.utcnow(),
                metadata_json={"sender_id": user["id"], "sender_name": sender_name, "sender_role": "teacher"},
                sent_message_id=sent_msg.id
            ))
            
            u = db.query(User).filter(User.id == student.user_id).first()
            if u and u.fcm_token: tokens.append(u.fcm_token)
            
    if notifs:
        db.add_all(notifs)
        db.commit()
        
    # Push Notifications
    if tokens:
         # Exclude sender's own token if testing on single device
         if sender_user and sender_user.fcm_token:
             tokens = [tok for tok in tokens if tok != sender_user.fcm_token]
             
    if tokens:
         background_tasks.add_task(
             firebase_utils.send_multicast_notification,
             tokens=tokens,
             title=f"Message from {sender_name}",
             body=msg.message,
             data={"type": "TEACHER_MESSAGE", "sender_id": str(user["id"])}
         )
         
    return {"message": "Message sent", "recipient_count": len(notifs)}