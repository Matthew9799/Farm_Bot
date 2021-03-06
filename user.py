from flask_login import UserMixin
from __init__ import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager


class User(UserMixin, db.Model):
    """Model for user accounts."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(200), primary_key=False, unique=False, nullable=False)
    created_on = db.Column(db.DateTime, index=False, unique=False, nullable=True)
    last_login = db.Column(db.DateTime, index=False, unique=False, nullable=True)
    failed_attempt = db.Column(db.Integer, index=False, unique=False, nullable=False)
    last_attempt = db.Column(db.DateTime, index=False, unique=False, nullable=True)
    active = db.Column(db.Boolean, index=False, unique=False, nullable=False)

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password, method='sha256')

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User {}>'.format(self.name)
