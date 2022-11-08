import re
from prefect import task
import prefect
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from torch.collections.specimens import Specimen
from torch.prefect_flows.tasks.save_specimen import save_specimen
from prefect.orion.schemas.states import Failed
import ast

@task
def check_catalog_number(collection, specimen: Specimen, app_config):
    
    flow_run_id = prefect.context.get_run_context().task_run.flow_run_id.hex
    
    try:
        catalog_number = specimen.name
        if collection.catalog_number_regex != None:
            for x in ast.literal_eval(collection.catalog_number_regex):
                c = re.search(x, specimen.name)
                if c != None and c.group("catNum") != None:
                    catalog_number = c.group("catNum")
                    break
        
        return catalog_number
    except:
        save_specimen(specimen,app_config,flow_run_id,'Failed','check_catalog_number')
        return Failed(message=f"Specimen {specimen.id}-{specimen.name} incorrect catalog number")
        


        
        