from prefect import prefect, task
import os


@task
def log_new_file_name(new_path):
    logger = prefect.context.get('logger')

    logfile = os.path.dirname(new_path) + '\\newfiles.txt'
    with open(logfile, 'a') as log:
        log.write(new_path + '\n')

    logger.info(f'Wrote new file names to {logfile}')
