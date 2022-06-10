import json
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


with open("../shared/config/config.json",'r') as config:
    connection_string = json.load(config)["SQLALCHEMY_DATABASE_URI"]

engine = create_engine(connection_string)
session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = scoped_session(session)

Entity = declarative_base()
Entity.query = db.query_property()


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    Entity.metadata.create_all(bind=engine)
