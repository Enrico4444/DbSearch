import os
import sys
import logging
from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from datetime import timedelta

from db import db

from blacklist import BLACKLIST

from resources.health import Health
from resources.supplier import Supplier, Suppliers
from resources.item import Item, Items
from resources.purchase import Purchase, Purchases
from resources.user import User, Users, UserLogin
from resources.merged_view import MergedView
from resources.tables import Tables
from resources.dataset import Dataset

from helpers.common import get_conf

# get config based on environment
# run app as python app.py <env>. Env can be local, dev, prod
env = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("ENV")
os.environ["ENV"] = env
# config is read from src/<ENV>.env file, which is gitignored
conf = get_conf()

# set logger
logging.basicConfig(filename = conf.get("LOGFILE"),
                    format = conf.get("FORMAT"),
                    filemode = "w",
                    level = logging.INFO)
logging.info(f"Running on {env}")

# db
db_user = conf.get("DB_USER")
db_pwd = conf.get("DB_PWD")
db_host = conf.get("DB_HOST")
db_port = conf.get("DB_PORT")
db_name = conf.get("DB_NAME")

# app and api
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{db_user}:{db_pwd}@{db_host}:{db_port}/{db_name}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False # use the sqlalchemy tracker not the flask_sqlalchemy tracker
app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=1800) # set JWT token to expire within 30 min
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_BLACKLIST_ENABLED'] = True  # enable blacklist feature
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']  # allow blacklisting for access and refresh tokens
app.secret_key = conf.get("SECRET_KEY")
api = Api(app)

# flask decorator
@app.before_first_request
def create_tables():
  db.create_all()

jwt = JWTManager(app)

# endpoints
api.add_resource(Health, '/health')
api.add_resource(Supplier, '/supplier')
api.add_resource(Suppliers, '/suppliers')
api.add_resource(Item, '/item')
api.add_resource(Items, '/items')
api.add_resource(Purchase, '/purchase')
api.add_resource(Purchases, '/purchases')
api.add_resource(User, '/user')
api.add_resource(Users, '/users')
api.add_resource(MergedView, '/merged_view')
api.add_resource(Tables, '/tables', '/tables/<string:table_name>')
api.add_resource(Dataset, '/dataset/<string:table_name>')
api.add_resource(UserLogin, '/login')

# run once
if __name__ == "__main__":
  db.init_app(app)
  app.run(port=conf.get("PORT"), debug=True)