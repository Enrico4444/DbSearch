import os
import logging
from dotenv import dotenv_values

def get_conf():
    # ENV is set in app.py from sys.argv
    env = os.environ.get("ENV", "local")
    # config is read from src/<ENV>.env file, which is gitignored
    return eval(f"dotenv_values('{env}.env')")

def get_logger(current_filename):
    conf = get_conf()
    logger = logging.getLogger(current_filename)

    handler = logging.FileHandler(filename=conf.get("LOGFILE"))
    handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)

    return logger