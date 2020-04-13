from flask_login import UserMixin
from __init__ import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, BigInteger, Boolean, PickleType, ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash


class Failed(Base):
    """Model for parts"""

    __tablename__ = 'failed'

    id = Column(Integer, primary_key=True)

    part = Column(Integer, ForeignKey('parts.id'))

    create = Column(DateTime, index=False, unique=False, nullable=True)
    delete = Column(DateTime, index=False, unique=False, nullable=True)


