from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import models, schemas

router = APIRouter()

@router.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.get("/gyms/{gym_id}/users", response_model=list[schemas.User])
def read_gym_users(gym_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(models.User).filter(models.User.gym_id == gym_id).offset(skip).limit(limit).all()
    return users

# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from typing import List

# from app.db import schemas
# from app.db.database import get_db
# from app.core.security import get_current_user
# from gymfastapiapp.app.db import bkp_models

# router = APIRouter()

# # ------------------------------
# # Get current user profile
# # ------------------------------
# @router.get("/me", response_model=schemas.UserResponse)
# def get_my_profile(
#     db: Session = Depends(get_db),
#     current_user: bkp_models.User = Depends(get_current_user),
# ):
#     return current_user


# # ------------------------------
# # List all users (Admin only)
# # ------------------------------
# @router.get("/", response_model=List[schemas.UserResponse])
# def list_users(
#     db: Session = Depends(get_db),
#     current_user: bkp_models.User = Depends(get_current_user),
# ):
#     if not current_user.is_admin:
#         raise HTTPException(status_code=403, detail="Only admins can view all users")

#     users = db.query(bkp_models.User).all()
#     return users
