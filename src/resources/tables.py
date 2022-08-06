from flask_restful import Resource
from flask_jwt_extended import jwt_required
from sqlalchemy import inspect
from db import db

class Tables(Resource):

  @jwt_required()
  def get(self, table_name=None):
    inspector = inspect(db.engine)

    if table_name:
      columns = inspector.get_columns(table_name)
      return {'columns': [col_dict['name'] for col_dict in columns]}, 200
    else:
      return {'tables': inspector.get_table_names()}, 200
    # oppure implementa in ogni classe questo
    # colnames = cls.__table__.columns
    # return {"message": [col.name for col in colnames]}