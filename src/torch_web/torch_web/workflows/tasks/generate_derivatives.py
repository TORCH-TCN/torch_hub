import os
import traceback
import requests

from pathlib import Path
from typing import Optional

from PIL import Image
from io import BytesIO
from torch_web.collections import collections
from torch_web.collections.collections import SpecimenImage
from torch_web.workflows.workflows import torch_task
from torch_web import db
from azure.storage.blob import BlobServiceClient


def parse_sizes(sizes):
    items = [item.strip() for item in sizes.split(",")]
    output_dict = {}

    # loop through the items
    for item in items:
      # split the item by colon and strip any whitespace
      key_value = [kv.strip() for kv in item.split(":")]
      # if there is only one element, it is the key and the value is None
      if len(key_value) == 1:
        output_dict[key_value[0]] = None
      # if there are two elements, they are the key and the value
      elif len(key_value) == 2:
        # try to convert the value to an integer
        try:
          value = int(key_value[1])
        # if it fails, use the original value as a string
        except ValueError:
          value = key_value[1]
        # add the key-value pair to the dictionary
        output_dict[key_value[0]] = value

    # print the output dictionary
    return output_dict


@torch_task("Generate Derivatives")
def generate_derivatives(specimen: collections.Specimen, sizes_to_generate):
    try:
        sizes = parse_sizes(sizes_to_generate)

        derivatives_to_add = {
            size: config
            for size, config in sizes.items()
            if not any(image.size == size for image in specimen.images)
        }

        result = {}
        for derivative in derivatives_to_add.keys():
            new_derivative = generate_derivative(specimen, derivative, derivatives_to_add[derivative])
            if new_derivative is not None:
                specimen.images.append(new_derivative)
                result[derivative] = {
                    "url": new_derivative.url,
                    "size": new_derivative.size,
                    "width": new_derivative.width,
                    "height": new_derivative.height
                }

        return result
    except Exception as e:
        return f"Unable to create derivatives: {e}"


def generate_derivative(specimen: collections.Specimen, size, width) -> Optional[collections.SpecimenImage]:
    full_image_path = Path(specimen.upload_path)
    derivative_file_name = full_image_path.stem + "_" + size + full_image_path.suffix
    derivative_path = str(specimen.collection_id) + '/' + str(specimen.id) + '/' + derivative_file_name

    try:
        img_bytes = specimen.image_bytes()
        if img_bytes is None:
            img_bytes = BytesIO(requests.get(specimen.upload_path, stream=True).content)
        img = Image.open(img_bytes)
        print('opened')

        if width is not None:
            img.thumbnail((width, width))

        # img.save(derivative_path)
        blob_service_client = BlobServiceClient.from_connection_string(os.environ.get("AZURE_STORAGE_CONNECTION_STRING"))
        blob_client = blob_service_client.get_blob_client(container='torchhub', blob=derivative_path)
        image_stream = BytesIO()
        img.save(image_stream, format='JPEG')
        print('saved')
        image_stream.seek(0)
        blob_client.upload_blob(image_stream.read(), overwrite=True)
        print('uploaded')

        specimen_image = SpecimenImage(
            specimen_id=specimen.id,
            size=size,
            height=img.height,
            width=img.width,
            url=blob_client.url,
            external_url = blob_client.url
        )

        return specimen_image

    except Exception as e:
        print("Unable to create derivative:", traceback.format_exc())
        return None
