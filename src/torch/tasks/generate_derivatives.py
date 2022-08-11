from pathlib import Path
from prefect import task
from PIL import Image

from torch.collections.specimens import Specimen, SpecimenImage
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


@task
def generate_derivatives(specimen: Specimen, config):
    derivatives_to_add = {
        size: config
        for size, config in config["GENERATE_DERIVATIVES"]["SIZES"].items()
        if is_missing(specimen.images, size)
    }

    for derivative in derivatives_to_add.keys():
        new_derivative = generate_derivative(
            specimen, derivative, derivatives_to_add[derivative]
        )
        specimen.images.append(new_derivative)

    engine = create_engine(config["SQLALCHEMY_DATABASE_URI_PREFECT"], future=True)
    with Session(engine) as session:
        session.add(specimen)
        session.commit()

    return specimen.images


def is_missing(images, size):
    return not any(image.size == size for image in images)


def generate_derivative(specimen: Specimen, size, config) -> SpecimenImage:
    full_image_path = Path(specimen.upload_path)
    derivative_file_name = full_image_path.stem + "_" + size + full_image_path.suffix
    derivative_path = str(full_image_path.parent.joinpath(derivative_file_name))

    try:
        img = Image.open(specimen.upload_path)
        
        if size != 'FULL':
            img.thumbnail((config["WIDTH"], config["WIDTH"]))
        
        img.save(derivative_path)
        
        return SpecimenImage(
            specimen_id=specimen.id,
            size=size,
            height=config["WIDTH"] if size != 'FULL' else img.height,
            width=config["WIDTH"] if size != 'FULL' else img.width,
            url=derivative_path
        )
    except Exception as e:
        print("Unable to create derivative:", e)
        return None
