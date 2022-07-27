from flask_restful import Resource, reqparse
from model.supplier import SupplierModel
from helpers.common import get_logger

logger = get_logger(__name__)

class Supplier(Resource):
    parser = reqparse.RequestParser()
    
    parser.add_argument('address', 
        type=str,
        required=True,
        help="This field cannot be left blank")

    parser.add_argument('email', 
        type=str,
        required=True,
        help="This field cannot be left blank")

    def get(self, name):
        supplier = SupplierModel.find_by(first_only=True, name=name)
        if supplier:
            return supplier.json(), 200
        return {'message': 'Supplier not found'}, 404

    def post(self, name):
        data = Supplier.parser.parse_args()

        supplier = SupplierModel.find_by(first_only=True, name=name)

        if supplier:
            return {'message': f'Supplier with name {name} already exists in db'}, 500
        
        supplier = SupplierModel(name, **data)
        attr = supplier.json()

        try:
            supplier.save_to_db()
        except:
            return {'message': 'An error occurred inserting the supplier'}, 500
        return attr, 201

    def put(self, name):
        data = Supplier.parser.parse_args()
        
        supplier = SupplierModel.find_by(first_only=True, name=name)

        if not supplier:    
            supplier = SupplierModel(name, **data)
        else:
            supplier.email = data.get('email')
            supplier.address = data.get('address')
        try:
            supplier.save_to_db()
        except:
            return {'message': 'An error occurred inserting the supplier'}, 500
        return supplier.json(), 201

    def delete(self, name):
        supplier = SupplierModel.find_by(first_only=True, name=name)
        if supplier:
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
