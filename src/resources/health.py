from flask_restful import Resource
from test import temp_test

class Health(Resource):

  def get(self):
    return {'message': 'Api OK'}, 200

  def post(self):
    return {'test result': temp_test()}, 200