from flask_login import UserMixin
from __init__ import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, BigInteger, Boolean, PickleType, ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash


class AllParts(Base):
    """Model for parts"""

    __tablename__ = 'allparts'

    id = Column(Integer, primary_key=True)

    part = Column(Integer, ForeignKey('parts.id'))
    installed_in = Column(Integer, ForeignKey('equipment.id'))

    weeks = Column(Integer, nullable=False, unique=False)
    quantity = Column(Integer, nullable=False, unique=False)

    active = Column(Boolean, index=False, unique=False, nullable=False)

    create = Column(DateTime, index=False, unique=False, nullable=True)
    delete = Column(DateTime, index=False, unique=False, nullable=True)


