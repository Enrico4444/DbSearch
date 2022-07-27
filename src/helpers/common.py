import os
import config
import logging

def get_conf():
    env = os.environ.get("ENV", "Local")
    return eval(f"config.{env}")

def get_logger(current_filename):
    conf = get_conf()
    logger = logging.getLogger(current_filename)

    handler = logging.FileHandler(filename=conf.LOG["LOGFILE"])
    handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)

    return logger