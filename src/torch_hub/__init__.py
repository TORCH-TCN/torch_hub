import os

from dotenv import load_dotenv
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()
metadata = MetaData()

Base = declarative_base(metadata=metadata)
db = SQLAlchemy(metadata=metadata)
Base.query = db.session.query_property()

basedir = os.path.abspath(os.path.dirname(__file__))
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
