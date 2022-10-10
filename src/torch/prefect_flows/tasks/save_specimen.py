from torch.collections.specimens import Specimen, SpecimenImage
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

def save_specimen(specimen:Specimen, config, flow_run_id, flow_run_state = None, failed_task = None):
        
    engine = create_engine(config["SQLALCHEMY_DATABASE_URI"], future=True)
    
    with Session(engine) as session:

        try:
            local_specimen = session.merge(specimen) #thread-safe

            local_specimen.flow_run_id = flow_run_id
            local_specimen.flow_run_state = flow_run_state if flow_run_state != None else 'Running'
            local_specimen.failed_task = failed_task
                        
            session.add(local_specimen)
            session.commit()

            return local_specimen
        except:
            session.rollback()
            raise Exception("Error updating database")
        finally:
            session.close()



def save_specimen_image(image:SpecimenImage, config):
        
    engine = create_engine(config["SQLALCHEMY_DATABASE_URI"], future=True)
    
    with Session(engine) as session:

        try:
            local_image = session.merge(image) #thread-safe
     
            session.add(local_image)
            session.commit()

            return local_image
        except:
            session.rollback()
            raise Exception("Error updating database")
        finally:
            session.close()