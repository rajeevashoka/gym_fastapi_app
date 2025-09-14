# app/db/init_data.py
from app.db.database import SessionLocal
from app.db import models
import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_shifts():
    db = SessionLocal()
    try:
        # Check if shifts already exist
        existing_shifts = db.query(models.Shift).count()
        
        if existing_shifts == 0:
            logger.info("No shifts found. Creating default shifts...")
            
            # Create default shifts
            morning_shift = models.Shift(
                name="Morning",
                start_time=datetime.time(3, 0),    # 3:00 AM
                end_time=datetime.time(12, 59),    # 12:59 PM
                description="Morning shift from 3 AM to 12:59 PM"
            )
            
            evening_shift = models.Shift(
                name="Evening",
                start_time=datetime.time(13, 0),   # 1:00 PM
                end_time=datetime.time(23, 59),    # 11:59 PM
                description="Evening shift from 1 PM to 11:59 PM"
            )
            
            db.add(morning_shift)
            db.add(evening_shift)
            db.commit()
            logger.info("Default shifts created successfully")
            
            return True
        else:
            logger.info(f"Shifts already exist ({existing_shifts} shifts found)")
            return False
            
    except Exception as e:
        logger.error(f"Error creating shifts: {e}")
        db.rollback()
        return False
    finally:
        db.close()

# You can keep this for manual execution
if __name__ == "__main__":
    init_shifts()