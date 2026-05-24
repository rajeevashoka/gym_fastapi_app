from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Date, Time
from app.db.database import Base
from sqlalchemy.orm import relationship
import datetime  # Import the whole datetime module

# Base = declarative_base() - Remove this line if it exists

# class StateCountry(Base):
#     __tablename__ = "state_country"
    
#     id = Column(Integer, primary_key=True, index=True)
#     state_name = Column(String, nullable=False)
#     country_name = Column(String, nullable=False, default="India")
#     pincodes = relationship("Pincode", back_populates="state_country")

# class Pincode(Base):
#     __tablename__ = "pincode"
    
#     id = Column(Integer, primary_key=True, index=True)
#     pincode = Column(String(6), unique=True, nullable=False)
#     state_country_id = Column(Integer, ForeignKey("state_country.id"))
#     state_country = relationship("StateCountry", back_populates="pincodes")
#     gyms = relationship("Gym", back_populates="pincode_ref")
#     users = relationship("User", back_populates="pincode_ref")

class Gym(Base):
    __tablename__ = "gym"
    
    id = Column(Integer, primary_key=True, index=True)
    gym_name = Column(String, nullable=False)
    prefix = Column(String(10), unique=True,nullable=False)  # NEW: Prefix for member IDs, e.g. "GYM1"
    gymID = Column(String, unique=True, index=True)
    address = Column(String)
    district = Column(String)
    state_ut = Column(String)  # state/union territory
    pincode = Column(String(6), nullable=False)
    country = Column(String, nullable=False, default="India")
    users = relationship("User", back_populates="gym")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    gym_id = Column(Integer, ForeignKey("gym.id"))
    gym = relationship("Gym", back_populates="users")
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    member_id = Column(String, unique=True, nullable=False)  # NEW: Member ID as a string to allow for more flexible formats    
    address1 = Column(String)
    address2 = Column(String)
    landmark = Column(String)
    state_ut = Column(String)  # state/union territory
    district = Column(String)
    pincode = Column(String(6), nullable=False)  # UPDATED: Mandatory, exactly 6 digits
    phone = Column(String(10))  # UPDATED: 10 digits only, can be null
    parents_phone = Column(String(10))  # NEW: Parent's phone number, 10 digits only, can be null
    is_member = Column(Boolean, default=True)
    is_trainer = Column(Boolean, default=False)
    is_staff = Column(Boolean, default=False) #added for future use, can be used to differentiate between different types of users if needed
    is_owner = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    # Relationship
    attendances = relationship(
    "Attendance",
    back_populates="user"
)

# # NEW ATTENDANCE MODELS
# class Shift(Base):
#     __tablename__ = "shift"
    
#     id = Column(Integer, primary_key=True)
#     name = Column(String(50), nullable=False)
#     start_time = Column(Time, nullable=False)
#     end_time = Column(Time, nullable=False)
#     is_active = Column(Boolean, default=True)
#     description = Column(String(200), nullable=True)
    
#     # Relationship
#     attendances = relationship("Attendance", back_populates="shift")

class Attendance(Base):
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    #shift_id = Column(Integer, ForeignKey("shift.id"))
    attendance_date = Column(Date, default=datetime.date.today)
    time_in = Column(DateTime, nullable=True)
    time_out = Column(DateTime, nullable=True)
    status = Column(Boolean, default=False)  # True=Present, False=Absent
    timeout_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    #user = relationship("User", backref="attendances")
    user = relationship(
    "User",
    back_populates="attendances"
)