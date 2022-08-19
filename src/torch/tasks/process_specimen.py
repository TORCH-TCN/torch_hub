from prefect import flow, unmapped
import prefect
from torch.tasks.generate_derivatives import generate_derivatives
from torch.tasks.notification_hub import Notification
from torch.tasks.upload import upload


@flow
def process_specimen(specimen, config):
    notification = Notification(config=config)
    #print(prefect.context.get("flow_run_id"))

    images = generate_derivatives(specimen=specimen, config=config)
    notification.send({
        "specimenid":specimen.id,
        "completed_task":"generate_derivatives",
        "errors":[]
        })

    #task1
    #task2
    #task3

    #upload.map(image=images, config=unmapped(config))
