import os
import sys
from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from datetime import timedelta

from db import db

from resources.health import Health
from resources.supplier import Supplier, Suppliers
from resources.item import Item, Items
from resources.purchase import Purchase, Purchases
from resources.user import User, Users, UserLogin, UserLogout, TokenRefresh
from resources.merged_view import MergedView
from resources.tables import Tables
from resources.dataset import Dataset
from resources.role import Role, Roles

from helpers.common import get_conf, get_logger
from helpers.user_role_management import create_role_and_user
from helpers.object_storage import ObjectStorage

# get config based on environment
# run app as python app.py <env>. Env can be local, dev, prod
envs = ["local","dev","prod"]
os.environ["ENVIRON"] = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in envs else os.environ.get("ENVIRON","local")
# config is read from src/<ENV>.env file, which is gitignored
conf = get_conf()

# set logger
logger = get_logger(__name__)

# db
db_user = conf.get("DB_USER")
db_pwd = conf.get("DB_PWD")
db_host = conf.get("DB_LOCAL_HOST")
db_port = conf.get("DB_LOCAL_PORT")
db_name = conf.get("DB_NAME")

# app and api
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f'postgresql://{db_user}:{db_pwd}@{db_host}:{db_port}/{db_name}'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False # use the sqlalchemy tracker not the flask_sqlalchemy tracker
app.config["JWT_EXPIRATION_DELTA"] = timedelta(seconds=1800) # set JWT token to expire within 30 min
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["JWT_BLACKLIST_ENABLED"] = True  # enable blacklist feature
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access", "refresh"]  # allow blacklisting for access and refresh tokens
app.secret_key = conf.get("SECRET_KEY")
api = Api(app)

# flask decorator
@app.before_first_request
def create_tables():
  db.create_all()

@app.before_first_request
def create_rsc():
  rsc = {
    conf.get("STORAGE_PERMISSIONS_PATH"): {}, 
    conf.get("STORAGE_BLACKLIST_PATH"): []
  }
  client = ObjectStorage()
  for r in rsc:
    try:
      client.get_json(r)
      logger.info(f'Resource {r} already exists')
    except FileNotFoundError:
      logger.info(f'Putting resource {r}')
      client.put_json(object=rsc[r], key=r)

@app.before_first_request
def create_initial_role_and_user():
  admin_permissions = {"all":["get","put","post","delete"]}
  # creates admin role and admin user
  create_role_and_user(
    role_name="admin", 
    permissions=admin_permissions,
    username="admin", 
    password=conf.get("ADMIN_PASSWORD")
  )

  basic_permissions = {"all":["get","put","post","delete"]} # basic are same as admin for testing purposed
  # creates basic default role without user
  create_role_and_user(
    role_name="basic", 
    permissions=basic_permissions
  )

jwt = JWTManager(app)

# endpoints
api.add_resource(Health, "/health")
api.add_resource(Supplier, "/supplier")
api.add_resource(Suppliers, "/suppliers")
api.add_resource(Item, "/item")
api.add_resource(Items, "/items")
api.add_resource(Purchase, "/purchase")
api.add_resource(Purchases, "/purchases")
api.add_resource(User, "/user")
api.add_resource(Users, "/users")
api.add_resource(MergedView, "/merged_view")
api.add_resource(Tables, "/tables", "/tables/<string:table_name>")
api.add_resource(Dataset, "/dataset/<string:table_name>")
api.add_resource(UserLogin, "/login")
api.add_resource(UserLogout, "/logout")
api.add_resource(TokenRefresh, "/refresh")
api.add_resource(Role, "/role")
api.add_resource(Roles, "/roles")

db.init_app(app)

if __name__ == "__main__":
  # NOTE: host=0.0.0.0 instead of 127.0.0.1 important for reaching app running on container from localhost
  app.run(host=conf.get("API_LOCAL_HOST"), port=conf.get("API_LOCAL_PORT"), debug=True)