from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Date, Time
from app.db.database import Base
from sqlalchemy.orm import relationship
import datetime  # Import the whole datetime module

# Base = declarative_base() - Remove this line if it exists

class StateCountry(Base):
    __tablename__ = "state_country"
    
    id = Column(Integer, primary_key=True, index=True)
    state_name = Column(String, nullable=False)
    country_name = Column(String, nullable=False)
    pincodes = relationship("Pincode", back_populates="state_country")

class Pincode(Base):
    __tablename__ = "pincode"
    
    id = Column(Integer, primary_key=True, index=True)
    pincode = Column(String(6), unique=True, nullable=False)
    state_country_id = Column(Integer, ForeignKey("state_country.id"))
    state_country = relationship("StateCountry", back_populates="pincodes")
    gyms = relationship("Gym", back_populates="pincode_ref")
    users = relationship("User", back_populates="pincode_ref")

class Gym(Base):
    __tablename__ = "gym"
    
    id = Column(Integer, primary_key=True, index=True)
    gym_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    gymID = Column(String, unique=True, index=True)
    address = Column(String)
    district = Column(String)
    state_ut = Column(String)  # state/union territory
    pincode = Column(String(6))
    country = Column(String)
    pincode_id = Column(Integer, ForeignKey("pincode.id"))
    pincode_ref = relationship("Pincode", back_populates="gyms")
    users = relationship("User", back_populates="gym")

class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True, index=True)
    gym_id = Column(Integer, ForeignKey("gym.id"))
    gym = relationship("Gym", back_populates="users")
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    address = Column(String)
    district = Column(String)
    state_ut = Column(String)  # state/union territory
    pincode = Column(String(6))
    phone = Column(String(15))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_member = Column(Boolean, default=True)
    is_trainer = Column(Boolean, default=False)
    is_owner = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    pincode_id = Column(Integer, ForeignKey("pincode.id"))
    pincode_ref = relationship("Pincode", back_populates="users")

# NEW ATTENDANCE MODELS
class Shift(Base):
    __tablename__ = "shift"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_active = Column(Boolean, default=True)
    description = Column(String(200), nullable=True)
    
    # Relationship
    attendances = relationship("Attendance", back_populates="shift")

class Attendance(Base):
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    shift_id = Column(Integer, ForeignKey("shift.id"))
    attendance_date = Column(Date, default=datetime.date.today)
    time_in = Column(DateTime, nullable=True)
    time_out = Column(DateTime, nullable=True)
    status = Column(String(1), default='A')  # P=Present, A=Absent
    timeout_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="attendances")
    shift = relationship("Shift", back_populates="attendances")