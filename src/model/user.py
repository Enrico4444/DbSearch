from ast import For
from sqlalchemy import ForeignKey
from db import db, DbQuery
from helpers.common import get_logger

logger = get_logger(__name__)

class UserModel(db.Model, DbQuery):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    password = db.Column(db.String(160))
    role_id = db.Column(db.Integer, ForeignKey("role.id"))
    
    def __init__(self, username, password, role_id):
        self.username = username
        self.password = password
        self.role_id = role_id