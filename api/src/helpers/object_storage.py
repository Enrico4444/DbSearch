import json
import io
from minio import Minio
from minio.error import S3Error
from helpers.common import get_conf, get_logger

logger = get_logger(__name__)

conf = get_conf()

def raise_storage_error(function):
    def wrapper(*args, **kwargs):
        try:
            result = function(*args, **kwargs)
            return result
        except S3Error as e:
            if e.code == "NoSuchKey":
                if "path" in kwargs:
                    file_not_found = str(kwargs["path"])
                else:
                    file_not_found = str(args[-1])
                msg = "File not found: {}".format(file_not_found)
                logger.error(msg, exc_info=True)
                raise FileNotFoundError(msg)
            else:
                msg = "Unknown Storage Error"
                logger.error(msg, exc_info=True)
                raise e
        except Exception as e:
            msg = "Unknown Storage Error"
            logger.error(msg, exc_info=True)
            raise e  
    return wrapper

class ObjectStorage():

    def __init__(self):
        self.client = self.storage_connection()
        self.bucket = conf.get("STORAGE_BUCKET")
        self.make_bucket_if_not_exists()

    @staticmethod
    def storage_connection():
        # general storage connection; replace content if replacing storage
        storage_credentials = {
            "access_key": conf.get("STORAGE_ACCESS_KEY"),
            "secret_key": conf.get("STORAGE_SECRET_KEY")
        }
        storage_url = f'{conf.get("STORAGE_HOST")}:{conf.get("STORAGE_PORT")}'
        try:
            minio = Minio(
                storage_url,
                access_key=storage_credentials["access_key"],
                secret_key=storage_credentials["secret_key"],
                secure=False
            )
            return minio
        except Exception as e:
            logger.error("Failed connecting to object storage", exc_info=True) 

    def make_bucket_if_not_exists(self):
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)   
        
    @raise_storage_error
    def get_json(self, key):
        if not key.endswith("json"):
            key = key + ".json"
        http_resp = self.client.get_object(self.bucket, key)
        obj = json.load(io.BytesIO(http_resp.read()))
        return obj

    @raise_storage_error
    def put_json(self, object, key):
        if not key.endswith("json"):
            key = key + ".json" 
        str_obj = json.dumps(object, indent=5)
        bytes_obj = str_obj.encode("utf-8")
        length = len(str_obj)

        self.client.put_object(
            bucket_name=self.bucket,
            object_name=key,
            data=io.BytesIO(bytes_obj),
            length=length
        )

    @raise_storage_error
    def delete_object(self, key):
        if not key.endswith("json"):
            key = key + ".json"
        return self.client.remove_object(self.bucket, key)