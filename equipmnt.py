from flask_login import UserMixin
from __init__ import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, BigInteger, Boolean, PickleType, ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash


class Equipment(Base):
    """Model for user accounts."""

    __tablename__ = 'equipment'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=False)
    year = Column(Integer, nullable=False, unique=False)

    active = Column(Boolean, index=False, unique=False, nullable=False)

