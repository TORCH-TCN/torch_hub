from torch_web.collections import collections
from torch_web.workflows.workflows import torch_task

from PIL import Image, TiffImagePlugin
from PIL.ExifTags import TAGS


def cast(v):
    try:
        if isinstance(v, TiffImagePlugin.IFDRational):
            return float(v)
        elif isinstance(v, tuple):
            return tuple(cast(t) for t in v)
        elif isinstance(v, bytes):
            return v.decode(errors="replace")
        elif isinstance(v, dict):
            for kk, vv in v.items():
                v[kk] = cast(vv)
            return v
        else: return v
    except Exception as e:
        return None


@torch_task("Get EXIF Info")
def get_exif_data(specimen: collections.Specimen):
    """
    Extract EXIF data from an image.
    Args:
        image_path (str): Path to the image file.
    Returns:
        dict: A dictionary containing the extracted EXIF data.
    """

    # Open the image
    for img in specimen.images:
        if img.size == 'FULL':
            image = Image.open(img.image_bytes)

    # Extract EXIF data
    exif_data = image._getexif()

    # Create a dictionary to store the extracted data
    exif_info = {}
    if exif_data is not None:
        for k, v in exif_data.items():
            if k in TAGS:
                v = cast(v)
                if v is not None:
                    exif_info[TAGS[k]] = v

    return exif_info

## Example usage
#image_path = 'example.jpg'  # Replace with your own image file path
#exif_info = get_exif_data(image_path)

