from torch_web.collections import collections
from torch_web.workflows.workflows import torch_task
from PIL import Image


def is_portrait(image_path=None):
    try:
        with Image.open(image_path) as im:
            width, height = im.size
            if height > width:
                return True
            else:
                return False
    except Exception as e:
        print('Error: ', e)
        raise


@torch_task("Check Portrait Orientation")
def check_orientation(specimen: collections.Specimen):
    image_bytes = specimen.image_bytes()
    print('image bytes is', image_bytes)
    if not is_portrait(image_bytes):
        return f"Incorrect orientation"

    return {
        "Orientation": "Portrait"
    }
