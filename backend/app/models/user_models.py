from . import db
import enum
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Date, Text, Enum, text, ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Gender(enum.Enum):
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    OTHER = 'OTHER'

class Role(db.Model):
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    # Relationship
    users = relationship('User', back_populates='role')


class User(db.Model):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey('role.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    otp = Column(String(10), nullable=True)
    otp_expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, server_default=text("TRUE"))
    created_at = Column(DateTime, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, default=func.now(), server_default=func.now(), onupdate=func.now(), server_onupdate=func.now())

    # Relationship
    # user has only 1 role
    role = relationship('Role', uselist=False, back_populates='users')
    user_info = relationship('UserInfor', back_populates='user', uselist=False, cascade="all, delete-orphan")
    cart = relationship('Cart', back_populates='user', uselist=False, cascade="all, delete-orphan")
    orders = relationship('Order', back_populates='user', cascade="all, delete-orphan")
    feedbacks = relationship('Feedback', back_populates='user', cascade="all, delete-orphan")
    interactions = relationship('Interaction', back_populates='user', cascade="all, delete-orphan")


class UserInfor(db.Model):
    __tablename__ = 'user_infor'

    user_id = Column(Integer, ForeignKey('user.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    gender = Column(Enum(Gender), nullable=True)
    phone_number = Column(String(20), unique=True, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    address = Column(Text, nullable=True)

    # Relationship
    user = relationship('User', back_populates='user_info')