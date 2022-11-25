from prefect import task
import prefect
from torch.collections.specimens import Specimen, is_portrait
from torch.prefect_flows.tasks.save_specimen import save_specimen
from prefect.orion.schemas.states import Failed


@task
def check_orientation(specimen: Specimen, config):
    flow_run_id = prefect.context.get_run_context().task_run.flow_run_id.hex

    if is_portrait(specimen.upload_path):
        save_specimen(specimen, config, flow_run_id)
    else:
        save_specimen(specimen, config, flow_run_id, 'Failed', 'check_orientation')
        return Failed(message=f"Specimen {specimen.id}-{specimen.name} incorrect orientation")
