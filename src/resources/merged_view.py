from flask_jwt_extended import jwt_required
from flask_restful import Resource, reqparse
from model.supplier import SupplierModel
from model.merged_view import MergedViewModel
from model.item import ItemModel
from model.purchase import PurchaseModel
from helpers.common import get_logger

logger = get_logger(__name__)

class MergedView(Resource):

    parser = reqparse.RequestParser()
    
    parser.add_argument("operator", 
        type=str,
        required=False,
        choices=('and', 'or'),
        help='Bad choice: {error_msg}',
        default="and")

    parser.add_argument("return", 
        type=str,
        required=False,
        action="append")

    cols = [f"supplier.{col.name}" for col in SupplierModel.__table__.columns] +\
           [f"item.{col.name}" for col in ItemModel.__table__.columns] +\
           [f"purchase.{col.name}" for col in PurchaseModel.__table__.columns]
    while "id" in cols:
        cols.remove('id')
    
    for col in cols:
        parser.add_argument(col, 
            type=str,
            required=False,
            store_missing=False)

    @jwt_required()
    def get(self):
        data = MergedView.parser.parse_args()
        return MergedViewModel.join(**data)


