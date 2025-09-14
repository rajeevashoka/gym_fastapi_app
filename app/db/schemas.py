from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime, date, time
from typing import Optional

# State and Country schemas
class StateCountryBase(BaseModel):
    state_name: str
    country_name: str

class StateCountryCreate(StateCountryBase):
    pass

class StateCountry(StateCountryBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

# Pincode schemas
class PincodeBase(BaseModel):
    pincode: str
    state_country_id: int

class PincodeCreate(PincodeBase):
    pass

class Pincode(PincodeBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

# Gym schemas
class GymBase(BaseModel):
    gym_name: str
    address: str
    district: str
    state_ut: str
    pincode: str
    country: str

class GymCreate(GymBase):
    pass

class Gym(GymBase):
    id: int
    gymID: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str  # NEW: Mandatory full name
    member_id: int  # NEW: Unique member ID
    address: Optional[str] = None
    district: Optional[str] = None
    state_ut: Optional[str] = None
    pincode: str  # UPDATED: Mandatory, exactly 6 digits
    phone: Optional[str] = None  # UPDATED: 10 digits only, can be null

class UserCreate(UserBase):
    password: str
    gym_id: int

class UserVerify(BaseModel):
    email: EmailStr
    otp: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    gym_id: int
    created_at: datetime
    is_member: bool
    is_trainer: bool
    is_owner: bool
    is_active: bool
    is_verified: bool
    
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResendOtp(BaseModel):
    email: EmailStr

# Attendance Schemas
class ShiftBase(BaseModel):
    name: str
    start_time: str  # Store as string
    end_time: str    # Store as string
    is_active: bool = True
    description: Optional[str] = None

class ShiftCreate(ShiftBase):
    pass

class Shift(ShiftBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

class ShiftResponse(BaseModel):
    id: int
    name: str
    start_time: str
    end_time: str
    is_active: bool
    description: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class AttendanceBase(BaseModel):
    shift_id: int
    attendance_date: Optional[date] = None

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceUpdate(BaseModel):
    time_out: Optional[datetime] = None

class Attendance(AttendanceBase):
    id: int
    user_id: int
    time_in: Optional[datetime] = None
    time_out: Optional[datetime] = None
    status: str
    timeout_default: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class AttendanceResponse(BaseModel):
    message: str
    attendance: Optional[Attendance] = None
    already_recorded: bool = False

class AttendanceCreateAdmin(BaseModel):
    user_id: int
    shift_id: int
    attendance_date: date
    time_in: Optional[datetime] = None
    time_out: Optional[datetime] = None
    status: str = 'A'

class AttendanceUpdateAdmin(BaseModel):
    time_in: Optional[datetime] = None
    time_out: Optional[datetime] = None
    status: Optional[str] = None

# from pydantic import BaseModel, EmailStr
# from typing import Optional
# from datetime import datetime

# # ------------------------------
# # Gym Schemas
# # ------------------------------
# class GymBase(BaseModel):
#     gym_name: str
#     owner_name: str
#     address: str
#     phone: str
#     email: Optional[EmailStr] = None

# class GymCreate(GymBase):
#     pass

# class GymResponse(GymBase):
#     id: int
#     created_at: datetime

#     model_config = {
#         "from_attributes": True
#     }

# # ------------------------------
# # User Schemas
# # ------------------------------
# class UserBase(BaseModel):
#     email: EmailStr
#     phone: str
#     first_name: str
#     middle_name: Optional[str] = None
#     last_name: str

# # ✅ For Gym Owner registration (Gym + User together)
# class OwnerCreate(UserBase):
#     password: str
#     gym: GymCreate

# # ✅ For Gym Members (must belong to an existing Gym)
# class MemberCreate(UserBase):
#     password: str
#     gym_id: int  # required for members

# # ✅ Response for any User
# class UserResponse(UserBase):
#     id: int
#     is_active: bool
#     is_admin: bool
#     created_at: datetime
#     gym_id: int

#     model_config = {
#         "from_attributes": True
#     }

# # ✅ For Gym Owner registration (Gym + User together)
# class UserCreate(UserBase):
#     password: str
#     gym_id: Optional[int] = None   # FK reference (can be null for owner) # Gym reference (required for members, optional for owner)

# class UserResponse(UserBase):
#     id: int
#     is_active: bool
#     is_admin: bool
#     created_at: datetime
#     gym_id: Optional[int]

#     model_config = {
#         "from_attributes": True
#     }

# # ------------------------------
# # Auth & OTP Schemas
# # ------------------------------
# class RegisterRequest(BaseModel):
#     email: EmailStr
#     phone: str

# class VerifyOtpRequest(BaseModel):
#     email: EmailStr
#     otp: str

# class RegisterGymOwnerRequest(BaseModel):
#     email: EmailStr
#     otp: str
#     password: str
#     first_name: str
#     middle_name: Optional[str] = None
#     last_name: str
#     gym: GymCreate   # Nested gym creation during owner registration

# class LoginRequest(BaseModel):
#     email: EmailStr
#     password: str

# class TokenResponse(BaseModel):
#     access_token: str
#     token_type: str = "bearer"