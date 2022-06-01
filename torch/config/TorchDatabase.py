from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Entity = declarative_base()


class TorchDatabase:
    def __init__(self, connectionString) -> None:
        self.engine = create_engine(connectionString)
        self.Session = sessionmaker(self.engine)
