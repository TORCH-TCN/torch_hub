import os
from prefect import prefect, task


@task
def log_new_file_name(directory, new_path):
    logger = prefect.context.get('logger')

    logfile = os.path.abspath(directory) + '/newfiles.txt'
    with open(logfile, 'a') as log:
        log.write(new_path + '\n')

    logger.info(f'Wrote new file names to {logfile}')
