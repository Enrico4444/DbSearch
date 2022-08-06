class Local:
    LOG = {
        "LOGFILE": "log/log.txt",
        "FORMAT": "%(asctime)s %(message)s"
    }
    APP = {
        "PORT": 5001,
        "SECRET_KEY": "enrico"
    }
    DB = {
        "DB_USER": "postgres_user",
        "DB_PWD": "postgres_password",
        "DB_HOST": "localhost",
        "DB_PORT": 5433,
        "DB_NAME": "ting_postgres_db"
    }
    PATH = {
        "DATASET_PATH": "tmp"
    }
    

