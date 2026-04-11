from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, models_placement, schemas_placement
from app.auth_dependencies import get_current_active_user
from datetime import datetime
import shutil
import os

router = APIRouter(prefix="/placement", tags=["Smart Placement Tracker"])

def get_student_id(user_id: int, db: Session):
    student = db.query(models.Student).filter(models.Student.user_id == user_id).first()
    if not student:
        raise HTTPException(status_code=400, detail="User is not a student")
    return student.id

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user: models.User = Depends(get_current_active_user)
):
    safe_filename = f"{datetime.now().timestamp()}_{file.filename}"
    file_location = f"images/placement/{safe_filename}"
    os.makedirs(os.path.dirname(file_location), exist_ok=True)
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"url": f"/images/placement/{safe_filename}", "filename": file.filename}

# --- Profile ---
@router.get("/profile", response_model=schemas_placement.StudentReadinessOut)
def get_readiness_profile(
    user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    student_id = get_student_id(user.id, db)
    
    profile = db.query(models_placement.PlacementProfile).filter_by(student_id=student_id).first()
    skills = db.query(models_placement.PlacementSkill).filter_by(student_id=student_id).all()
    certs = db.query(models_placement.PlacementCertification).filter_by(student_id=student_id).all()
    inter = db.query(models_placement.PlacementInternship).filter_by(student_id=student_id).all()
    projs = db.query(models_placement.PlacementProject).filter_by(student_id=student_id).all()
    events = db.query(models_placement.PlacementEvent).filter_by(student_id=student_id).all()
    
    # Calculate Score
    score = 0.0
    missing = []
    
    if profile and profile.resume_url: score += 20
    else: missing.append("Resume Upload")
    
    if len(skills) >= 3: score += 15
    elif len(skills) > 0: score += 5
    else: missing.append("Add at least 3 skills")
    
    if len(inter) >= 1: score += 25
    else: missing.append("Internship Experience")
    
    if len(projs) >= 2: score += 20
    else: missing.append("Minimum 2 Projects")
    
    if len(certs) >= 1: score += 10
    else: missing.append("Certification")
    
    if len(events) >= 1: score += 10
    else: missing.append("Event Participation")
    
    if score > 100: score = 100
    
    return {
        "profile": profile,
        "skills": skills,
        "certifications": certs,
        "internships": inter,
        "projects": projs,
        "events": events,
        "total_score": score,
        "missing_elements": missing
    }

@router.post("/profile", response_model=schemas_placement.PlacementProfileOut)
def update_profile(
    data: schemas_placement.PlacementProfileCreate,
    user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    student_id = get_student_id(user.id, db)
    profile = db.query(models_placement.PlacementProfile).filter_by(student_id=student_id).first()
    
    if not profile:
        profile = models_placement.PlacementProfile(student_id=student_id)
        db.add(profile)
    
    if data.linkedin_link: profile.linkedin_link = data.linkedin_link
    if data.github_link: profile.github_link = data.github_link
    if data.portfolio_link: profile.portfolio_link = data.portfolio_link
    if data.resume_url: 
        profile.resume_url = data.resume_url
        profile.resume_version += 1
        
    profile.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(profile)
    return profile

# --- Skills ---
@router.post("/skill", response_model=schemas_placement.SkillOut)
def add_skill(skill: schemas_placement.SkillCreate, user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    st_id = get_student_id(user.id, db)
    new_skill = models_placement.PlacementSkill(student_id=st_id, **skill.dict())
    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)
    return new_skill

@router.put("/skill/{item_id}", response_model=schemas_placement.SkillOut)
def edit_skill(item_id: int, item: schemas_placement.SkillCreate, user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    st_id = get_student_id(user.id, db)
    obj = db.query(models_placement.PlacementSkill).filter_by(id=item_id, student_id=st_id).first()
    if not obj: raise HTTPException(404, "Skill not found or unauthorized")
    for k, v in item.dict().items(): setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/skill/{item_id}")
def delete_skill(item_id: int, user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    st_id = get_student_id(user.id, db)
    obj = db.query(models_placement.PlacementSkill).filter_by(id=item_id, student_id=st_id).first()
    if not obj: raise HTTPException(404, "Skill not found or unauthorized")
    db.delete(obj)
    db.commit()
    return {"message": "Skill deleted successfully"}

# --- Certifications ---
@router.post("/certification", response_model=schemas_placement.CertificationOut)
def add_certification(cert: schemas_placement.CertificationCreate, user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    st_id = get_student_id(user.id, db)
    new_cert = models_placement.PlacementCertification(student_id=st_id, **cert.dict())
    db.add(new_cert)
    db.commit()
    db.refresh(new_cert)
    return new_cert

@router.put("/certification/{item_id}", response_model=schemas_placement.CertificationOut)
def edit_certification(item_id: int, item: schemas_placement.CertificationCreate, user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    st_id = get_student_id(user.id, db)
    obj = db.query(models_placement.PlacementCertification).filter_by(id=item_id, student_id=st_id).first()
    if not obj: raise HTTPException(404, "Certification not found or unauthorized")
    for k, v in item.dict().items(): setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/certification/{item_id}")
def delete_certification(item_id: int, user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    st_id = get_student_id(user.id, db)
    obj = db.query(models_placement.PlacementCertification).filter_by(id=item_id, student_id=st_id).first()
    if not obj: raise HTTPException(404, "Certification not found or unauthorized")
    db.delete(obj)
    db.commit()
    return {"message": "Certification deleted successfully"}

# --- Internships ---
@router.post("/internship", response_model=schemas_placement.InternshipOut)
def add_internship(intern: schemas_placement.InternshipCreate, user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    st_id = get_student_id(user.id, db)
    
    intern_dict = intern.dict()
    def _parse(d):
        if not d: return None
        try: return datetime.strptime(str(d)[:10], "%Y-%m-%d")
        except: return datetime.utcnow()
        
    intern_dict['start_date'] = _parse(intern_dict.get('start_date'))
    intern_dict['end_date'] = _parse(intern_dict.get('end_date')) if intern_dict.get('end_date') else None

    new_int = models_placement.PlacementInternship(student_id=st_id, **intern_dict)
    db.add(new_int)
    db.commit()
    db.refresh(new_int)
    return new_int

@router.put("/internship/{item_id}", response_model=schemas_placement.InternshipOut)
def edit_internship(item_id: int, item: schemas_placement.InternshipCreate, user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    st_id = get_student_id(user.id, db)
    obj = db.query(models_placement.PlacementInternship).filter_by(id=item_id, student_id=st_id).first()
    if not obj: raise HTTPException(404, "Internship not found or unauthorized")
    
    intern_dict = item.dict()
    def _parse(d):
        if not d: return None
        try: return datetime.strptime(str(d)[:10], "%Y-%m-%d")
        except: return datetime.utcnow()
        
    intern_dict['start_date'] = _parse(intern_dict.get('start_date'))
    intern_dict['end_date'] = _parse(intern_dict.get('end_date')) if intern_dict.get('end_date') else None

    for k, v in intern_dict.items(): setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/internship/{item_id}")
def delete_internship(item_id: int, user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    st_id = get_student_id(user.id, db)
    obj = db.query(models_placement.PlacementInternship).filter_by(id=item_id, student_id=st_id).first()
    if not obj: raise HTTPException(404, "Internship not found or unauthorized")
    db.delete(obj)
    db.commit()
    return {"message": "Internship deleted successfully"}

# --- Projects ---
@router.post("/project", response_model=schemas_placement.ProjectOut)
def add_project(proj: schemas_placement.ProjectCreate, user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    st_id = get_student_id(user.id, db)
    new_proj = models_placement.PlacementProject(student_id=st_id, **proj.dict(), approval_status="PENDING", submitted_at=datetime.utcnow())
    db.add(new_proj)
    db.commit()
    db.refresh(new_proj)
    return new_proj

@router.put("/project/{item_id}", response_model=schemas_placement.ProjectOut)
def edit_project(item_id: int, item: schemas_placement.ProjectCreate, user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    st_id = get_student_id(user.id, db)
    obj = db.query(models_placement.PlacementProject).filter_by(id=item_id, student_id=st_id).first()
    if not obj: raise HTTPException(404, "Project not found or unauthorized")
    for k, v in item.dict().items(): setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/project/{item_id}")
def delete_project(item_id: int, user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    st_id = get_student_id(user.id, db)
    obj = db.query(models_placement.PlacementProject).filter_by(id=item_id, student_id=st_id).first()
    if not obj: raise HTTPException(404, "Project not found or unauthorized")
    db.delete(obj)
    db.commit()
    return {"message": "Project deleted successfully"}

# --- Events ---
@router.post("/event", response_model=schemas_placement.EventOut)
def add_event(event: schemas_placement.EventCreate, user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    st_id = get_student_id(user.id, db)
    
    evt_dict = event.dict()
    def _parse(d):
        if not d: return None
        try: return datetime.strptime(str(d)[:10], "%Y-%m-%d")
        except: return datetime.utcnow()
        
    evt_dict['date'] = _parse(evt_dict.get('date'))

    new_evt = models_placement.PlacementEvent(student_id=st_id, **evt_dict)
    db.add(new_evt)
    db.commit()
    db.refresh(new_evt)
    return new_evt

@router.put("/event/{item_id}", response_model=schemas_placement.EventOut)
def edit_event(item_id: int, item: schemas_placement.EventCreate, user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    st_id = get_student_id(user.id, db)
    obj = db.query(models_placement.PlacementEvent).filter_by(id=item_id, student_id=st_id).first()
    if not obj: raise HTTPException(404, "Event not found or unauthorized")
    
    evt_dict = item.dict()
    def _parse(d):
        if not d: return None
        try: return datetime.strptime(str(d)[:10], "%Y-%m-%d")
        except: return datetime.utcnow()
        
    evt_dict['date'] = _parse(evt_dict.get('date'))

    for k, v in evt_dict.items(): setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/event/{item_id}")
def delete_event(item_id: int, user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    st_id = get_student_id(user.id, db)
    obj = db.query(models_placement.PlacementEvent).filter_by(id=item_id, student_id=st_id).first()
    if not obj: raise HTTPException(404, "Event not found or unauthorized")
    db.delete(obj)
    db.commit()
    return {"message": "Event deleted successfully"}
