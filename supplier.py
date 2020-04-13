from flask_login import UserMixin
from __init__ import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, BigInteger, Boolean, PickleType, ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash


class Supplier(Base):
    """Model for parts"""

    __tablename__ = 'supplier'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), index=False, nullable=False, unique=False)
    email = Column(String(100), index=False, nullable=False, unique=False)
    phone = Column(String(100), index=False, nullable=False, unique=False)

    active = Column(Boolean, index=False, unique=False, nullable=False)

