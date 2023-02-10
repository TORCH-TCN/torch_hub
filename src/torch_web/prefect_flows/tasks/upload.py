import os

import boto3
import paramiko
import pysftp
from botocore.config import Config
from botocore.exceptions import ClientError
from minio import Minio
from prefect import get_run_logger, task
from prefect.blocks.core import Block

from torch_web.collections.specimens import SpecimenImage
from torch_web.prefect_flows.blocks.upload_credentials import UploadCredentials
from torch_web.prefect_flows.tasks import save_specimen


@task
def upload(collection, image: SpecimenImage, config):

    logger = get_run_logger()
    credentials = UploadCredentials.load(f"{collection.id}")
    upload_type = credentials.type
    logger.info(f"Uploading {image.url} via {upload_type}...")

    if upload_type == "sftp":
        image.external_url = upload_via_paramiko_sftp(collection, image.url, credentials)
    elif upload_type == "s3":
        image.external_url = upload_via_s3(collection, image.url, credentials)
    elif upload_type == "minio":
        image.external_url = upload_via_minio(collection, image.url, credentials)
    else:
        raise NotImplementedError(f"Upload type {upload_type} is not yet implemented.")

    save_specimen.save_specimen_image(image, config)


def upload_via_paramiko_sftp(collection, path, credentials):
    host = credentials.host
    transport = paramiko.Transport((host, 22))
    transport.connect(username=credentials.username, password=credentials.password.get_secret_value())
    sftp = paramiko.SFTPClient.from_transport(transport)

    mkdir_p(sftp, collection.collection_folder)
    sftp.put(path, os.path.basename(path))
    final_url = f"{host}" + sftp.getcwd() + f"/{os.path.basename(path)}"
    sftp.close()
    transport.close()

    return final_url


def upload_via_s3(collection, path, credentials):
    amazon_config = Config(
        region_name=credentials.host,
    )

    s3 = boto3.client(
        "s3",
        config=amazon_config,
        aws_access_key_id=credentials.username,
        aws_secret_access_key=credentials.password.get_secret_value(),
    )

    try:
        response = s3.upload_file(
            path, collection.collection_folder, os.path.basename(path)
        )
        return response
    except ClientError:
        return None


def upload_via_pysftp(collection, path, credentials):
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    with pysftp.Connection(
        host=credentials.host,
        username=credentials.username,
        password=credentials.password.get_secret_value(),
        cnopts=cnopts,
    ) as sftp:
        try:
            sftp.chdir(collection.collection_folder)
        except IOError:
            sftp.mkdir(collection.collection_folder)
            sftp.chdir(collection.collection_folder)

        sftp.put(path)

        return f'{credentials.host}' + sftp.getcwd() + f"/{os.path.basename(path)}"


def upload_via_minio(collection, path, credentials):
    client = Minio(
        credentials.host,
        access_key=credentials.username,
        secret_key=credentials.password.get_secret_value(),
    )

    bucket = collection.collection_folder
    found = client.bucket_exists(bucket)
    if not found:
        client.make_bucket(bucket)
    else:
        print(f"Bucket {bucket} already exists")

    result = client.fput_object(bucket, os.path.basename(path), path)

    return result.location


def mkdir_p(sftp, remote_directory):
    if remote_directory == "/":
        sftp.chdir("/")
        return
    if remote_directory == "":
        return
    try:
        sftp.chdir(remote_directory)  # subdirectory exists
    except IOError:
        dirname, basename = os.path.split(remote_directory.rstrip("/"))
        mkdir_p(sftp, dirname)  # make parent directories
        sftp.mkdir(basename)  # subdirectory missing, so created it
        sftp.chdir(basename)
        return True
