import os

import boto3
import paramiko
import pysftp
from botocore.config import Config
from botocore.exceptions import ClientError
from minio import Minio
from prefect import get_run_logger, task

from torch.collections.specimens import SpecimenImage


@task
def upload(collection, image: SpecimenImage):

    logger = get_run_logger()
    upload_type = os.environ["TORCH_UPLOAD_TYPE"]
    logger.info(f"Uploading {image.url} via {upload_type}...")

    if upload_type == "sftp":
        image.external_url = upload_via_paramiko_sftp(collection, image.url)
    elif upload_type == "s3":
        image.external_url = upload_via_s3(collection, image.url)
    elif upload_type == "minio":
        image.external_url = upload_via_minio(collection, image.url)
    else:
        raise NotImplementedError(f"Upload type {upload_type} is not yet implemented.")


def upload_via_paramiko_sftp(collection, path):
    host = os.environ["TORCH_UPLOAD_HOST"]
    transport = paramiko.Transport((host, 22))
    transport.connect(username=os.environ["TORCH_UPLOAD_USERNAME"], password=os.environ["TORCH_UPLOAD_PASSWORD"])
    sftp = paramiko.SFTPClient.from_transport(transport)

    mkdir_p(sftp, collection.collection_folder)
    sftp.put(path, os.path.basename(path))
    final_url = f"{host}" + sftp.getcwd() + f"/{os.path.basename(path)}"
    sftp.close()
    transport.close()

    return final_url


def upload_via_s3(collection, path):
    amazon_config = Config(
        region_name=os.environ["TORCH_UPLOAD_HOST"],
    )

    s3 = boto3.client(
        "s3",
        config=amazon_config,
        aws_access_key_id=os.environ["TORCH_UPLOAD_USERNAME"],
        aws_secret_access_key=os.environ["TORCH_UPLOAD_PASSWORD"],
    )

    try:
        response = s3.upload_file(
            path, collection.collection_folder, os.path.basename(path)
        )
        return response
    except ClientError:
        return None


def upload_via_pysftp(collection, path):
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    with pysftp.Connection(
        host=os.environ["TORCH_UPLOAD_HOST"],
        username=os.environ["TORCH_UPLOAD_USERNAME"],
        password=os.environ["TORCH_UPLOAD_PASSWORD"],
        cnopts=cnopts,
    ) as sftp:
        try:
            sftp.chdir(collection.collection_folder)
        except IOError:
            sftp.mkdir(collection.collection_folder)
            sftp.chdir(collection.collection_folder)

        sftp.put(path)

        return f'{os.environ["TORCH_UPLOAD_HOST"]}' + sftp.getcwd() + f"/{os.path.basename(path)}"


def upload_via_minio(collection, path):
    client = Minio(
        os.environ["TORCH_UPLOAD_HOST"],
        access_key=os.environ["TORCH_UPLOAD_USERNAME"],
        secret_key=os.environ["TORCH_UPLOAD_PASSWORD"],
    )

    bucket = collection.collection_folder
    found = client.bucket_exists(bucket)
    if not found:
        client.make_bucket(bucket)
    else:
        print(f"Bucket {bucket} already exists")

    result = client.fput_object(bucket, os.path.basename(path), path)

    #return result.location
    return result.object_name


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
