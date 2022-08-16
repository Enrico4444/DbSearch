from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    jwt_required,
    create_access_token,
    create_refresh_token,
    get_jwt
)
from model.user import UserModel as Model
from model.role import RoleModel as Role
from helpers.common import get_logger, get_conf
from helpers.object_storage import ObjectStorage
from helpers.user_role_management import get_permissions, role_has_permissions
from helpers.jwt import refresh_token

logger = get_logger(__name__)

conf = get_conf()

get_parser = reqparse.RequestParser()
post_parser = reqparse.RequestParser()
login_parser = reqparse.RequestParser()

get_parser.add_argument("operator", 
    type=str,
    required=False,
    choices=("and", "or"),
    help="Bad choice: {error_msg}",
    default="and")

cols = [col.name for col in Model.__table__.columns]
cols.remove("id")
for col in cols:
    
    # for user:
    # remove "password" as it is not possible to search by password
    if col != "password":
        get_parser.add_argument(col, 
            type=str,
            required=False,
            store_missing=False)

    if col != "role_id": # role_id not required when adding new user
        login_parser.add_argument(col, 
            type=str,
            required=True,
            help="This field cannot be left blank")
        post_parser.add_argument(col, 
            type=str,
            required=True,
            help="This field cannot be left blank")

    # let user optionally input role name; app will find id; role_name is not required, default role will be input
    post_parser.add_argument("role_name", 
        type=str,
        required=False,
        default="basic")

class User(Resource):

    @staticmethod
    def get_role_id_from_name(role_name):
        role = Role.find_by(name=role_name)
        if role:
            return role[0].id

    @jwt_required()
    def get(self):
        # NOTE: only for testing purpose. To be deleted
        if not role_has_permissions(Model.__tablename__):
            return { "message": "User does not have permissions to perform this request" }
        data = get_parser.parse_args()
        obj_list = Model.find_by(**data)
        if obj_list and len(obj_list) > 0:
            # do not return password
            return [obj.json(exclude=["password"]) for obj in obj_list], 200
        return {"message": "Element not found"}, 404

    @jwt_required()
    def post(self):
        if not role_has_permissions(Model.__tablename__):
            return { "message": "User does not have permissions to perform this request" }
        data = post_parser.parse_args()
        username = data.get("username")
        role_name = data.get("role_name")
        role_id = self.get_role_id_from_name(role_name)
        if not role_id:
            return {"message": f'{role_name} is not a valid role_name'}, 400

        data.pop("role_name")
        data["role_id"] = role_id

        obj_list = Model.find_by(**{"username":username})

        if obj_list and len(obj_list) > 0:
            return {"message": f'Element with username {username} already exists in db'}, 500
        
        obj = Model(**data)
        attr = obj.json()

        try:
            obj.save_to_db()
        except Exception as e:
            logger.error(e, exc_info=True)
            return {"message": "An error occurred inserting the element"}, 500
        return attr, 201

    @jwt_required()
    def put(self):
        if not role_has_permissions(Model.__tablename__):
            return { "message": "User does not have permissions to perform this request" }
        data = post_parser.parse_args()
        username = data.get("username")
        role_name = data.get("role_name")
        role_id = self.get_role_id_from_name(role_name)
        if not role_id:
            return {"message": f'{role_name} is not a valid role_name'}, 400

        data.pop("role_name")
        data["role_id"] = role_id
        
        obj_list = Model.find_by(**{"username":username})

        if not obj_list or len(obj_list)==0:    
            obj = Model(**data)
        else:
            data.pop("username")
            obj = obj_list[0]
            obj.update(data)
        attr = obj.json()
        try:
            obj.save_to_db()
        except Exception as e:
            logger.error(e, exc_info=True)
            return {"message": "An error occurred inserting the element"}, 500
        return attr, 201

    @jwt_required(fresh=True)
    def delete(self):
        if not role_has_permissions(Model.__tablename__):
            return { "message": "User does not have permissions to perform this request" }
        data = get_parser.parse_args()

        obj_list = Model.find_by(**data)
        if obj_list and len(obj_list) > 0:
            for obj in obj_list:
                obj.delete_from_db()
            return { "message": "Element deleted" } 
        return { "message": "Element did not exist in db" } 

class Users(Resource):

    @jwt_required()
    def get(self):
        # NOTE: only for testing purpose. To be deleted
        # do not return password
        if not role_has_permissions(Model.__tablename__):
            return { "message": "User does not have permissions to perform this request" }
        return { "Elements": [obj.json(exclude="password") for obj in Model.query.all()] }
        
    
    @jwt_required(fresh=True)
    def delete(self):
        # TODO: find if exists delete all
        if not role_has_permissions(Model.__tablename__):
            return { "message": "User does not have permissions to perform this request" }
        for obj in Model.query.all():
            obj.delete_from_db()
        return { "message": "Elements deleted from db" }

class UserLogin(Resource):
    def post(self):
        data = login_parser.parse_args()

        user = Model.find_by(**data)

        # authenticate
        if not user:
            return {"message": "Invalid Credentials!"}, 401
        user = user[0]

        # get permissions as additional claim
        permissions = {"permissions": get_permissions(user.id)}

        if user.password == data["password"]:
            access_token = create_access_token(identity=user.id, fresh=True, additional_claims=permissions)
            refresh_token = create_refresh_token(user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}, 200

class UserLogout(Resource):
    @jwt_required()
    def post(self):
        storage = ObjectStorage()
        BLACKLIST = storage.get_json(conf.get("STORAGE_BLACKLIST_PATH"))
        jti = get_jwt()["jti"]  # jti is "JWT ID", a unique identifier for a JWT.
        if jti not in BLACKLIST:
            logger.info("adding jti to blacklist")
            BLACKLIST.append(jti)
            storage.put_json(BLACKLIST, conf.get("STORAGE_BLACKLIST_PATH"))
            return {"message": "Successfully logged out"}, 200 
        logger.info("jti already in blacklist")
        
class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        return {"access_token": refresh_token()}, 200