from prefect import flow, unmapped
from torch.tasks.generate_derivatives import generate_derivatives
from torch.tasks.upload import upload


@flow
def process_specimen(specimen, config):
    images = generate_derivatives(specimen=specimen, config=config)
    upload.map(image=images, config=unmapped(config))

    # log_new_file_name.map(
    #     new_path=new_path,
    #     directory=unmapped(path))
