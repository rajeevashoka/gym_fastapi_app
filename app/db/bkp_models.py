from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Gym(Base):
    __tablename__ = "gyms"

    id = Column(Integer, primary_key=True, index=True)
    gym_name = Column(String(100), nullable=False)
    owner_name = Column(String(100), nullable=False)
    address = Column(String(200), nullable=False)
    phone = Column(String(20), nullable=False, unique=True)
    email = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # One-to-many relationship (Gym → Users)
    users = relationship("User", back_populates="gym", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # gym_id is mandatory for members but will be set when owner creates gym
    gym_id = Column(Integer, ForeignKey("gyms.id", ondelete="CASCADE"), nullable=False)

    email = Column(String(100), nullable=False, unique=True, index=True)
    password = Column(String(200), nullable=False)  # hashed password
    phone = Column(String(20), nullable=False)
    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)   # Gym owner = True

    # Relationship back to gym
    gym = relationship("Gym", back_populates="users")
