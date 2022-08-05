from sqlalchemy import ForeignKey
from sqlalchemy.schema import UniqueConstraint
from db import db, DbQuery
from helpers.common import get_logger

logger = get_logger(__name__)

class ItemModel(db.Model, DbQuery):
    __tablename__ = 'item'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    category = db.Column(db.String(160))
    price = db.Column(db.Float)
    supplier_name = db.Column(db.String(80), ForeignKey("supplier.name"))
    __table_args__ = (UniqueConstraint("name"),)
    
    def __init__(self, name, category, price, supplier_name):
        self.name = name
        self.category = category
        self.price = price
        self.supplier_name = supplier_name
        