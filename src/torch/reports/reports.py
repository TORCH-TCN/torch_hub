import csv
import io
from flask import Blueprint, flash, jsonify, make_response, render_template, request
from flask_login import login_required
from sqlalchemy import Column, DateTime, Integer, String, func
#from torch.config.database.TorchDatabase import Entity, db
from torch import db
from sqlalchemy.orm import relationship
from flask_security import current_user, roles_accepted

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")

@reports_bp.route('/import', methods=['GET'])
# @roles_accepted('admin')
def csvfiles_import():

    header = [] 
    data_read = [] 

    return render_template("/reports/import.html", user=current_user, header=header, reader=data_read)

@reports_bp.route('/import', methods=[ 'POST'])
# @roles_accepted('admin')
def csvfiles_import_post():

    header = [] 
    data_read = []
    if request.method == 'POST':
            file = request.files['csv-file']
            str_file_value = file.read().decode('utf-8')
            file_t = str_file_value.splitlines()
            reader = csv.reader(file_t, delimiter=',', quotechar='"')
            data_read = [row for row in reader]

            header = data_read[0]
                            
            data_read.pop(0)     

    return render_template("/reports/import.html", user=current_user, header=header, reader=data_read)

@reports_bp.route('/export', methods=['GET'])
# @roles_accepted('admin')
def reports():
    tables = db.engine.table_names()

    return render_template("/reports/export.html", user=current_user, tables=tables)

@reports_bp.route('/export', methods=['POST'])
# @roles_accepted('admin')
def reports_post():
    if request.method == 'POST':
        selectedtable = request.form.get('selecttable')
        whereclause = request.form.get('whereclause')
        
        result = db.engine.execute("select * from " + selectedtable + ' ' + whereclause)

        si = io.StringIO()
        cw = csv.writer(si, delimiter=",")
        cw.writerow(result.keys())
        cw.writerows(result.fetchall())
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=export.csv"
        output.headers["Content-type"] = "text/csv"
        return output


    tables = db.engine.table_names()

    return render_template("/reports/export.html", user=current_user, tables=tables)