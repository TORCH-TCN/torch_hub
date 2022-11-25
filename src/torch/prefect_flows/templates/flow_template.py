import os
import json
# This is a flow template using Prefect flow
# A flow file should be added to the prefect_flows folder
# Basic prefect imports:
import prefect
from prefect import flow, get_run_logger
from prefect.orion.schemas.states import Failed
from torch.prefect_flows.tasks.save_specimen import save_specimen

from torch.prefect_flows.templates.task_template import task_template


# to declare a new flow:
# torch is using specimen and app_config as default parameters
@flow(name="Flow template")
def flow_template(specimen, app_config):
    # get prefect log and flow info
    logger = get_run_logger()
    flow_run_id = prefect.context.get_run_context().flow_run.id.hex
    flow_run_state = prefect.context.get_run_context().flow_run.state_name

    # load flow config (if exists)
    with open(os.path.join(app_config["BASE_DIR"], 'prefect_flows', 'configs', 'flow_template_config.json'), 'r') as f:
        flow_config = json.load(f)

    # main block, catch the exception here and manually set the Failed status
    try:
        example_config = flow_config["EXAMPLE_CONFIG"]
        logger.info(
            f"Flow using {specimen.name}, "
            f"Flow ID {flow_run_id}, "
            f"current state {flow_run_state}, "
            f"example flow config {example_config}...")

        # call save_specimen between tasks, after manipulate specimen object or to save flow info
        save_specimen(specimen, app_config, flow_run_id, flow_run_state)

        # call Prefect task
        task_template(specimen, app_config, flow_config)

        # log completed state calling save_specimen
        save_specimen(specimen, app_config, flow_run_id, "Completed")
    except Exception as e:
        logger.error(f"Error running flow_template", exc_info=e)
        return Failed(message="Error running flow_template")
