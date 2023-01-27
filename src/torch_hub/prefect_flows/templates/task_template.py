# This is a task template using Prefect
# A task file should be added to the prefect_flows/tasks folder

# Basic prefect imports:
import prefect
from prefect import get_run_logger, task
from prefect.orion.schemas.states import Failed

from torch_hub import save_specimen


@task
def task_template(specimen, app_config, flow_config):
    # get prefect log and task/flow info
    logger = get_run_logger()
    flow_run_id = prefect.context.get_run_context().task_run.flow_run_id.hex

    try:
        example_config = flow_config["EXAMPLE_CONFIG"]
        logger.info(f"Task using {specimen.name}, Flow ID {flow_run_id}, example flow config {example_config}...")

        # manipulate specimen and after that:
        save_specimen(specimen, app_config, flow_run_id)
    except Exception as e:
        # log which task failed
        save_specimen(specimen, app_config, flow_run_id, 'Failed', 'task_template')
        return Failed(message=f"task_template failed for {specimen.id}-{specimen.name}: {e}")
