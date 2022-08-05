from sqlalchemy import ForeignKey
from db import db, DbQuery
from helpers.common import get_logger

logger = get_logger(__name__)

class PurchaseModel(db.Model, DbQuery):
    __tablename__ = 'purchase'

    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(80), ForeignKey("item.name"))
    quantity = db.Column(db.Integer)
    discount_percent = db.Column(db.Float)
    date_time = db.Column(db.String(80))
    
    def __init__(self, item_name, quantity, discount_percent, date_time):
        self.item_name = item_name
        self.quantity = quantity
        self.discount_percent = discount_percent
        self.date_time = date_time
        