from prefect import get_run_logger, task
import os


@task
def read_dir(path: str):
    logger = get_run_logger()

    files = [os.path.join(os.path.abspath(path), file)
             for file in os.listdir(path)
             if os.path.isfile(os.path.join(path, file))]

    logger.info(f'Processing {len(files)} files...')

    return files
