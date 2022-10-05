import prefect
import json
import os
from prefect import flow, task, get_run_logger
from prefect.task_runners import SequentialTaskRunner
from prefect.orion.schemas.states import Failed
from tasks.generate_derivatives import generate_derivatives
from tasks.herbar import herbar
from tasks.save_specimen import save_specimen


@flow(name="Process Specimen",task_runner=SequentialTaskRunner, version=os.getenv("GIT_COMMIT_SHA"))
def process_specimen(specimen, app_config):

    with open(os.path.join(app_config["BASE_DIR"],'prefect_flows','configs','process_specimen_config.json'), 'r') as f:
        flow_config = json.load(f)
    
    logger = get_run_logger()
    flow_run_id = prefect.context.get_run_context().flow_run.id.hex
    flow_run_state = prefect.context.get_run_context().flow_run.state_name
        
    try:
        logger.info(f"Saving {specimen.name} to database...")
        save_specimen(specimen, app_config, flow_run_id, flow_run_state)
        logger.info(f"{specimen.name} saved...")

        logger.info(f"Running herbar {specimen.name} (id:{specimen.id})...")
        herbar(specimen,app_config,flow_config)
        
        logger.info(f"Running generate_derivatives {specimen.name} (id:{specimen.id})...")
        generate_derivatives(specimen, flow_config)
        
        save_specimen(specimen, app_config, flow_run_id, "Completed")
    except:
        logger.error(f"Error running process_specimen flow")
        return Failed(message="Error running process_specimen flow")
        

# @task(name="test_task_error")
# def test_task(specimen: Specimen, config):
#     flow_run_id = prefect.context.get_run_context().task_run.flow_run_id.hex
#     try:
#         raise ValueError("test")
#     except:
#         save_specimen(specimen,config,flow_run_id,'Failed','test_task')
#         raise Exception("Error test_task")