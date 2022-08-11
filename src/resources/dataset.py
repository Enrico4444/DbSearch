from flask_restful import Resource, reqparse
from werkzeug.datastructures import FileStorage
from flask_jwt_extended import jwt_required
from helpers.dataset import DatasetHelper
from helpers.common import get_logger
from helpers.user_role_management import role_has_permissions

logger = get_logger(__name__)

class Dataset(Resource):
    parser = reqparse.RequestParser()
    
    parser.add_argument('dataset_file', 
        type=FileStorage,
        required=True,
        location='files', # NOTE: THIS LINE IS ESSENTIAL and location has to be exactly 'files'
        help="This field cannot be left blank")

    @jwt_required()
    def put(self, table_name):
        if not role_has_permissions('dataset'):
            return { 'message': 'User does not have permissions to perform this request' }
        data = Dataset.parser.parse_args()
        dataset_file = data.get("dataset_file")
        try:
            dataset = DatasetHelper(dataset_file=dataset_file, table_name=table_name)
            filename = dataset.save_to_db()
            return {'message': f'Dataset saved as {filename}'}, 200
        except Exception as e: 
            logger.error(e, exc_info=True)
            return {'message': 'An error occurred uploading the dataset'}, 500