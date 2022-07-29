from multiprocessing.dummy import freeze_support
import threading
import time
from flask_socketio import SocketIO
from flask_mail import Mail
from prefect.agent.docker import DockerAgent
from prefect.cli.server import start as start_prefect_server
import requests
from torch import create_app, db, client
from torch.institutions.institutions import Institution

# Make sure to run 'prefect backend server' before running this


def wait_for_prefect_server():
    for i in range(120):
        try:
            response = requests.get(
                "http://localhost:4200/.well-known/apollo/server-health"
            )
            if response.status_code == 200:
                print("Prefect Server is UP")
                break
            else:
                time.sleep(1)
        except requests.RequestException:
            time.sleep(1)


app = create_app()
mail = Mail(app)
socketio = SocketIO(app)


def check_default_institution(app):
    app.app_context().push()
    institutions = Institution.query.all()

    if len(institutions) == 0:
        print("Creating default tenant...")
        default_institution = Institution(name="Default Institution", code="default")
        db.session.add(default_institution)
        db.session.commit()

    if len(client.get_available_tenants()) == 0:
        print("Registering default tenant with prefect...")
        client.create_tenant("default")


if __name__ == "__main__":
    freeze_support()

    server = threading.Thread(target=lambda: start_prefect_server())
    server.daemon = True
    server.start()
    wait_for_prefect_server()

    ui = threading.Thread(target=lambda: socketio.run(app))
    ui.daemon = True
    ui.start()

    check_default_institution(app)

    DockerAgent().start()
