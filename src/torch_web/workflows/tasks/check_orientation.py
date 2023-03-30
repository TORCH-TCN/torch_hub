from prefect import task
import prefect
from torch_web.collections import specimens
from prefect.orion.schemas.states import Failed
from torch_web.prefect_flows.tasks import save_specimen


@task
def check_orientation(specimen: specimens.Specimen, config):
    flow_run_id = prefect.context.get_run_context().task_run.flow_run_id.hex

    if specimens.is_portrait(specimen.upload_path):
        save_specimen.save_specimen(specimen, config, flow_run_id)
    else:
        save_specimen.save_specimen(specimen, config, flow_run_id, 'Failed', 'check_orientation')
        return Failed(message=f"Specimen {specimen.id}-{specimen.name} incorrect orientation")
