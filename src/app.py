import os
import sys
import logging
from flask import Flask
from flask_restful import Api

from db import db

from resources.health import Health
from resources.supplier import Supplier, Suppliers
from resources.tables import Tables
from resources.dataset import Dataset

from helpers.common import get_conf

# get config based on environment
env = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("ENV") # Local, Dev, Prod
os.environ["ENV"] = env
conf = get_conf()

# set logger
logging.basicConfig(filename = conf.LOG.get("LOGFILE"),
                    format = conf.LOG.get("FORMAT"),
                    filemode = "w",
                    level = logging.INFO)
logging.info(f"Running on {env}")

# db
db_user = conf.DB.get("DB_USER")
db_pwd = conf.DB.get("DB_PWD")
db_host = conf.DB.get("DB_HOST")
db_port = conf.DB.get("DB_PORT")
db_name = conf.DB.get("DB_NAME")

# app and api
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{db_user}:{db_pwd}@{db_host}:{db_port}/{db_name}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False # use the sqlalchemy tracker not the flask_sqlalchemy tracker
api = Api(app)

# flask decorator
@app.before_first_request
def create_tables():
  db.create_all()

# endpoints
api.add_resource(Health, '/health')
api.add_resource(Supplier, '/supplier')
api.add_resource(Suppliers, '/suppliers')
api.add_resource(Tables, '/tables', '/tables/<string:table_name>')
api.add_resource(Dataset, '/dataset/<string:table_name>')

# run once
if __name__ == "__main__":
  db.init_app(app)
  app.run(port=conf.APP.get("PORT"), debug=True)