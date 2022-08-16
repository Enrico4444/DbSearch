from flask_jwt_extended import jwt_required
from flask_restful import Resource, reqparse
from model.supplier import SupplierModel
from model.merged_view import MergedViewModel
from model.item import ItemModel
from model.purchase import PurchaseModel
from model.role import RoleModel
from model.user import UserModel
from helpers.common import get_logger
from helpers.user_role_management import role_has_permissions

logger = get_logger(__name__)

class MergedView(Resource):

    parser = reqparse.RequestParser()
    
    parser.add_argument("operator", 
        type=str,
        required=False,
        choices=("and", "or"),
        help="Bad choice: {error_msg}",
        default="and")

    parser.add_argument("return", 
        type=str,
        required=False,
        action="append")

    cols = [f'supplier.{col.name}' for col in SupplierModel.__table__.columns] +\
           [f'item.{col.name}' for col in ItemModel.__table__.columns] +\
           [f'purchase.{col.name}' for col in PurchaseModel.__table__.columns] +\
           [f'role.{col.name}' for col in RoleModel.__table__.columns] +\
           [f'user.{col.name}' for col in UserModel.__table__.columns]
    
    for col in cols:
        parser.add_argument(col, 
            type=str,
            required=False,
            store_missing=False)

    @jwt_required()
    def get(self):
        if not role_has_permissions("merged_view"):
            return { "message": "User does not have permissions to perform this request" }
        data = MergedView.parser.parse_args(strict=True) # abort if wrong arguments
        return MergedViewModel.join(**data)


