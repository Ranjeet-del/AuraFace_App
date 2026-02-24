from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Attendance, Student, ClassSchedule
from app.auth import admin_only

from app.models import LeaveRequest
from sqlalchemy import func
from app.models import Attendance


router = APIRouter(prefix="/admin/charts", tags=["Admin Charts"])

@router.get("/overview")
def attendance_overview(
    db: Session = Depends(get_db),
    user=Depends(admin_only)
):
    total_students = db.query(Student).count()
    total_classes = db.query(ClassSchedule).count()
    total_attendance = db.query(Attendance).count()

    overall_percentage = (
        (total_attendance / (total_students * total_classes)) * 100
        if total_students and total_classes else 0
    )

    return {
        "total_students": total_students,
        "total_classes": total_classes,
        "attendance_marked": total_attendance,
        "overall_percentage": round(overall_percentage, 2)
    }

@router.get("/subject-wise")
def subject_wise_attendance(
    db: Session = Depends(get_db),
    user=Depends(admin_only)
):
    data = db.query(
        Attendance.subject,
        func.count(Attendance.id)
    ).group_by(Attendance.subject).all()

    return {
        "subjects": [d[0] for d in data],
        "attendance_count": [d[1] for d in data]
    }

@router.get("/daily")
def daily_attendance(
    db: Session = Depends(get_db),
    user=Depends(admin_only)
):
    data = db.query(
        Attendance.date,
        func.count(Attendance.id)
    ).group_by(Attendance.date).order_by(Attendance.date).all()

    return {
        "dates": [str(d[0]) for d in data],
        "attendance": [d[1] for d in data]
    }

@router.get("/department-year")
def department_year_attendance(
    db: Session = Depends(get_db),
    user=Depends(admin_only)
):
    data = db.query(
        Student.department,
        Student.year,
        func.count(Attendance.id)
    ).join(
        Attendance, Attendance.student_id == Student.id
    ).group_by(
        Student.department, Student.year
    ).all()

    result = {}
    for dept, year, count in data:
        key = f"{dept} - Year {year}"
        result[key] = count

    return result

@router.get("/leaves")
def leave_statistics(
    db: Session = Depends(get_db),
    user=Depends(admin_only)
):
    approved = db.query(LeaveRequest).filter(
        LeaveRequest.status == "Approved"
    ).count()

    rejected = db.query(LeaveRequest).filter(
        LeaveRequest.status == "Rejected"
    ).count()

    pending = db.query(LeaveRequest).filter(
        LeaveRequest.status == "Pending"
    ).count()

    return {
        "approved": approved,
        "rejected": rejected,
        "pending": pending
    }

from sqlalchemy import case

@router.get("/defaulters")
def defaulter_count(
    db: Session = Depends(get_db),
    user=Depends(admin_only)
):
    # Calculate attendance per student
    # Note: SQLite bool sum trickery or Case
    stmt = db.query(
        Attendance.student_id,
        func.count(Attendance.id).label('total'),
        func.sum(case((Attendance.status == 'Present', 1), else_=0)).label('present')
    ).group_by(Attendance.student_id).all()
    
    defaulters = 0
    safe = 0
    
    for _, total, present in stmt:
        if total > 0:
            pct = present / total
            if pct < 0.75:
                defaulters += 1
            else:
                safe += 1
                
    return {"defaulters": defaulters, "safe": safe}

@router.get("/most-absent")
def most_absent_subject(
    db: Session = Depends(get_db),
    user=Depends(admin_only)
):
    # Calculate average attendance % per subject
    stmt = db.query(
        Attendance.subject,
        func.count(Attendance.id).label('total'),
        func.sum(case((Attendance.status == 'Present', 1), else_=0)).label('present')
    ).group_by(Attendance.subject).all()
    
    result = []
    for subj, total, present in stmt:
        pct = (present/total)*100 if total > 0 else 0
        result.append({"subject": subj, "percentage": round(pct, 2)})
        
    # Sort ascending (lowest attendance first)
    result.sort(key=lambda x: x['percentage'])
    
    return result[:5] # Top 5 worst subjects


