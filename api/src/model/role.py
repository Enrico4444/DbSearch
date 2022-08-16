# from sqlalchemy.schema import UniqueConstraint
from db import db, DbQuery
from helpers.common import get_logger

logger = get_logger(__name__)

class RoleModel(db.Model, DbQuery):
    __tablename__ = "role"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    # __table_args__ = (UniqueConstraint("name"),)
    
    def __init__(self, name):
        self.name = name