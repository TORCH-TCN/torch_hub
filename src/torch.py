from multiprocessing.dummy import freeze_support
import socket
import threading
import time
from flask_socketio import SocketIO
from flask_mail import Mail
from prefect.agent.docker import DockerAgent
from prefect.cli.server import start as start_prefect_server
from torch import create_app


def wait_for_prefect_server():
    for i in range(120):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect(("127.0.0.1", int(4200)))
            s.shutdown(socket.SHUT_RDWR)
            print("Prefect Server is UP")
        except OSError:
            time.sleep(1)
            print("Prefect Server is not up yet")
        finally:
            s.close()


app = create_app()
mail = Mail(app)
socketio = SocketIO(app)

if __name__ == "__main__":
    freeze_support()

    server = threading.Thread(target=lambda: start_prefect_server())
    server.daemon = True
    server.start()
    wait_for_prefect_server()

    ui = threading.Thread(target=lambda: socketio.run(app))
    ui.daemon = True
    ui.start()

    time.sleep(5)  # make sure server is ready

    DockerAgent().start()
