import json
from sqlalchemy.orm import Session
from db import db
from model.item import ItemModel as Item
from model.supplier import SupplierModel as Supplier
from model.purchase import PurchaseModel as Purchase
from helpers.common import get_logger

logger = get_logger(__name__)

with open("join.json","r") as f:
    conf = json.load(f)

class MergedViewModel():

    @staticmethod
    def _join(filters, tables):

        tbls = tables.copy()

        session = Session(db.engine)
        query = session.query(*[eval(t) for t in tbls]).select_from(eval(tbls[0]))
        
        left_tables = [tbls[0]]
        rm_tables = []

        while len(tbls) > 0:
            for table in tbls:
                for left_table in left_tables:
                    on = conf[left_table].get(table)
                    if on:
                        left_col = list(on.keys())[0]
                        right_col = on[left_col]
                        on = f"{left_table}.{left_col}=={table}.{right_col}"
                        query = query.join(eval(table)).filter(eval(on))
                        if left_table in tbls:
                            rm_tables.append(left_table)
                        rm_tables.append(table)
                        left_tables.append(table)
                        break
            for rm_table in set(rm_tables):
                tbls.remove(rm_table)
            rm_tables = []

        for key in filters:
            query = query.filter(eval(f"{key} == '{filters[key]}'"))
        return query
    
    # TODO: split this function in smaller functions
    def join(**filters):
        tables = []
        if "return" in filters:
            tables = filters.get("return")
            tables = [t.capitalize() for t in tables]
            filters.pop("return")
        if "operator" in filters:
            filters.pop("operator")
        filters = {key.capitalize():val for key,val in filters.items()}      
        for key in filters:
            tables.append(key.split(".")[0])
        tables = list(set(tables))
        
        columns = []
        for t in tables:
            temp_cols = eval(f"{t}.__table__.columns")
            temp_cols = [c.name for c in temp_cols]
            columns += temp_cols
        columns = list(set(columns))
        
        # TODO: use with Session (sqlalchemy >= 1.4) https://stackoverflow.com/questions/66554373/receiving-attributeerror-enter-when-using-sqlalchemy-session-as-context-m
        # with Session(db.engine) as session:
        query = MergedViewModel._join(filters, tables)
        query = query.all()
        
        # GOOD FOR JOINING TWO TABLES
        # query = session.query(*[eval(t) for t in tables])
        # for table in tables[1:]:
        #     query = query.join(eval(table))
        # for key in filters:
        #     query = query.filter(eval(f"{key} == '{filters[key]}'"))
        # query = query.all()
        
        results = []
        for row in query:
            row_results = {}
            for i in range(len(tables)):
                tbl = row[i].__tablename__
                row_dict = row[i].__dict__
                row_results = {
                    **row_results,
                    **{f"{tbl}.{key}":val for key,val in row_dict.items() if key in columns}
                }
            rm_keys = []
            keys = []
            for key in row_results:
                if key.split(".")[1] in keys:
                    rm_keys.append(key)
                else:
                    keys.append(key.split(".")[1])
            for key in rm_keys:
                row_results.pop(key)
            results.append(row_results)
        return results