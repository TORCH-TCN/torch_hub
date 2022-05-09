import os
import boto3
import pysftp
from prefect import prefect, task
from botocore.exceptions import ClientError
from botocore.config import Config


@task
def upload(config, path: str):
    logger = prefect.context.get('logger')
    type = config['upload']['type']
    logger.info(f"Uploading {path} via {type}...")

    match type:
        case 'sftp':
            return upload_via_sftp(config['upload'], path)
        case 's3':
            return upload_via_s3(config['upload'], path)
        case _:
            raise NotImplementedError(
                f"Upload type {type} is not yet implemented.")


def upload_via_sftp(config, path):
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    with pysftp.Connection(
        host=config['host'],
        username=config['username'],
        password=config['password'],
        cnopts=cnopts
    ) as sftp:
        try:
            sftp.chdir(config['path'])
        except IOError:
            sftp.mkdir(config['path'])
            sftp.chdir(config['path'])

        sftp.put(path)

        return f'{config["host"]}' \
            + sftp.getcwd() \
            + f'/{os.path.basename(path)}'


def upload_via_s3(config, path):
    amazon_config = Config(
        region_name=config['host'],
    )

    s3 = boto3.client(
        's3',
        config=amazon_config,
        aws_access_key_id=config['username'],
        aws_secret_access_key=config['password']
    )

    try:
        response = s3.upload_file(
            path,
            config['path'],
            os.path.basename(path))
        return response
    except ClientError:
        return None
