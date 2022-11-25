from multiprocessing.dummy import freeze_support

from flask_mail import Mail

from torch import create_app, db, socketio
from torch.collections.collections import Collection
from torch.institutions.institutions import Institution
from torch.users.role import Role

app = create_app()
mail = Mail(app)


@app.before_first_request
def create_tables():
    db.create_all()


def check_init_db(flask_app):
    flask_app.app_context().push()
    create_tables()
    institutions = db.session.query(Institution).all()

    if len(institutions) == 0:
        print("Creating default institution...")
        default_institution = Institution(name="Default Institution", code="default")
        db.session.add(default_institution)
        db.session.commit()

    # test collection
    collections = db.session.query(Collection).all()

    if len(collections) == 0:
        print("Creating default collection...")
        default_collection = Collection(
            name="Default",
            code="DEFAULT",
            institution_id=1,
            workflow="process_specimen",
            collection_folder="Default",
        )
        db.session.add(default_collection)
        db.session.commit()

    # admin role

    roles = db.session.query(Role).all()

    if len(roles) == 0:
        print("Creating admin role...")
        admin_role = Role(name="admin", description="admin")
        db.session.add(admin_role)
        db.session.commit()


if __name__ == "__main__":
    freeze_support()

    check_init_db(app)
    # app.run(debug=True)
    socketio.run(app)
else:
    freeze_support()
    check_init_db(app)
