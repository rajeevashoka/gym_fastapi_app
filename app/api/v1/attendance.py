# app/api/v1/attendance.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import datetime 
from datetime import date
from typing import List, Optional
import pytz

from app.db.database import get_db
from app.db import models, schemas
from app.core.security import get_current_user

router = APIRouter()

# Indian timezone
INDIAN_TIMEZONE = pytz.timezone('Asia/Kolkata')

def get_current_indian_time():
    return datetime.datetime.now(INDIAN_TIMEZONE)

# Helper functions for time conversion
def time_to_string(time_obj):
    """Convert time object to string for API response"""
    if time_obj:
        return time_obj.strftime("%H:%M:%S")
    return None

def get_current_shift(db: Session):
    """Get current active shift based on Indian time"""
    current_time = get_current_indian_time().time()
    
    shift = db.query(models.Shift).filter(
        models.Shift.is_active == True,
        models.Shift.start_time <= current_time,
        models.Shift.end_time >= current_time
    ).first()
    
    return shift

def get_shift_by_time(check_time: datetime.time, db: Session):
    """Get shift for a specific time"""
    shift = db.query(models.Shift).filter(
        models.Shift.is_active == True,
        models.Shift.start_time <= check_time,
        models.Shift.end_time >= check_time
    ).first()
    
    return shift

@router.post("/attendance/time-in", response_model=schemas.AttendanceResponse)
async def record_time_in(
    attendance_data: schemas.AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Use current date if not provided
    attendance_date = attendance_data.attendance_date or get_current_indian_time().date()
    
    # Check if shift exists and is active
    shift = db.query(models.Shift).filter(
        models.Shift.id == attendance_data.shift_id,
        models.Shift.is_active == True
    ).first()
    
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected shift is not available"
        )
    
    # Check if attendance already exists for today and shift
    existing_attendance = db.query(models.Attendance).filter(
        models.Attendance.user_id == current_user.id,
        models.Attendance.attendance_date == attendance_date,
        models.Attendance.shift_id == attendance_data.shift_id
    ).first()
    
    current_time = get_current_indian_time()
    
    if existing_attendance:
        if existing_attendance.time_in:
            return {
                "message": "Time-in already recorded for this shift",
                "attendance": existing_attendance,
                "already_recorded": True
            }
        else:
            # Update existing record with time_in
            existing_attendance.time_in = current_time
            existing_attendance.status = 'P'
            db.commit()
            db.refresh(existing_attendance)
            
            return {
                "message": "Time-in recorded successfully",
                "attendance": existing_attendance
            }
    else:
        # Create new attendance record
        attendance = models.Attendance(
            user_id=current_user.id,
            shift_id=attendance_data.shift_id,
            attendance_date=attendance_date,
            time_in=current_time,
            status='P'
        )
        
        db.add(attendance)
        db.commit()
        db.refresh(attendance)
        
        return {
            "message": "Time-in recorded successfully",
            "attendance": attendance
        }

@router.post("/attendance/time-out", response_model=schemas.AttendanceResponse)
async def record_time_out(
    attendance_data: schemas.AttendanceUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    current_date = get_current_indian_time().date()
    
    # Get current shift based on time_out or current time
    if attendance_data.time_out:
        time_out_dt = attendance_data.time_out
        if time_out_dt.tzinfo is None:
            time_out_dt = INDIAN_TIMEZONE.localize(time_out_dt)
        check_time = time_out_dt.time()
    else:
        check_time = get_current_indian_time().time()
    
    shift = get_shift_by_time(check_time, db)
    
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active shift found for the current time"
        )
    
    # Find attendance record
    attendance = db.query(models.Attendance).filter(
        models.Attendance.user_id == current_user.id,
        models.Attendance.attendance_date == current_date,
        models.Attendance.shift_id == shift.id
    ).first()
    
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No attendance record found for time-out"
        )
    
    if not attendance.time_in:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Time-in not recorded for this shift"
        )
    
    if attendance.time_out:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Time-out already recorded for this shift"
        )
    
    # Update time_out
    attendance.time_out = attendance_data.time_out or get_current_indian_time()
    db.commit()
    db.refresh(attendance)
    
    return {
        "message": "Time-out recorded successfully",
        "attendance": attendance
    }

@router.get("/attendance/today", response_model=List[schemas.Attendance])
async def get_today_attendance(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    current_date = get_current_indian_time().date()
    
    attendances = db.query(models.Attendance).filter(
        models.Attendance.user_id == current_user.id,
        models.Attendance.attendance_date == current_date
    ).all()
    
    return attendances

# In your attendance.py, update the shift endpoints:
@router.get("/attendance/shifts", response_model=List[schemas.ShiftResponse])
async def get_active_shifts(db: Session = Depends(get_db)):
    shifts = db.query(models.Shift).filter(models.Shift.is_active == True).all()
    
    # Convert time objects to strings for response
    shift_responses = []
    for shift in shifts:
        shift_responses.append({
            "id": shift.id,
            "name": shift.name,
            "start_time": shift.start_time.strftime("%H:%M:%S") if shift.start_time else None,
            "end_time": shift.end_time.strftime("%H:%M:%S") if shift.end_time else None,
            "is_active": shift.is_active,
            "description": shift.description
        })
    
    return shift_responses

@router.get("/attendance/current-shift", response_model=schemas.ShiftResponse)
async def get_current_shift_endpoint(db: Session = Depends(get_db)):
    shift = get_current_shift(db)
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active shift at the moment"
        )
    
    # Convert time objects to strings for response
    shift_response = {
        "id": shift.id,
        "name": shift.name,
        "start_time": shift.start_time.strftime("%H:%M:%S") if shift.start_time else None,
        "end_time": shift.end_time.strftime("%H:%M:%S") if shift.end_time else None,
        "is_active": shift.is_active,
        "description": shift.description
    }
    
    return shift_response

