import os
from pathlib import Path
import re
from prefect import task
from PIL import Image


@task
def generate_derivatives(config, input_file: str):

    current_dir = os.path.dirname(input_file)
    regex = re.compile(
        config['collection']['catalog_number_regex']
        + config['generate_derivatives']['regex'])

    for _, _, files in os.walk(current_dir):
        matches = [file for file in files if regex.match(file)]

    derivatives_to_add = {size: config
                          for size, config
                          in config['generate_derivatives']['sizes'].items()
                          if is_missing(matches, size)}

    for derivative in derivatives_to_add.keys():
        generate_derivative(
            input_file,
            derivative,
            derivatives_to_add[derivative])


def is_missing(matches, size):
    return not any(match['size'] == size for match in matches)


def generate_derivative(input_file, size, config):
    full_image_path = Path(input_file)
    derivative_file_name = full_image_path.stem \
        + '_' + size \
        + full_image_path.suffix
    derivative_path = full_image_path.parent.joinpath(derivative_file_name)

    try:
        img = Image.open(input_file)
        img.thumbnail((config['width'], config['width']))
        img.save(derivative_path)
        return derivative_path
    except Exception as e:
        print('Unable to create derivative:', e)
        return None
