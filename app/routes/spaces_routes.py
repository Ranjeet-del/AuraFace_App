from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth_dependencies import get_current_active_user as get_current_user
from app.models import User
from app.models_campus import FacilitySpace, SpaceBooking
import random

router = APIRouter(prefix="/spaces", tags=["Aura Spaces (Facility Booking)"])

class SpaceItem(BaseModel):
    id: str
    name: str
    type: str # "Study Room", "Lab Equipment", "Hall", "Sports"
    capacity: int
    is_available: bool
    next_available_time: Optional[str] = None
    icon_emoji: str
    location: str

class BookingRequest(BaseModel):
    space_id: str
    date: str # YYYY-MM-DD
    time_slot: str # e.g., "10:00 AM - 11:00 AM"
    purpose: str

class BookingResponse(BaseModel):
    booking_id: str
    space_name: str
    date: str
    time_slot: str
    status: str
    message: str

class MyBookingOut(BaseModel):
    id: str
    space_name: str
    type: str
    date: str
    time_slot: str
    status: str # "CONFIRMED", "COMPLETED", "CANCELLED"
    icon_emoji: str

INITIAL_SPACES = [
    {"id": "sr-1", "name": "Alpha Discussion Room", "type": "Study Room", "capacity": 6, "is_available": True, "icon_emoji": "📚", "location": "Library 2nd Floor"},
    {"id": "sr-2", "name": "Beta Quiet Zone", "type": "Study Room", "capacity": 4, "is_available": False, "next_available_time": "02:00 PM", "icon_emoji": "🤫", "location": "Library 3rd Floor"},
    {"id": "lab-1", "name": "MakerSpace 3D Printer", "type": "Lab Equipment", "capacity": 1, "is_available": True, "icon_emoji": "🖨️", "location": "Tech Block, Rm 102"},
    {"id": "hall-1", "name": "Mini Presentation Hall", "type": "Hall", "capacity": 30, "is_available": False, "next_available_time": "04:00 PM", "icon_emoji": "📽️", "location": "Main Block, Rm 405"},
    {"id": "gym-1", "name": "Badminton Court 1", "type": "Sports", "capacity": 4, "is_available": True, "icon_emoji": "🏸", "location": "Sports Complex"},
]

@router.get("/list", response_model=List[SpaceItem])
def get_spaces(db: Session = Depends(get_db)):
    spaces = db.query(FacilitySpace).all()
    if not spaces:
        for s in INITIAL_SPACES:
            db.add(FacilitySpace(**s))
        db.commit()
        spaces = db.query(FacilitySpace).all()
    return [SpaceItem(**{col.name: getattr(sp, col.name) for col in sp.__table__.columns}) for sp in spaces]

@router.post("/book", response_model=BookingResponse)
def book_space(req: BookingRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    space = db.query(FacilitySpace).filter(FacilitySpace.id == req.space_id).first()
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")
        
    if not space.is_available:
        raise HTTPException(status_code=400, detail="Space is currently booked. Check next available time.")
        
    booking_id = f"BKG-{random.randint(10000, 99999)}"
    new_booking = SpaceBooking(
        id=booking_id,
        user_id=current_user.id,
        space_id=space.id,
        date=req.date,
        time_slot=req.time_slot,
        purpose=req.purpose,
        status="CONFIRMED"
    )
    db.add(new_booking)
    # Optional logic to set space as not available for realism
    # space.is_available = False # skipping to allow multiple mock bookings in demo
    db.commit()
        
    return BookingResponse(
        booking_id=booking_id,
        space_name=space.name,
        date=req.date,
        time_slot=req.time_slot,
        status="CONFIRMED",
        message="Booking confirmed! Please tap your Digital ID at the venue scanner."
    )

@router.get("/my-bookings", response_model=List[MyBookingOut])
def get_my_bookings(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bookings = db.query(SpaceBooking).filter(SpaceBooking.user_id == current_user.id).order_by(SpaceBooking.created_at.desc()).all()
    out = []
    for b in bookings:
        space = db.query(FacilitySpace).filter(FacilitySpace.id == b.space_id).first()
        out.append(MyBookingOut(
            id=b.id,
            space_name=space.name if space else "Unknown Space",
            type=space.type if space else "Unknown",
            date=b.date,
            time_slot=b.time_slot,
            status=b.status,
            icon_emoji=space.icon_emoji if space else "🚪"
        ))
    return out
