from turtle import update
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from model.role import RoleModel as Model
from helpers.common import get_logger
from helpers.user_role_management import assign_permissions

logger = get_logger(__name__)

class Role(Resource):
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

    # for role, add permission mapping to post_parser
    # NOTE: default permission is allow all for testing only
    default_permissions = {"all":["get","put","post","delete"]}

    post_parser.add_argument("permissions",
        type=dict,
        required=False,
        default=default_permissions
    )
    post_parser.add_argument("permission_action",
        type=str,
        choices=("append","replace"),
        required=False,
        default="append"
    )

    @staticmethod
    def correct_input_permissions(permission_dict, allowed):
        allowed = set(allowed)
        for resource_name in permission_dict:
            permissions = set(permission_dict[resource_name])
            if len(permissions.difference(allowed)) > 0:
                return False
        return True

    @jwt_required()
    def get(self):
        data = Role.get_parser.parse_args()
        obj_list = Model.find_by(**data)
        if obj_list and len(obj_list) > 0:
            return [obj.json() for obj in obj_list], 200
        return {'message': 'Element not found'}, 404

    @jwt_required()
    def post(self):
        data = Role.post_parser.parse_args()
        # separate columns from permission information
        permissions = data["permissions"]
        allowed = ["get","put","post","delete"]
        if not self.correct_input_permissions(permissions, allowed):
            return {'message': f'Invalid permissions. Allowed are {allowed}'}, 400
        permission_action = "replace" # for post request, action must be replace
        data.pop("permissions")
        data.pop("permission_action")

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
        
        # add permissions to permission mapping
        assign_permissions(role_name=name, permissions=permissions, permission_action=permission_action)

        return attr, 201

    @jwt_required()
    def put(self):
        data = Role.post_parser.parse_args()
        # separate columns from permission information
        permissions = data["permissions"]
        allowed = ["get","put","post","delete"]
        if not self.correct_input_permissions(permissions, allowed):
            return {'message': f'Invalid permissions. Allowed are {allowed}'}, 400
        permission_action = data["permission_action"]
        data.pop("permissions")
        data.pop("permission_action")

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
        
        # add permissions to permission mapping
        assign_permissions(role_name=name, permissions=permissions, permission_action=permission_action)

        return attr, 201

    @jwt_required(fresh=True)
    def delete(self):
        data = Role.get_parser.parse_args()

        obj_list = Model.find_by(**data)
        if obj_list and len(obj_list) > 0:
            for obj in obj_list:
                obj.delete_from_db()
            return { 'message': 'Element deleted' } 
        return { 'message': 'Element did not exist in db' } 

class Roles(Resource):

    @jwt_required()
    def get(self):
        return { 'Elements': [obj.json() for obj in Model.query.all()] }
    
    @jwt_required(fresh=True)
    def delete(self):
        # TODO: find if exists delete all
        for obj in Model.query.all():
            obj.delete_from_db()
        return { 'message': 'Elements deleted from db' }
