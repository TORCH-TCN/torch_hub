import os

import prefect
from prefect import flow, get_run_logger
from prefect.orion.schemas.states import Failed
from torch_web.prefect_flows.tasks import check_catalog_number, check_orientation, generate_derivatives, save_specimen, upload


@flow(name="Process Specimen", version=os.getenv("GIT_COMMIT_SHA"))
def execute(collection, specimen, app_config, progress):
    logger = get_run_logger()
    flow_run_id = prefect.context.get_run_context().flow_run.id.hex
    flow_run_state = prefect.context.get_run_context().flow_run.state_name
    if progress:
        task = progress.add_task(specimen.name, total=5)

    def log(message, advance=False):
        # if logger:
            # logger.info(message)
        if progress:
            progress.console.log(message)
            if advance:
                progress.advance(task)


    try:
        log(f"Saving to database...")
        save_specimen.save_specimen(specimen, app_config, flow_run_id, flow_run_state)
        log(f"Saved!", True)

        log(f"Running check_catalog_number...")
        specimen.catalog_number = check_catalog_number.check_catalog_number(collection, specimen, app_config)
        save_specimen.save_specimen(specimen, app_config, flow_run_id, flow_run_state)
        log(f"check_catalog_number complete...", True)

        log(f"Running check_orientation...")
        check_orientation.check_orientation(specimen, app_config)
        log(f"check_orientation complete...", True)

        log(f"Running generate_derivatives...")
        imgs = generate_derivatives.generate_derivatives(specimen, app_config)
        log(f"generate_derivatives complete...", True)

        for img in imgs:
            log(f"Uploading image {img.size}...")
            upload.upload.submit(collection, img, app_config)

        save_specimen.save_specimen(specimen, app_config, flow_run_id, "Completed")
        log(f"Complete!", True)
        
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
