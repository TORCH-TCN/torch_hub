import os

import prefect
from prefect import flow, get_run_logger
from prefect.orion.schemas.states import Failed

from torch_hub.prefect_flows.tasks import check_catalog_number, check_orientation, generate_derivatives, save_specimen, upload

@flow(name="Process Specimen", version=os.getenv("GIT_COMMIT_SHA"))
def process_specimen(collection, specimen, app_config):
    logger = get_run_logger()
    flow_run_id = prefect.context.get_run_context().flow_run.id.hex
    flow_run_state = prefect.context.get_run_context().flow_run.state_name

    try:
        logger.info(f"Saving {specimen.name} to database...")
        save_specimen(specimen, app_config, flow_run_id, flow_run_state)
        logger.info(f"{specimen.name} saved...")

        logger.info(f"Running check_catalog_number {specimen.name} (id:{specimen.id})...")
        specimen.catalog_number = check_catalog_number(collection, specimen, app_config)
        save_specimen(specimen, app_config, flow_run_id, flow_run_state)

        logger.info(f"Running check_orientation {specimen.name} (id:{specimen.id})...")
        check_orientation(specimen, app_config)

        logger.info(f"Running generate_derivatives {specimen.name} (id:{specimen.id})...")
        imgs = generate_derivatives(specimen, app_config)

        logger.info(f"Uploading image {specimen.name} (id:{specimen.id})...")
        for img in imgs:
            upload(collection, img)
            save_specimen_image(img, app_config)

        save_specimen(specimen, app_config, flow_run_id, "Completed")
    except Exception as e:
        logger.error(f"Error running process_specimen flow", exc_info=e)
        return Failed(message="Error running process_specimen flow")

# @task(name="test_task_error")
# def test_task(specimen: Specimen, config):
#     flow_run_id = prefect.context.get_run_context().task_run.flow_run_id.hex
#     try:
#         raise ValueError("test")
#     except:
#         save_specimen(specimen,config,flow_run_id,'Failed','test_task')
#         raise Exception("Error test_task")
