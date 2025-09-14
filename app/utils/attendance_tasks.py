# app/utils/attendance_tasks.py
from app.db.database import SessionLocal
from app.db import models
import datetime
import pytz

INDIAN_TIMEZONE = pytz.timezone('Asia/Kolkata')

def get_current_indian_time():
    return datetime.datetime.now(INDIAN_TIMEZONE)

def mark_absent_users():
    """Mark users as absent who didn't record attendance"""
    db = SessionLocal()
    try:
        today = get_current_indian_time().date()
        
        # Get all active users
        active_users = db.query(models.User).filter(
            models.User.is_active == True,
            models.User.is_verified == True
        ).all()
        
        for user in active_users:
            # Check if user has attendance for today
            attendance_exists = db.query(models.Attendance).filter(
                models.Attendance.user_id == user.id,
                models.Attendance.attendance_date == today
            ).first()
            
            if not attendance_exists:
                # Get all active shifts
                shifts = db.query(models.Shift).filter(models.Shift.is_active == True).all()
                
                for shift in shifts:
                    # Create absent record for each shift
                    absent_attendance = models.Attendance(
                        user_id=user.id,
                        shift_id=shift.id,
                        attendance_date=today,
                        status='A'  # Absent
                    )
                    db.add(absent_attendance)
        
        db.commit()
        print(f"Absent users marked for {today}")
        
    except Exception as e:
        print(f"Error marking absent users: {e}")
        db.rollback()
    finally:
        db.close()

def set_default_timeout():
    """Set default timeout for users who forgot to check out"""
    db = SessionLocal()
    try:
        today = get_current_indian_time().date()
        
        # Find attendances with time_in but no time_out
        incomplete_attendances = db.query(models.Attendance).filter(
            models.Attendance.attendance_date == today,
            models.Attendance.time_in.isnot(None),
            models.Attendance.time_out.is_(None),
            models.Attendance.timeout_default == False
        ).all()
        
        for attendance in incomplete_attendances:
            # Check if it's been more than 1 hour since time_in
            current_time = get_current_indian_time()
            
            if current_time - attendance.time_in > datetime.timedelta(hours=1):
                attendance.time_out = attendance.time_in + datetime.timedelta(hours=1)
                attendance.timeout_default = True
                print(f"Set default timeout for user {attendance.user_id}")
        
        db.commit()
        
    except Exception as e:
        print(f"Error setting default timeout: {e}")
        db.rollback()
    finally:
        db.close()