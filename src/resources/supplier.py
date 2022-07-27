from flask_restful import Resource, reqparse
from model.supplier import SupplierModel
from helpers.common import get_logger

logger = get_logger(__name__)

class Supplier(Resource):
    get_parser = reqparse.RequestParser()
    post_parser = reqparse.RequestParser()

    get_parser.add_argument("operator", 
        type=str,
        required=False,
        choices=('and', 'or'),
        help='Bad choice: {error_msg}',
        default="and")

    cols = [col.name for col in SupplierModel.__table__.columns]
    cols.remove('id')
    for col in cols:
    
        get_parser.add_argument(col, 
            type=str,
            required=False,
            store_missing=False)

        post_parser.add_argument(col, 
            type=str,
            required=True,
            help="This field cannot be left blank")

    def get(self):
        data = Supplier.get_parser.parse_args()
        supplier_list = SupplierModel.find_by(**data)
        if supplier_list and len(supplier_list) > 0:
            return [supplier.json() for supplier in supplier_list], 200
        return {'message': 'Supplier not found'}, 404

    def post(self):
        data = Supplier.post_parser.parse_args()
        name = data.get("name")

        supplier_list = SupplierModel.find_by(**{"name":name})

        if supplier_list and len(supplier_list) > 0:
            return {'message': f'Supplier with name {name} already exists in db'}, 500
        
        supplier = SupplierModel(**data)
        attr = supplier.json()

        try:
            supplier.save_to_db()
        except:
            return {'message': 'An error occurred inserting the supplier'}, 500
        return attr, 201

    def put(self):
        data = Supplier.post_parser.parse_args()
        name = data.get("name")
        
        supplier_list = SupplierModel.find_by(**{"name":name})

        if not supplier_list or len(supplier_list)==0:    
            supplier = SupplierModel(**data)
        else:
            supplier = supplier_list[0]
            supplier.email = data.get('email')
            supplier.address = data.get('address')
        attr = supplier.json()
        try:
            supplier.save_to_db()
        except:
            return {'message': 'An error occurred inserting the supplier'}, 500
        return attr, 201

    def delete(self):
        data = Supplier.get_parser.parse_args()

        supplier_list = SupplierModel.find_by(**data)
        if supplier_list and len(supplier_list) > 0:
            for supplier in supplier_list:
                supplier.delete_from_db()
            return { 'message': 'Supplier deleted' } 
        return { 'message': 'Supplier did not exist in db' } 

class Suppliers(Resource):

    def get(self):
        return { 'suppliers': [supplier.json() for supplier in SupplierModel.query.all()] }
    
    def delete(self):
        # TODO: find if exists delete all
        for supplier in SupplierModel.query.all():
            supplier.delete_from_db()
        return { 'message': 'Suppliers deleted from db' }
