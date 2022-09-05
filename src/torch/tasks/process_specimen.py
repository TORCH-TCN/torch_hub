from asyncio import tasks
from prefect import flow, unmapped,task
import prefect
from torch.tasks.generate_derivatives import generate_derivatives
from torch.tasks.herbar import herbar
from torch.tasks.notification_hub import Notification
from torch.tasks.save_specimen import save_specimen
from torch.tasks.upload import upload
import os
import time
from prefect.task_runners import SequentialTaskRunner

@flow(name="Process Specimen",task_runner=SequentialTaskRunner, version=os.getenv("GIT_COMMIT_SHA"))
async def process_specimen(specimen, config):
    n = Notification(config=config)
    
    flow_run_id = prefect.context.get_run_context().flow_run.id.hex
    flow_run_state = prefect.context.get_run_context().flow_run.state_name
        
    try:
        save_specimen(specimen, config, flow_run_id, flow_run_state)
        id = specimen.id
        n.send(sdata(id,10))

        herbar(specimen,config)
        n.send(sdata(id,20))
        
        generate_derivatives(specimen, config)
        n.send(sdata(id,40))
        
        time.sleep(1)
        
        n.send(sdata(id,60))
        
        time.sleep(1)
        
        n.send(sdata(id,80))
        
        #upload.map(image=images, config=unmapped(config))
        
        n.send(sdata(id, 100, "Completed"))
        
    except:
        n.send(sdata(specimen.id, 100, "Failed"))
        raise
        

def sdata(id,progress,state = None,errors = None):
    state = state if state != None else "Running"
    errors = errors if errors != None else []
    return {"specimenid":id, "state":state, "progress": progress,"errors":errors}

@task
def test_task():
    try:
        raise ValueError("bad code")
    except:
        print("task error")
        raise

