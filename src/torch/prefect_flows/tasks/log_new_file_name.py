import os
from prefect import task, get_run_logger


@task
def log_new_file_name(directory, new_path):
    logger = get_run_logger()

    logfile = os.path.abspath(directory) + '/newfiles.txt'
    with open(logfile, 'a') as log:
        log.write(new_path + '\n')

    logger.info(f'Wrote new file names to {logfile}')
