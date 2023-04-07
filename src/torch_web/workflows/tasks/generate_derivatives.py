import json
from pathlib import Path
from typing import Optional

from PIL import Image
from torch_web.collections import collections
from torch_web.collections.collections import SpecimenImage
from torch_web.workflows.workflows import torch_task
from torch_web import db
from flask import current_app


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
        local_specimen = db.session.merge(specimen)  # thread-safe

        sizes = parse_sizes(sizes_to_generate)

        derivatives_to_add = {
            size: config
            for size, config in sizes.items()
            if not any(image.size == size for image in local_specimen.images)
        }

        for derivative in derivatives_to_add.keys():
            new_derivative = generate_derivative(local_specimen, derivative, derivatives_to_add[derivative])
            local_specimen.images.append(new_derivative)

        return local_specimen
    except Exception as e:
        return f"Unable to create derivatives: {e}"


def generate_derivative(specimen: collections.Specimen, size, width) -> Optional[collections.SpecimenImage]:
    full_image_path = Path(specimen.upload_path)
    derivative_file_name = full_image_path.stem + "_" + size + full_image_path.suffix
    derivative_path = str(full_image_path.parent.joinpath(derivative_file_name))

    try:
        img = Image.open(specimen.upload_path)

        if width is None:
            img.thumbnail((width, width))

        img.save(derivative_path)

        return SpecimenImage(
            specimen_id=specimen.id,
            size=size,
            height=width if width is not None else img.height,
            width=width if width is not None else img.width,
            url=derivative_path,
            external_url = derivative_path.replace(current_app.config['BASE_DIR'] + "\\", '').replace("\\", "/")
        )
    except Exception as e:
        print("Unable to create derivative:", e)
        return None
