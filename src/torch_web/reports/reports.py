import csv
import io
from torch_web import db
from sqlalchemy import inspect, Integer, Numeric


def import_csv(file):
    str_file_value = file.read().decode("utf-8")
    file_t = str_file_value.splitlines()
    reader = csv.reader(file_t, delimiter=",", quotechar='"')
    data_read = [row for row in reader]
    header = data_read[0]
    data_read.pop(0)

    return {header: header, reader: data_read}


def get_reports():
    insp = inspect(db.engine)
    tables = insp.get_table_names()
    table_struct = []
    for table in tables:
        primary_key = insp.get_pk_constraint(table)["constrained_columns"]
        dimensions = insp.get_foreign_keys(table)
        foreign_keys = [col for fk in dimensions for col in fk["constrained_columns"]]
        facts = [column for column in insp.get_columns(table) 
                 if column["name"] not in primary_key
                 and column["name"] not in foreign_keys
                 and (isinstance(column["type"], Integer) 
                 or isinstance(column["type"], Numeric))]

        table_struct.append({
            "name": table,
            "foreign_keys": foreign_keys,
            "primary_key": primary_key,
            "dimensions": [{ 
                "fromcolumn": column["constrained_columns"], 
                "totable": column["referred_table"], 
                "tocolumn": column["referred_columns"]} for column in dimensions],
            "facts": [{ "column": column["name"] } for column in facts]
            })

    return table_struct


def run_report(selectedtable, whereclause):
    result = db.engine.execute("select * from " + selectedtable + " " + whereclause)

    si = io.StringIO()
    cw = csv.writer(si, delimiter=",")
    cw.writerow(result.keys())
    cw.writerows(result.fetchall())
    return si.getvalue()
