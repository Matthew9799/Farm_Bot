from flask_login import UserMixin
from __init__ import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, BigInteger, Boolean, PickleType, ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash


class Parts(Base):
    """Model for parts"""

    __tablename__ = 'parts'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), index=False, nullable=False, unique=False)
    supplier = Column(Integer, ForeignKey('supplier.id'), index=False, unique=False, nullable=False)
    quantity = Column(Integer, index=False, unique=False, nullable=False)
    location = Column(Integer, ForeignKey('locations.id'), nullable=False, unique=False)

    model = Column(Integer, ForeignKey('mlmodels.id'), nullable=False, unique=True)

    active = Column(Boolean, index=False, unique=False, nullable=False)

    harvest = Column(Boolean, index=False, unique=False, nullable=True)
    spraying = Column(Boolean, index=False, unique=False, nullable=True)
    seeding = Column(Boolean, index=False, unique=False, nullable=True)
    winter = Column(Boolean, index=False, unique=False, nullable=True)
