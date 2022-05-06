from pathlib import Path
from prefect import prefect, task

@task
def log_new_file_name(new_path):
    logger = prefect.context.get('logger')

    logfile = Path(new_path).parent / 'newfiles.txt'
    with open(logfile, 'a') as log:
        log.write(new_path + '\n')

    logger.info(f'Wrote new file names to {logfile}')
