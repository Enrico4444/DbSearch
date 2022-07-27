import os
from helpers.common import get_conf
from db import bulk_upload

class DatasetHelper():

    def __init__(self, dataset_file, table_name):
        self.dataset_file = dataset_file
        self.table_name = table_name
    
    def save_to_db(self):
        conf = get_conf()
        out_path = os.path.join(conf.PATH["DATASET_PATH"], f"{self.table_name}.csv")
        self.dataset_file.save(out_path)

        bulk_upload(
            filename=out_path, 
            table_name=self.table_name
        )
        # upload to db
        # bulk_upload(
        #     host=conf.DB["DB_HOST"], 
        #     user=conf.DB["DB_USER"], 
        #     password=conf.DB["DB_PWD"], 
        #     port=conf.DB["DB_PORT"], 
        #     filename=out_path, 
        #     table_name=self.table_name,
        #     sep=","
        # )
