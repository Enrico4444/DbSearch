from sqlalchemy.schema import UniqueConstraint
from db import db, DbQuery
from helpers.common import get_logger

logger = get_logger(__name__)

class SupplierModel(db.Model, DbQuery):
    __tablename__ = "supplier"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    address = db.Column(db.String(160))
    email = db.Column(db.String(80))
    __table_args__ = (UniqueConstraint("name"),)

    def __init__(self, name, address, email):
        self.name = name
        self.address = address
        self.email = email