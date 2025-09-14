from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import models, schemas

router = APIRouter()

@router.post("/gyms/", response_model=schemas.Gym)
def create_gym(gym: schemas.GymCreate, db: Session = Depends(get_db)):
    # Generate a unique gymID (you might want to use a more sophisticated method)
    import uuid
    gymID = str(uuid.uuid4())[:8].upper()
    
    db_gym = models.Gym(
        gym_name=gym.gym_name,
        gymID=gymID,
        address=gym.address,
        district=gym.district,
        state_ut=gym.state_ut,
        pincode=gym.pincode,
        country=gym.country
    )
    
    db.add(db_gym)
    db.commit()
    db.refresh(db_gym)
    return db_gym

@router.get("/gyms/", response_model=list[schemas.Gym])
def read_gyms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    gyms = db.query(models.Gym).offset(skip).limit(limit).all()
    return gyms

@router.get("/gyms/{gym_id}", response_model=schemas.Gym)
def read_gym(gym_id: int, db: Session = Depends(get_db)):
    db_gym = db.query(models.Gym).filter(models.Gym.id == gym_id).first()
    if db_gym is None:
        raise HTTPException(status_code=404, detail="Gym not found")
    return db_gym

# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from typing import List

# from app.db import schemas
# from app.db.database import get_db
# from app.core.security import get_current_user
# from gymfastapiapp.app.db import bkp_models

# router = APIRouter()

# # ------------------------------
# # Create a new Gym (Admin only)
# # ------------------------------
# @router.post("/", response_model=schemas.GymResponse)
# def create_gym(
#     gym: schemas.GymCreate,
#     db: Session = Depends(get_db),
#     current_user: bkp_models.User = Depends(get_current_user),
# ):
#     if not current_user.is_admin:
#         raise HTTPException(status_code=403, detail="Only admins can create gyms")

#     db_gym = bkp_models.Gym(
#         gym_name=gym.gym_name,
#         owner_name=gym.owner_name,
#         address=gym.address,
#         phone=gym.phone,
#         email=gym.email,
#     )
#     db.add(db_gym)
#     db.commit()
#     db.refresh(db_gym)

#     return db_gym


# # ------------------------------
# # List all gyms
# # ------------------------------
# @router.get("/", response_model=List[schemas.GymResponse])
# def list_gyms(db: Session = Depends(get_db)):
#     gyms = db.query(bkp_models.Gym).all()
#     return gyms
