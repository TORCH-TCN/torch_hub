from prefect import task
from PIL import Image
import prefect

from torch.collections.specimens import Specimen, SpecimenImage
from torch.tasks.save_specimen import save_specimen

@task
def check_orientation(specimen: Specimen, config):
    flow_run_id = prefect.context.get_run_context().task_run.flow_run_id.hex

    if is_portrait(path=specimen.upload_path):
        save_specimen(specimen,config,flow_run_id)
    else:
        save_specimen(specimen,config,flow_run_id,'Failed','check_orientation')
        # TODO flag and log image as incorrect orientation so the uploader can fix and re-upload
        raise

def is_portrait(path=None):
    with Image.open(path) as im:
        width, height = im.size
        if height > width:
            return True
        else:
            return False