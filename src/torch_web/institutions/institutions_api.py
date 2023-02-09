from flask import Blueprint, jsonify, render_template, request
from flask_security import current_user
from torch_web.institutions import institutions
from rich.console import Console
from rich.table import Table


institutions_bp = Blueprint("institutions", __name__, url_prefix="/institutions")


@institutions_bp.get("/")
def institutions_get():
    return render_template(
        "/institutions/institutions.html", user=current_user, institutions=institutions.get_institutions()
    )


@institutions_bp.cli.command("list")
def list_institutions():
    result = institutions.get_institutions()
    table = Table(title="Current Institutions")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Code", style="green")

    for i in result:
        table.add_row(str(i.id), i.name, i.code)

    Console().print(table)
    

@institutions_bp.post("/")
def post_institution():
    name = request.form.get("institution")
    code = request.form.get("code")
    institutions.create_institution(name, code)
    return institutions.get_institutions()


@institutions_bp.delete("/<institution_id>")
def delete(institution_id):
    institutions.delete_institution(institution_id)
    return jsonify({})
