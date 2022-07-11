from prefect import Flow, Parameter

from tasks.read_dir import read_dir
from tasks.copy_file import copy_file
from tasks.log_new_file_name import log_new_file_name


with Flow("process-file") as process_file:
    path = Parameter("path", required=True)

    files = read_dir(path)
    new_path = copy_file.map(files)
    log_new_file_name.map(new_path)
