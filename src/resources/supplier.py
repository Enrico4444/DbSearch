from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from model.supplier import SupplierModel as Model
from helpers.common import get_logger
from helpers.user_role_management import role_has_permissions

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

    cols = [col.name for col in Model.__table__.columns]
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

    @jwt_required()
    def get(self):
        if not role_has_permissions(Model.__tablename__):
            return { 'message': 'User does not have permissions to perform this request' }
        data = Supplier.get_parser.parse_args()
        obj_list = Model.find_by(**data)
        if obj_list and len(obj_list) > 0:
            return [obj.json() for obj in obj_list], 200
        return {'message': 'Element not found'}, 404

    @jwt_required()
    def post(self):
        if not role_has_permissions(Model.__tablename__):
            return { 'message': 'User does not have permissions to perform this request' }
        data = Supplier.post_parser.parse_args()
        name = data.get("name")

        obj_list = Model.find_by(**{"name":name})

        if obj_list and len(obj_list) > 0:
            return {'message': f'Element with name {name} already exists in db'}, 500
        
        obj = Model(**data)
        attr = obj.json()

        try:
            obj.save_to_db()
        except Exception as e:
            logger.error(e, exc_info=True)
            return {'message': 'An error occurred inserting the element'}, 500
        return attr, 201

    @jwt_required()
    def put(self):
        if not role_has_permissions(Model.__tablename__):
            return { 'message': 'User does not have permissions to perform this request' }
        data = Supplier.post_parser.parse_args()
        name = data.get("name")
        
        obj_list = Model.find_by(**{"name":name})

        if not obj_list or len(obj_list)==0:    
            obj = Model(**data)
        else:
            data.pop("name")
            obj = obj_list[0]
            obj.update(data)
        attr = obj.json()
        try:
            obj.save_to_db()
        except Exception as e:
            logger.error(e, exc_info=True)
            return {'message': 'An error occurred inserting the element'}, 500
        return attr, 201

    @jwt_required(fresh=True)
    def delete(self):
        if not role_has_permissions(Model.__tablename__):
            return { 'message': 'User does not have permissions to perform this request' }
        data = Supplier.get_parser.parse_args()

        obj_list = Model.find_by(**data)
        if obj_list and len(obj_list) > 0:
            for obj in obj_list:
                obj.delete_from_db()
            return { 'message': 'Element deleted' } 
        return { 'message': 'Element did not exist in db' } 

class Suppliers(Resource):

    @jwt_required()
    def get(self):
        if not role_has_permissions(Model.__tablename__):
            return { 'message': 'User does not have permissions to perform this request' }
        return { 'Elements': [obj.json() for obj in Model.query.all()] }
    
    @jwt_required(fresh=True)
    def delete(self):
        # TODO: find if exists delete all
        if not role_has_permissions(Model.__tablename__):
            return { 'message': 'User does not have permissions to perform this request' }
        for obj in Model.query.all():
            obj.delete_from_db()
        return { 'message': 'Elements deleted from db' }
