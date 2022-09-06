from torch.collections.specimens import Specimen
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

def save_specimen(specimen:Specimen, config, flow_run_id, flow_run_state = None):

    engine = create_engine(config["SQLALCHEMY_DATABASE_URI_PREFECT"], future=True)
    
    with Session(engine) as session:
        #session_specimen = session.query(Specimen).filter_by(id=specimen.id)
        
        specimen.flow_run_id = flow_run_id
        specimen.flow_run_state = flow_run_state if flow_run_state != None else 'Running'
        
        session.add(specimen)
        
        session.commit()
        #session.expunge(specimen)
