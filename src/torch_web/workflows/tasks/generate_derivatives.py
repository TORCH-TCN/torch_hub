import json
from pathlib import Path
from typing import Optional

from PIL import Image
from torch_web.collections import specimens
from torch_web.collections.collections import SpecimenImage
from torch_web.workflows.workflows import torch_task
from torch_web import db


@torch_task("Generate Derivatives")
def generate_derivatives(specimen: specimens.Specimen, sizes_json):
    try:
        local_specimen = db.session.merge(specimen)  # thread-safe

        sizes = json.loads(sizes_json)

        derivatives_to_add = {
            size: config
            for size, config in sizes.items()
            if is_missing(local_specimen.images, size)
        }

        for derivative in derivatives_to_add.keys():
            new_derivative = generate_derivative(
                local_specimen, derivative, derivatives_to_add[derivative]["WIDTH"]
            )
            local_specimen.images.append(new_derivative)

        db.session.commit()

        return local_specimen
    except Exception as e:
        db.session.commit()
        return Failed(message=f"Unable to create derivatives for specimen {specimen.id}-{specimen.name}: {e}")


def is_missing(images, size):
    return not any(image.size == size for image in images)


def generate_derivative(specimen: specimens.Specimen, size, width) -> Optional[specimens.SpecimenImage]:
    full_image_path = Path(specimen.upload_path)
    derivative_file_name = full_image_path.stem + "_" + size + full_image_path.suffix
    derivative_path = str(full_image_path.parent.joinpath(derivative_file_name))

    try:
        img = Image.open(specimen.upload_path)

        if size != 'FULL':
            img.thumbnail((width, width))

        img.save(derivative_path)

        return SpecimenImage(
            specimen_id=specimen.id,
            size=size,
            height=width if size != 'FULL' else img.height,
            width=width if size != 'FULL' else img.width,
            url=derivative_path
        )
    except Exception as e:
        print("Unable to create derivative:", e)
        return None
