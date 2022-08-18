import os
from helpers.common import get_conf
from db import bulk_upload

conf = get_conf()

class DatasetHelper():

    def __init__(self, dataset_file, table_name):
        self.dataset_file = dataset_file
        self.table_name = table_name
    
    def save_to_db(self):
        out_path = os.path.join(conf.get("LOCAL_TEMP_PATH"), f'{self.table_name}.csv')
        self.dataset_file.save(out_path)

        bulk_upload(
            filename=out_path, 
            table_name=self.table_name
        )
        # upload to db
        # bulk_upload(
        #     host=conf.get("DB_LOCAL_HOST"), 
        #     user=conf.get("DB_USER"), 
        #     password=conf.get("DB_PWD"), 
        #     port=conf.get("DB_LOCAL_PORT"), 
        #     filename=out_path, 
        #     table_name=self.table_name,
        #     sep=","
        # )
