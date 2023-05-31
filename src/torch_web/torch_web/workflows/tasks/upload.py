import os
import boto3
import paramiko
import requests
from io import BytesIO

from botocore.config import Config
from botocore.exceptions import ClientError
from minio import Minio
from pbkdf2 import PBKDF2
from Cryptodome.Cipher import AES

from torch_web.collections.collections import Specimen
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


@torch_task("Transfer")
def upload(specimen: Specimen, upload_folder: str, upload_type='sftp', host=None, username=None, password=None):
    # password = decrypt(password)
    try:
        result = {}
        for image in specimen.images:
            if upload_type == "sftp":
                image.external_url = upload_via_paramiko_sftp(upload_folder, image.url, host, username, password)
            elif upload_type == "s3":
                image.external_url = upload_via_s3(upload_folder, image.url, host, username, password)
            elif upload_type == "minio":
                image.external_url = upload_via_minio(upload_folder, image.url, host, username, password)
            else:
                raise NotImplementedError(f"Upload type {upload_type} is not yet implemented.")
            result[image.size] = image.external_url

        return result
    except Exception as e:
        return f"An error occurred: {e}"
    


def upload_via_paramiko_sftp(collection_folder, path, host, username, password):
    transport = paramiko.Transport((host, 22))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    image_bytes = BytesIO(requests.get(path, stream=True).content)

    mkdir_p(sftp, collection_folder)
    sftp.putfo(image_bytes, os.path.basename(path))
    final_url = f"{host}" + sftp.getcwd() + f"/{os.path.basename(path)}"
    sftp.close()
    transport.close()

    return 'https://' + final_url.replace('windows.net', 'windows.net/torch-admin')


def upload_via_s3(collection_folder, path, host, username, password):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=username,
        aws_secret_access_key=password,
        endpoint_url='https://' + host,
    )
    print('transferring...')
    image_bytes = BytesIO(requests.get(path, stream=True).content)
    s3.upload_fileobj(image_bytes, collection_folder, os.path.basename(path))

    #files = s3.list_objects_v2(Bucket=collection_folder)
    #for file in files["Contents"]:
    #    print(file)

    hostnoport = host.split(":")[0]
    return f"https://{hostnoport}/{collection_folder}/{os.path.basename(path)}"


def upload_via_minio(collection_folder, path, host, username, password):
    client = Minio(
        host,
        access_key=username,
        secret_key=password,
    )

    found = client.bucket_exists(collection_folder)
    if not found:
        client.make_bucket(collection_folder)
    else:
        print(f"Bucket {collection_folder} already exists")

    r = requests.get(path, stream=True)
    image_bytes = BytesIO(r.content)
    image_size = image_bytes.getbuffer().nbytes
    
    client.put_object(collection_folder, os.path.basename(path), image_bytes, image_size, content_type='image/jpeg')
    hostnoport = host.split(":")[0]

    #files = client.list_objects(collection_folder, recursive=True)
    #for file in files:
    #    print(file)

    return f"https://{hostnoport}/{collection_folder}/{os.path.basename(path)}"


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
