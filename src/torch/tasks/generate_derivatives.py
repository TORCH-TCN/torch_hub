import os
from pathlib import Path
import re
from prefect import task
from PIL import Image

from torch.collections.specimens import Specimen, SpecimenImage


@task
def generate_derivatives(specimen: Specimen, config):
    images = SpecimenImage.query.

    for _, _, files in os.walk(current_dir):
        matches = [file for file in files if regex.match(file)]

    derivatives_to_add = {
        size: config
        for size, config in config["generate_derivatives"]["sizes"].items()
        if is_missing(matches, size)
    }

    for derivative in derivatives_to_add.keys():
        new_file = generate_derivative(
            specimen, derivative, derivatives_to_add[derivative]
        )
        matches.append(new_file)

    return matches


def is_missing(matches, size):
    return not any(match["size"] == size for match in matches)


def generate_derivative(specimen: Specimen, size, config) -> SpecimenImage:
    full_image_path = Path(specimen.upload_path)
    derivative_file_name = full_image_path.stem + "_" + size + full_image_path.suffix
    derivative_path = full_image_path.parent.joinpath(derivative_file_name)

    try:
        img = Image.open(specimen.upload_path)
        img.thumbnail((config["width"], config["width"]))
        img.save(derivative_path)
        return SpecimenImage(
            specimen_id=specimen.id,
            size=size,
            height=config["width"],
            width=config["width"],
            url=derivative_path
        )
    except Exception as e:
        print("Unable to create derivative:", e)
        return None
