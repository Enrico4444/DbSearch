from db import db, DbQuery
from helpers.common import get_logger

logger = get_logger(__name__)

class UserModel(db.Model, DbQuery):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    password = db.Column(db.String(160))
    
    def __init__(self, username, password):
        self.username = username
        self.password = password