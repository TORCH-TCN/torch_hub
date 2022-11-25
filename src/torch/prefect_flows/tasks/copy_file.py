from prefect import get_run_logger, task
import shutil
import os


@task
def copy_file(path: str):
    logger = get_run_logger()

    split_path = os.path.splitext(path)
    logger.info(f'Processing {split_path}...')
    new_file_name = split_path[0] + '-copy' + split_path[1]
    shutil.copyfile(path, new_file_name)

    return new_file_name
