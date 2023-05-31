import os

from dotenv import load_dotenv
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def init_db():
    connection_string = os.environ.get("TORCH_HUB_DATABASE_URI")
    metadata = MetaData()
    engine = create_engine(connection_string)
    metadata.create_all(engine)
    #
    # with Session(engine) as session:
    #     institutions = session.query(Institution).all()
    #
    #     if len(institutions) == 0:
    #         print("Creating default institution...")
    #         default_institution = Institution(name="Default Institution", code="default")
    #         session.add(default_institution)
    #         session.commit()
    #
    #     # test collection
    #     collections = session.query(Collection).all()
    #
    #     if len(collections) == 0:
    #         print("Creating default collection...")
    #         default_collection = Collection(
    #             name="Default",
    #             code="DEFAULT",
    #             institution_id=1,
    #             workflow="process_specimen",
    #             collection_folder="Default",
    #         )
    #         session.add(default_collection)
    #         session.commit()
    #
    #     # admin role
    #
    #     roles = session.query(Role).all()
    #
    #     if len(roles) == 0:
    #         print("Creating admin role...")
    #         admin_role = Role(name="admin", description="admin")
    #         session.add(admin_role)
    #         session.commit()

    return sessionmaker(engine)


load_dotenv()

Base = declarative_base()
db = init_db()
# Base.query = db().query_property()

basedir = os.path.abspath(os.path.dirname(__file__))
