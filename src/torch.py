from multiprocessing.dummy import freeze_support

from flask_mail import Mail
from torch import create_app, db, socketio
from torch.institutions.institutions import Institution
from torch.users.user import User


app = create_app()
mail = Mail(app)

@app.before_first_request
def create_tables():
    db.create_all()


def check_default_institution(app):
    app.app_context().push()
    create_tables()
    institutions = db.session.query(Institution).all()
    
    if len(institutions) == 0:
        print("Creating default institution...")
        default_institution = Institution(name="Default Institution", code="default")
        db.session.add(default_institution)
        db.session.commit()

    

if __name__ == "__main__":
    freeze_support()

    check_default_institution(app)
    socketio.run(app)
