from prefect import Flow, Parameter, unmapped
from tasks.generate_derivatives import generate_derivatives
from tasks.upload import upload


with Flow("process-specimen") as process_specimen:
    specimen = Parameter("specimen", required=True)
    config = Parameter("config", required=True)

    derivatives = generate_derivatives(specimen=specimen, config=config)

    new_path = upload.map(
        derivatives=derivatives, config=unmapped(config)
    )

    # log_new_file_name.map(
    #     new_path=new_path,
    #     directory=unmapped(path))
