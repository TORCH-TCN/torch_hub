import os
import boto3
import paramiko
import pysftp

from botocore.config import Config
from botocore.exceptions import ClientError
from minio import Minio
from PBKDF2 import PBKDF2
from Crypto.Cipher import AES

from torch_web.collections.specimens import Specimen
from torch_web.workflows.workflows import torch_task


KEY_SIZE = 32 # AES-256
IV_SIZE = 16 # 128-bits to initialise
BLOCK_SIZE = 16

def encrypt(password):
    salt = os.environ.get('FLASK_SECRET_KEY')
    key = PBKDF2(password, salt).read(KEY_SIZE)
    initVector = os.urandom(IV_SIZE)
    cipher = AES.new(key, AES.MODE_CBC, initVector)
    return initVector + cipher.encrypt(password + ' ' * (BLOCK_SIZE - len(password) % BLOCK_SIZE))


def decrypt(password):
    salt = os.environ.get('FLASK_SECRET_KEY')
    key = PBKDF2(password, salt).read(KEY_SIZE)
    initVector = ciphertext[:IV_SIZE]
    ciphertext = ciphertext[IV_SIZE:]
    cipher = AES.new(key, AES.MODE_CBC, initVector)
    return cipher.decrypt(ciphertext).rstrip(' ')


@torch_task("Upload")
def upload(specimen: Specimen, upload_folder: str, upload_type='sftp', host=None, username=None, password=None):
    password = decrypt(password)
    
    for image in specimen.images:
        if upload_type == "sftp":
            image.external_url = upload_via_paramiko_sftp(upload_folder, image.url, host, username, password)
        elif upload_type == "s3":
            image.external_url = upload_via_s3(upload_folder, image.url, host, username, password)
        elif upload_type == "minio":
            image.external_url = upload_via_minio(upload_folder, image.url, host, username, password)
        else:
            raise NotImplementedError(f"Upload type {upload_type} is not yet implemented.")


def upload_via_paramiko_sftp(collection_folder, path, host, username, password):
    transport = paramiko.Transport((host, 22))
    transport.connect(username=username, password=password.get_secret_value())
    sftp = paramiko.SFTPClient.from_transport(transport)

    mkdir_p(sftp, collection_folder)
    sftp.put(path, os.path.basename(path))
    final_url = f"{host}" + sftp.getcwd() + f"/{os.path.basename(path)}"
    sftp.close()
    transport.close()

    return final_url


def upload_via_s3(collection_folder, path, host, username, password):
    amazon_config = Config(
        region_name=host,
    )

    s3 = boto3.client(
        "s3",
        config=amazon_config,
        aws_access_key_id=username,
        aws_secret_access_key=password.get_secret_value(),
    )

    try:
        response = s3.upload_file(
            path, collection_folder, os.path.basename(path)
        )
        return response
    except ClientError:
        return None


def upload_via_pysftp(collection_folder, path, host, username, password):
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    with pysftp.Connection(
        host=host,
        username=username,
        password=password.get_secret_value(),
        cnopts=cnopts,
    ) as sftp:
        try:
            sftp.chdir(collection_folder)
        except IOError:
            sftp.mkdir(collection_folder)
            sftp.chdir(collection_folder)

        sftp.put(path)

        return f'{host}' + sftp.getcwd() + f"/{os.path.basename(path)}"


def upload_via_minio(collection_folder, path, host, username, password):
    client = Minio(
        host,
        access_key=username,
        secret_key=password.get_secret_value(),
    )

    found = client.bucket_exists(collection_folder)
    if not found:
        client.make_bucket(collection_folder)
    else:
        print(f"Bucket {collection_folder} already exists")

    result = client.fput_object(collection_folder, os.path.basename(path), path)

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
