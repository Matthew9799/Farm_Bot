from flask_login import UserMixin
from __init__ import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, BigInteger, Boolean, PickleType, ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash


class MlModel(Base):
    """Model for linear regression."""

    __tablename__ = 'mlmodels'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=False)
    w1 = Column(Float, index=False, unique=False, nullable=True)
    w2 = Column(Float, index=False, unique=False, nullable=True)
    w3 = Column(Float, index=False, unique=False, nullable=True)
    w4 = Column(Float, index=False, unique=False, nullable=True)
    w5 = Column(Float, index=False, unique=False, nullable=True)
