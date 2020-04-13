from flask_login import UserMixin
from __init__ import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, BigInteger, Boolean, PickleType
from werkzeug.security import generate_password_hash, check_password_hash


class Banned(Base):
    """Model for parts"""

    __tablename__ = 'banned'

    id = Column(Integer, primary_key=True)

    ipAddress = Column(String(30), nullable=False, unique=False)
    attempts = Column(Integer, nullable=False, unique=False)
    weeklyAttempts = Column(BigInteger, nullable=False, unique=False)

    lockoutStart = Column(DateTime, nullable=True, unique=False)
    permaBan = Column(Boolean, nullable=False, unique=False)

    active = Column(Boolean, index=False, unique=False, nullable=False)


