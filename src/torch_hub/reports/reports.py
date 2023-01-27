import csv
import io
from torch import db


def import_csv(file):
    str_file_value = file.read().decode("utf-8")
    file_t = str_file_value.splitlines()
    reader = csv.reader(file_t, delimiter=",", quotechar='"')
    data_read = [row for row in reader]
    header = data_read[0]
    data_read.pop(0)

    return {header: header, reader: data_read}


def get_reports():
    return db.engine.table_names()


def run_report(selectedtable, whereclause):
    result = db.engine.execute("select * from " + selectedtable + " " + whereclause)

    si = io.StringIO()
    cw = csv.writer(si, delimiter=",")
    cw.writerow(result.keys())
    cw.writerows(result.fetchall())
    return si.getvalue()
