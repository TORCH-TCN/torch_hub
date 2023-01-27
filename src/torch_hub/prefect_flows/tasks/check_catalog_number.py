import ast
import re

import prefect
from prefect import task
from prefect.orion.schemas.states import Failed

from torch_hub.collections import specimens


@task
def check_catalog_number(collection, specimen: specimens.Specimen, app_config):
    flow_run_id = prefect.context.get_run_context().task_run.flow_run_id.hex

    try:
        catalog_number = specimen.name
        if collection.catalog_number_regex is not None:
            for x in ast.literal_eval(collection.catalog_number_regex):
                c = re.search(x, specimen.name)
                if c is not None and c.group("catNum") is not None:
                    catalog_number = c.group("catNum")
                    break

        return catalog_number
    except Exception as e:
        save_specimen(specimen, app_config, flow_run_id, 'Failed', 'check_catalog_number')
        return Failed(message=f"Specimen {specimen.id}-{specimen.name} incorrect catalog number: {e}")
