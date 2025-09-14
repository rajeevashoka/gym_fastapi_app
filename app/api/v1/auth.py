from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db.database import get_db
from app.db import models, schemas
from app.core.security import get_password_hash, verify_password, create_access_token
from app.utils.otp import generate_otp, send_email_otp, store_otp, verify_otp  # Import the correct function

router = APIRouter()

@router.post("/register", response_model=schemas.User)
async def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if gym exists
    db_gym = db.query(models.Gym).filter(models.Gym.id == user.gym_id).first()
    if not db_gym:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gym not found"
        )
    
    # Create user (not verified yet)
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        password=hashed_password,
        full_name=user.full_name,  # NEW
        member_id=user.member_id,  # NEW
        gym_id=user.gym_id,
        address=user.address,
        district=user.district,
        state_ut=user.state_ut,
        pincode=user.pincode,
        phone=user.phone,
        is_verified=False
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Generate and store OTP
    otp = generate_otp()
    store_otp(user.email, otp)

    # Send OTP email
    send_email_otp(user.email, otp)
    
    return db_user

@router.post("/verify-otp")
async def verify_otp_endpoint(verification: schemas.UserVerify, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == verification.email).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if db_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already verified"
        )
    
    # CORRECTED: Call verify_otp function with parameters
    if not verify_otp(verification.email, verification.otp):  # Pass email and OTP
        # Generate and store OTP
        otp = generate_otp()
        store_otp(db_user.email, otp)

        # Send OTP email
        send_email_otp(db_user.email, otp)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP/ OTP Re-sent to email"
        )
        

    # Mark user as verified
    db_user.is_verified = True
    db.commit()
    
    return {"message": "Email verified successfully"}

@router.post("/resend-otp")
async def resend_otp(request: schemas.UserResendOtp, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == request.email).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if db_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already verified"
        )
    
    # Generate and store new OTP
    otp = generate_otp()
    store_otp(request.email, otp)
    
    # Send OTP email
    send_email_otp(request.email, otp)
    
    return {"message": "OTP sent successfully"}

@router.post("/login")
async def login(user_login: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user_login.email).first()
    if not db_user or not verify_password(user_login.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not db_user.is_verified:
        # Generate and send new OTP for unverified users
        otp = generate_otp()
        store_otp(db_user.email, otp)
        send_email_otp(db_user.email, otp)
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not verified. New OTP sent to your email.",
        )
    
    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account deactivated",
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from datetime import datetime, timedelta
# from jose import jwt

# from app.db import schemas
# from app.db.database import get_db
# from app.core import security, config
# from app.utils.otp import generate_otp, send_email_otp
# from gymfastapiapp.app.db import bkp_models

# # Temporary OTP store (in production, use Redis or DB)
# otp_store = {}

# router = APIRouter()

# # -------------------------------
# # Step 1: Request OTP (User details submitted)
# # -------------------------------
# @router.post("/register-request")
# def register_request(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     # check if email already exists
#     existing = db.query(bkp_models.User).filter(bkp_models.User.email == user.email).first()
#     if existing:
#         raise HTTPException(status_code=400, detail="Email already registered")

#     # generate and store OTP
#     otp = generate_otp()
#     otp_store[user.email] = otp

#     # send OTP via email
#     send_email_otp(user.email, otp)

#     return {"message": "OTP sent to your email. Please verify."}


# # -------------------------------
# # Step 2: Verify OTP & Register User
# # -------------------------------
# class UserVerifyRequest(schemas.UserCreate):
#     otp: str

# @router.post("/register-verify")
# def register_verify(user: UserVerifyRequest, db: Session = Depends(get_db)):
#     # validate OTP
#     if user.email not in otp_store or otp_store[user.email] != user.otp:
#         raise HTTPException(status_code=400, detail="Invalid or expired OTP")

#     # hash password
#     hashed_pwd = security.hash_password(user.password)

#     # create new user
#     new_user = bkp_models.User(
#         email=user.email,
#         password=hashed_pwd,
#         phone=user.phone,
#         first_name=user.first_name,
#         middle_name=user.middle_name,
#         last_name=user.last_name,
#         gym_id=user.gym_id,
#         is_admin=False,  # members by default
#     )
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)

#     # remove OTP from store
#     del otp_store[user.email]

#     return {"message": "User registered successfully", "user_id": new_user.id}


# # -------------------------------
# # Step 3: Register Gym Owner (Admin)
# # -------------------------------
# class GymOwnerRequest(schemas.GymBase):
#     user_email: str
#     password: str
#     user_phone: str
#     first_name: str
#     middle_name: str = None
#     last_name: str
#     otp: str

# @router.post("/register-gym-owner")
# def register_gym_owner(data: GymOwnerRequest, db: Session = Depends(get_db)):
#     # validate OTP
#     if data.user_email not in otp_store or otp_store[data.user_email] != data.otp:
#         raise HTTPException(status_code=400, detail="Invalid or expired OTP")

#     # create gym first
#     new_gym = bkp_models.Gym(
#         name=data.gym_name,
#         owner_name=data.owner_name,
#         address=data.address,
#         phone=data.phone,
#         email=data.email,
#     )
#     db.add(new_gym)
#     db.commit()
#     db.refresh(new_gym)

#     # hash password
#     hashed_pwd = security.hash_password(data.password)

#     # create owner user
#     new_owner = bkp_models.User(
#         email=data.user_email,
#         password=hashed_pwd,
#         phone=data.user_phone,
#         first_name=data.first_name,
#         middle_name=data.middle_name,
#         last_name=data.last_name,
#         gym_id=new_gym.id,
#         is_admin=True,
#     )
#     db.add(new_owner)
#     db.commit()
#     db.refresh(new_owner)

#     del otp_store[data.user_email]

#     return {
#         "message": "Gym and Owner registered successfully",
#         "gym_id": new_gym.id,
#         "owner_id": new_owner.id,
#     }


# # -------------------------------
# # Step 4: Login with JWT
# # -------------------------------
# class LoginRequest(schemas.UserBase):
#     password: str

# @router.post("/login")
# def login(data: LoginRequest, db: Session = Depends(get_db)):
#     user = db.query(bkp_models.User).filter(bkp_models.User.email == data.email).first()

#     if not user or not security.verify_password(data.password, user.password):
#         raise HTTPException(status_code=401, detail="Invalid credentials")

#     if not user.is_active:
#         raise HTTPException(status_code=403, detail="User account is inactive")

#     # generate JWT
#     token_data = {
#         "sub": user.email,
#         "exp": datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES),
#     }
#     token = jwt.encode(token_data, config.SECRET_KEY, algorithm=config.ALGORITHM)

#     return {"access_token": token, "token_type": "bearer"}
