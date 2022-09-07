from prefect import prefect, task
import os


@task
def read_dir(path: str):
    logger = prefect.context.get('logger')

    files = [os.path.join(os.path.abspath(path), file)
             for file in os.listdir(path)
             if os.path.isfile(os.path.join(path, file))]

    logger.info(f'Processing {len(files)} files...')

    return files
