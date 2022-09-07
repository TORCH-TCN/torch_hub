from multiprocessing.dummy import freeze_support
from prefect.agent.docker import DockerAgent


if __name__ == "__main__":
    freeze_support()
    DockerAgent().start()
