from asyncio import tasks
from prefect import flow, unmapped,task
import prefect
from torch.tasks.generate_derivatives import generate_derivatives
from torch.tasks.notification_hub import Notification
from torch.tasks.save_specimen import save_specimen
from torch.tasks.upload import upload
import os
import time
from prefect.task_runners import SequentialTaskRunner

@flow(name="Process Specimen",task_runner=SequentialTaskRunner, version=os.getenv("GIT_COMMIT_SHA"))
async def process_specimen(specimen, config):
    notification = Notification(config=config)
    
    flow_run_id = prefect.context.get_run_context().flow_run.id.hex
    #flow_run_state = prefect.context.get_run_context().flow_run.state_name
    #todo get tasks from flow to calculate progress
    
    save_specimen(specimen, config)
    # notification.send({"specimenid":specimen.id, "state":"running", "progress": "10","errors":[]})
    
    generate_derivatives(specimen, config)

    # for each task check state and save new flow_run_state
    notification.send({"specimenid":specimen.id, "state":"running", "progress": "20","errors":[]})
    
    test_task()
    
    notification.send({"specimenid":specimen.id, "state":"running", "progress": "40","errors":[]})
    
    time.sleep(1)
    
    notification.send({"specimenid":specimen.id, "state":"running", "progress": "60","errors":[]})
    
    time.sleep(1)
    
    notification.send({"specimenid":specimen.id, "state":"running", "progress": "80","errors":[]})
    
    time.sleep(1)
    
    notification.send({"specimenid":specimen.id, "state":"finished", "progress": "100","errors":[]})

    #upload.map(image=images, config=unmapped(config))


@task
def test_task():
    try:
        raise ValueError("bad code")
    except:
        print("task error")

