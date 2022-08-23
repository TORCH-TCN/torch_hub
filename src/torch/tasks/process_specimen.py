from prefect import flow, unmapped
import prefect
from torch.tasks.generate_derivatives import generate_derivatives
from torch.tasks.notification_hub import Notification
from torch.tasks.upload import upload
import time


@flow
def process_specimen(specimen, config):
    notification = Notification(config=config)
    
    #save specimens in different task (?)
    # notification.send({"specimenid":specimen.id, "state":"running", "progress": "10","errors":[]})

    flow_run_id = prefect.context.get_run_context().flow_run.id.hex

    images = generate_derivatives(specimen=specimen, config=config)

    notification.send({"specimenid":specimen.id, "state":"running", "progress": "20","errors":[]})
    
    time.sleep(3)
    
    notification.send({"specimenid":specimen.id, "state":"running", "progress": "40","errors":[]})
    
    time.sleep(3)
    
    notification.send({"specimenid":specimen.id, "state":"running", "progress": "60","errors":[]})
    
    time.sleep(3)
    
    notification.send({"specimenid":specimen.id, "state":"running", "progress": "80","errors":[]})
    
    time.sleep(3)
    
    notification.send({"specimenid":specimen.id, "state":"finished", "progress": "100","errors":[]})

    #upload.map(image=images, config=unmapped(config))