@router.get("/attendance/history", response_model=List[schemas.Attendance])
async def get_attendance_history(
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    query = db.query(models.Attendance).filter(
        models.Attendance.user_id == current_user.id
    )
    
    if start_date:
        query = query.filter(models.Attendance.attendance_date >= start_date)
    if end_date:
        query = query.filter(models.Attendance.attendance_date <= end_date)
    
    return query.order_by(models.Attendance.attendance_date.desc()).all()

@router.put("/attendance/{attendance_id}", response_model=schemas.Attendance)
async def update_attendance(
    attendance_id: int,
    attendance_data: schemas.AttendanceUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Find attendance record
    attendance = db.query(models.Attendance).filter(
        models.Attendance.id == attendance_id,
        models.Attendance.user_id == current_user.id
    ).first()
    
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )
    
    # Update time_out if provided
    if attendance_data.time_out:
        attendance.time_out = attendance_data.time_out
    
    db.commit()
    db.refresh(attendance)
    
    return attendance

@router.get("/attendance/stats/monthly", response_model=dict)
async def get_monthly_stats(
    year: int = None,
    month: int = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Use current year/month if not provided
    now = get_current_indian_time()
    year = year or now.year
    month = month or now.month
    
    # Calculate start and end dates for the month
    start_date = datetime.date(year, month, 1)
    if month == 12:
        end_date = datetime.date(year + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        end_date = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
    
    # Get attendance records for the month
    attendances = db.query(models.Attendance).filter(
        models.Attendance.user_id == current_user.id,
        models.Attendance.attendance_date >= start_date,
        models.Attendance.attendance_date <= end_date
    ).all()
    
    # Calculate stats
    total_days = (end_date - start_date).days + 1
    present_days = sum(1 for a in attendances if a.status == 'P')
    absent_days = total_days - present_days
    
    return {
        "year": year,
        "month": month,
        "total_days": total_days,
        "present_days": present_days,
        "absent_days": absent_days,
        "attendance_rate": round((present_days / total_days) * 100, 2) if total_days > 0 else 0
    }


#--------------------------
# Admin endpoints for attendance management
# Add these endpoints to your attendance.py
@router.post("/attendance/admin", response_model=schemas.Attendance)
async def create_attendance_admin(
    attendance_data: schemas.AttendanceCreateAdmin,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    print(f"Current user: {current_user.email}, is_owner: {current_user.is_owner}, is_trainer: {current_user.is_trainer}")
    print(f"Attendance data: {attendance_data}")
    if not current_user.is_owner and not current_user.is_trainer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners and trainers can create attendance records"
        )
    
    # Check if attendance already exists
    existing_attendance = db.query(models.Attendance).filter(
        models.Attendance.user_id == attendance_data.user_id,
        models.Attendance.attendance_date == attendance_data.attendance_date,
        models.Attendance.shift_id == attendance_data.shift_id
    ).first()
    
    if existing_attendance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attendance record already exists for this user, date, and shift"
        )
    
    # Create new attendance record
    attendance = models.Attendance(
        user_id=attendance_data.user_id,
        shift_id=attendance_data.shift_id,
        attendance_date=attendance_data.attendance_date,
        time_in=attendance_data.time_in,
        time_out=attendance_data.time_out,
        status=attendance_data.status
    )
    
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    
    return attendance

@router.get("/attendance/admin", response_model=List[schemas.Attendance])
async def get_attendance_admin(
    date: date = None,
    user_id: int = None,
    shift_id: int = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get attendance records with optional filtering"""
    # Check if user has permission
    if not current_user.is_owner and not current_user.is_trainer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners and trainers can access attendance data"
        )
    
    # Build query
    query = db.query(models.Attendance)
    
    # Apply filters
    if date:
        query = query.filter(models.Attendance.attendance_date == date)
    if user_id:
        query = query.filter(models.Attendance.user_id == user_id)
    if shift_id:
        query = query.filter(models.Attendance.shift_id == shift_id)
    
    # Execute query
    attendances = query.order_by(models.Attendance.attendance_date.desc()).all()
    
    return attendances

@router.put("/attendance/admin/{attendance_id}", response_model=schemas.Attendance)
async def update_attendance_admin(
    attendance_id: int,
    attendance_data: schemas.AttendanceUpdateAdmin,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_owner and not current_user.is_trainer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners and trainers can update attendance records"
        )
    
    attendance = db.query(models.Attendance).filter(models.Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )
    
    # Update fields
    if attendance_data.time_in is not None:
        attendance.time_in = attendance_data.time_in
    if attendance_data.time_out is not None:
        attendance.time_out = attendance_data.time_out
    if attendance_data.status is not None:
        attendance.status = attendance_data.status
    
    db.commit()
    db.refresh(attendance)
    
    return attendance

@router.get("/attendance/admin/{attendance_id}", response_model=schemas.Attendance)
async def get_attendance_by_id(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_owner and not current_user.is_trainer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners and trainers can access attendance data"
        )
    
    attendance = db.query(models.Attendance).filter(models.Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )
    
    return attendance

# Temporary fix - remove authentication for development
# In app/api/v1/attendance.py, replace all instances of:
# current_user: models.User = Depends(get_current_user)
# with:
# current_user: models.User = None

# And add this at the top of each function:
# if current_user is None:
#     # For development only - get first user
#     current_user = db.query(models.User).first()
#     if not current_user:
#         raise HTTPException(status_code=404, detail="No users found")