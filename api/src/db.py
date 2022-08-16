from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import column, and_, or_
# import psycopg2
import pandas as pd

# sqlalchemy db
db = SQLAlchemy()

def bulk_upload(filename, table_name):
    # TODO: handle duplicate primary keys when inserting from csv
    df = pd.read_csv(filename)
    df.to_sql(table_name, db.engine, if_exists="append", index=False)

class DbQuery():
    
    @staticmethod
    def build_query(filters):
        ops = {
            "and": and_,
            "or": or_
        }
        operator = ops[filters["operator"]]
        return operator(
            *[column(key)==filters[key] for key in filters if key != "operator"]
        )

    @classmethod
    def find_by(cls, **filters):
        if "operator" in filters:
            return cls.query.filter(
                DbQuery.build_query(filters)
            ).all()
        else:
            return cls.query.filter_by(
                **filters
            ).all()

    @classmethod
    def get_columns(cls):
        return [col.name for col in cls.__table__.columns]

    def json(self, exclude=[]):
        cols = self.__table__.columns # accessing __table__ property of cls through __class__
        colnames = [col.name for col in cols]
        return { col: self.__dict__[col] for col in colnames if col in self.__dict__ and col not in exclude}

    # upsert 
    def save_to_db(self): 
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def update(self, new_values):
        cols = self.__table__.columns
        cols = [col.name for col in cols if col.name in list(new_values.keys())]
        for col in cols:
            setattr(self, col, new_values.get(col))

# psycopg2 connection used for bulk upload
# def bulk_upload(host, user, password, port, filename, table_name, sep=","):
#     conn = psycopg2.connect(host=host,user=user,password=password,port=port)
#     cur = conn.cursor()

#     with open(filename, "r") as f:
#         next(f) # skip header row
#         cur.copy_from(f, table_name, sep=sep)
#         conn.commit()

