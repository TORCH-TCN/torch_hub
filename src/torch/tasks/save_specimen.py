from torch.collections.specimens import Specimen
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import prefect
from prefect import task

@task
def save_specimen(specimen:Specimen, config):

    specimen.flow_run_id = prefect.context.get_run_context().task_run.flow_run_id.hex
    # specimen.flow_run_state = prefect.context.get_run_context()
    
    engine = create_engine(config["SQLALCHEMY_DATABASE_URI_PREFECT"], future=True)
    
    with Session(engine) as session:
        session.add(specimen)
        session.commit()

        return specimen.images