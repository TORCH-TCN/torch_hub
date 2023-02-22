from apiflask import APIBlueprint
from flask import make_response, render_template, request
from flask_security import current_user, roles_accepted

reports_bp = APIBlueprint("reports", __name__, url_prefix="/reports")


@reports_bp.get("/import")
@roles_accepted('admin')
def csvfiles_import():

    header = []
    data_read = []

    return render_template(
        "/reports/import.html", user=current_user, header=header, reader=data_read
    )


@reports_bp.post("/import")
@roles_accepted('admin')
def csvfiles_import_post():
    result = import_csv(request.files["csv-file"])
    return render_template(
        "/reports/import.html", user=current_user, header=result.header, reader=result.data_read
    )


@reports_bp.get("/export")
@roles_accepted('admin')
def reports():
    return render_template("/reports/export.html", user=current_user, tables=get_reports())


@reports_bp.post("/export")
@roles_accepted('admin')
def reports_post():
    selectedtable = request.form.get("selecttable")
    whereclause = request.form.get("whereclause")

    output = make_response(run_report(selectedtable, whereclause))
    output.headers["Content-Disposition"] = "attachment; filename=export.csv"
    output.headers["Content-type"] = "text/csv"
    return output
