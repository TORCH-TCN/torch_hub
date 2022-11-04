import re
from prefect import task
import prefect
from torch.collections.collections import Collection
from torch.collections.specimens import Specimen
from torch.prefect_flows.tasks.save_specimen import save_specimen
from prefect.orion.schemas.states import Failed


def match_catalog_number(catalog_number_regex, specimen):
    txt = Specimen.name
    pattern = Collection.catalog_number_regex
    
    for x in range(len(pattern)):
        print(pattern[x])

    #x = re.search(pattern, txt)
    #print(x.group("catNum"))

    specimen.catalog_number = "catNum"

@task
def check_catalog_number(collection: Collection, specimen: Specimen, config):

    flow_run_id = prefect.context.get_run_context().task_run.flow_run_id.hex

    try:
        if match_catalog_number(collection.catalog_number_regex, specimen): #check if catalog_number has been saved
            save_specimen(specimen,config,flow_run_id)
        else:
            save_specimen(specimen,config,flow_run_id,'Failed','check_catalog_number')
            return Failed(message=f"Specimen {specimen.id}-{specimen.name} incorrect catalog number")

    except:
        save_specimen(specimen,config,flow_run_id,'Failed','check_catalog_number')
        return Failed(message=f"Specimen {specimen.id}-{specimen.name} incorrect catalog number")


        
        