from multiprocessing.dummy import freeze_support
from prefect.agent.local import LocalAgent


if __name__ == "__main__":
    freeze_support()

    LocalAgent().start()
