import os
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Boolean, JSON
from .db import Base
from werkzeug.security import check_password_hash, generate_password_hash


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(128))
    slack_id = Column(String(128))
    password_hash = Column(String(254))
    location = Column(String(128))
    config = Column(JSON)
    is_admin = Column(Boolean, default=False)

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
