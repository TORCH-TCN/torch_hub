import click

from apiflask import APIBlueprint
from flask import Blueprint, make_response, render_template, request
from flask_security import current_user
from torch_web.reports import reports
from rich.console import Console
from rich.table import Table

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")

@reports_bp.get('/')
def reports_get():
    result = reports.get_reports()
    return result


@reports_bp.cli.command("list")
def list_reports():
    result = reports.get_reports()
    table = Table(title="Source Tables")
    table.add_column("Name", style="cyan")
    table.add_column("Dimensions", style="magenta")
    table.add_column("Measures", style="green")

    for i in result:
        dimensions = [ f'{dim["totable"]} ({dim["fromcolumn"]} -> {dim["tocolumn"]})' for dim in i["dimensions"] ]
        measures = [ fact["column"] for fact in i["facts"] ]
        table.add_row(i["name"], '\r\n'.join(dimensions), '\r\n'.join(measures))

    Console().print(table)  
    

@reports_bp.get("/import")
def csvfiles_import():

    header = []
    data_read = []

    return render_template(
        "/reports/import.html", user=current_user, header=header, reader=data_read
    )


@reports_bp.post("/import")
def csvfiles_import_post():
    result = import_csv(request.files["csv-file"])
    return render_template(
        "/reports/import.html", user=current_user, header=result.header, reader=result.data_read
    )

    
@reports_bp.cli.command("export")
@click.argument("reportname")
@click.argument("output", type=click.Path())
def export_reports(reportname, output):
    result = reports.run_report(reportname, "")
    with open(output, "w") as csv:
        csv.write(result)
    

@reports_bp.get("/export")
def reports_export():
    return render_template("/reports/export.html", user=current_user, tables=get_reports())


@reports_bp.post("/export")
def reports_post():
    selectedtable = request.form.get("selecttable")
    whereclause = request.form.get("whereclause")

    output = make_response(run_report(selectedtable, whereclause))
    output.headers["Content-Disposition"] = "attachment; filename=export.csv"
    output.headers["Content-type"] = "text/csv"
    return output
