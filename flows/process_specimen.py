from prefect import Flow, Parameter, unmapped
from tasks.log_new_file_name import log_new_file_name
from tasks.read_dir import read_dir
from tasks.upload import upload


with Flow("process-specimen") as process_specimen:
    path = Parameter("path", required=True)
    config = Parameter("config", required=True)

    files = read_dir(path)
    new_path = upload.map(
        path=files,
        config=unmapped(config))
    log_new_file_name.map(
        new_path=new_path,
        directory=unmapped(path))
