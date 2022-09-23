from prefect import flow, task, get_run_logger, unmapped
import prefect
from torch.collections.specimens import Specimen
from torch.tasks.generate_derivatives import generate_derivatives
from torch.tasks.herbar import herbar
from torch.tasks.notification_hub import Notification
from torch.tasks.save_specimen import save_specimen
from torch.tasks.upload import upload
import os
from prefect.task_runners import SequentialTaskRunner
from multiprocessing import Process

@flow(name="Process Specimen",task_runner=SequentialTaskRunner, version=os.getenv("GIT_COMMIT_SHA"))
async def process_specimen(specimen, config):
    
    n = Notification(config=config)
    logger = get_run_logger()
    flow_run_id = prefect.context.get_run_context().flow_run.id.hex
    flow_run_state = prefect.context.get_run_context().flow_run.state_name
        
    try:
        logger.info(f"Saving {specimen.name} to database...")
        save_specimen(specimen, config, flow_run_id, flow_run_state)
        id = specimen.id
        n.send(sdata(specimen,50))

        # logger.info(f"Running herbar {specimen.name} (id:{specimen.id})...")
        # herbar(specimen,config)
        # n.send(sdata(id,20))

        logger.info("Simulating error for testing purposes")
        # test_task(specimen,config)
        
        logger.info(f"Running generate_derivatives {specimen.name} (id:{specimen.id})...")
        generate_derivatives(specimen, config)
        #n.send(sdata(id,40))
        
        logger.info(f"Running upload {specimen.name} (id:{specimen.id})...")
        save_specimen(specimen, config, flow_run_id, "Completed")
        #upload.map(image=specimen.images, config=unmapped(config))
        #save_specimen(specimen, config, flow_run_id, flow_run_state) #todo solve db locked issue
        n.send(sdata(specimen, 100, "Completed"))
    except:
        logger.error(f"Error running process_specimen flow")
        n.send(sdata(specimen, 100, "Failed"))
        

def sdata(specimen,progress,state = None,errors = None):
    state = state if state != None else "Running"
    errors = errors if errors != None else []
    return {"id":specimen.id, "name": specimen.name, "upload_path": specimen.upload_path, "flow_run_state":state, "progress": progress,"errors":errors}


@task(name="test_task_error")
def test_task(specimen: Specimen, config):
    flow_run_id = prefect.context.get_run_context().task_run.flow_run_id.hex
    try:
        raise ValueError("test")
    except:
        save_specimen(specimen,config,flow_run_id,'Failed','test_task')
        raise Exception("Error test_task")