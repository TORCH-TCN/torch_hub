from torch_hub.collections import specimens
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


def save_specimen(specimen: specimens.Specimen, config, flow_run_id=None, flow_run_state=None, failed_task=None):
    engine = create_engine(config["SQLALCHEMY_DATABASE_URI"], future=True)

    with Session(engine) as session:

        try:
            local_specimen = session.merge(specimen)  # thread-safe

            if flow_run_id is not None:
                local_specimen.flow_run_id = flow_run_id

            local_specimen.flow_run_state = flow_run_state if flow_run_state is not None else 'Running'
            local_specimen.failed_task = failed_task

            session.add(local_specimen)
            session.commit()

            return local_specimen
        except Exception as e:
            session.rollback()
            raise Exception(f"Error updating database: {e}")
        finally:
            session.close()


def save_specimen_image(image: specimens.SpecimenImage, config):
    engine = create_engine(config["SQLALCHEMY_DATABASE_URI"], future=True)

    with Session(engine) as session:

        try:
            local_image = session.merge(image)  # thread-safe

            session.add(local_image)
            session.commit()

            return local_image
        except Exception as e:
            session.rollback()
            raise Exception(f"Error updating database: {e}")
        finally:
            session.close()
