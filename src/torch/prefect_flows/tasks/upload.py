import os
import boto3
import pysftp
from prefect import get_run_logger, task
from botocore.exceptions import ClientError
from botocore.config import Config
from torch.collections.specimens import SpecimenImage
from torch.prefect_flows.tasks.save_specimen import save_specimen_image


@task
def upload(config, image: SpecimenImage):

    logger = get_run_logger()
    upload_type = config["UPLOAD"]["TYPE"]
    logger.info(f"Uploading {image.url} via {upload_type}...")
    
    match upload_type:
        case "sftp":
            image.external_url = upload_via_sftp(config["UPLOAD"], image.url)
        case "s3":
            image.external_url = upload_via_s3(config["UPLOAD"], image.url)
        case _:
            raise NotImplementedError(
                f"Upload type {upload_type} is not yet implemented."
            )



def upload_via_sftp(config, path):
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    with pysftp.Connection(
        host=config["HOST"],
        username=config["USERNAME"],
        password=config["PASSWORD"],
        cnopts=cnopts,
    ) as sftp:
        try:
            sftp.chdir(config["PATH"])
        except IOError:
            sftp.mkdir(config["PATH"])
            sftp.chdir(config["PATH"])

        sftp.put(path)

        return f'{config["HOST"]}' + sftp.getcwd() + f"/{os.path.basename(path)}"


def upload_via_s3(config, path):
    amazon_config = Config(
        region_name=config["HOST"],
    )

    s3 = boto3.client(
        "s3",
        config=amazon_config,
        aws_access_key_id=config["USERNAME"],
        aws_secret_access_key=config["PASSWORD"],
    )

    try:
        response = s3.upload_file(path, config["PATH"], os.path.basename(path))
        return response
    except ClientError:
        return None
