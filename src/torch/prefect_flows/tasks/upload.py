import os
import boto3
import pysftp
import paramiko
from prefect import get_run_logger, task
from botocore.exceptions import ClientError
from botocore.config import Config
from torch.collections.specimens import SpecimenImage


@task
def upload(collection, config, image: SpecimenImage):

    logger = get_run_logger()
    upload_type = config["UPLOAD"]["TYPE"]
    logger.info(f"Uploading {image.url} via {upload_type}...")
    
    match upload_type:
        case "sftp":
            image.external_url = upload_via_paramiko_sftp(collection, config["UPLOAD"], image.url)
        case "s3":
            image.external_url = upload_via_s3(collection, config["UPLOAD"], image.url)
        case _:
            raise NotImplementedError(
                f"Upload type {upload_type} is not yet implemented."
            )


def upload_via_paramiko_sftp(collection, config, path):
    host = config["HOST"]
    transport = paramiko.Transport((host, 22))
    transport.connect(username = config["USERNAME"], password = config["PASSWORD"])
    sftp = paramiko.SFTPClient.from_transport(transport)

    mkdir_p(sftp, collection.collection_folder) 
    sftp.put(path, os.path.basename(path)) 
    final_url = f'{host}' + sftp.getcwd() + f"/{os.path.basename(path)}"
    sftp.close()
    transport.close()

    return final_url



def upload_via_s3(collection, config, path):
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
        response = s3.upload_file(path, collection.collection_folder, os.path.basename(path))
        return response
    except ClientError:
        return None

def upload_via_pysftp(collection, config, path):
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    with pysftp.Connection(
        host=config["HOST"],
        username=config["USERNAME"],
        password=config["PASSWORD"],
        cnopts=cnopts,
    ) as sftp:
        try:
            sftp.chdir(collection.collection_folder)
        except IOError:
            sftp.mkdir(collection.collection_folder)
            sftp.chdir(collection.collection_folder)

        sftp.put(path)

        return f'{config["HOST"]}' + sftp.getcwd() + f"/{os.path.basename(path)}"


def mkdir_p(sftp, remote_directory):
    if remote_directory == '/':
        sftp.chdir('/')
        return
    if remote_directory == '':
        return
    try:
        sftp.chdir(remote_directory) # sub-directory exists
    except IOError:
        dirname, basename = os.path.split(remote_directory.rstrip('/'))
        mkdir_p(sftp, dirname) # make parent directories
        sftp.mkdir(basename) # sub-directory missing, so created it
        sftp.chdir(basename)
        return True