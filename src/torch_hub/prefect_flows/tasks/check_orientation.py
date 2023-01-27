from prefect import task
import prefect
from torch_hub.collections import specimens
from prefect.orion.schemas.states import Failed


@task
def check_orientation(specimen: specimens.Specimen, config):
    flow_run_id = prefect.context.get_run_context().task_run.flow_run_id.hex

    if is_portrait(specimen.upload_path):
        save_specimen(specimen, config, flow_run_id)
    else:
        save_specimen(specimen, config, flow_run_id, 'Failed', 'check_orientation')
        return Failed(message=f"Specimen {specimen.id}-{specimen.name} incorrect orientation")
