import os
import boto3
import pysftp
from prefect import prefect, task
from botocore.exceptions import ClientError
from botocore.config import Config


@task
def upload(config, path: str):
    logger = prefect.context.get('logger')

    logger.info(f'Uploading {path} via {config.upload.type}...')

    match config.upload.type:
        case 'sftp':
            return upload_via_sftp(config, path)
        case 's3':
            return upload_via_s3(config, path)
        case _:
            raise NotImplementedError(
                f"Upload type {config.upload.type} is not yet implemented.")


def upload_via_sftp(config, path):
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    with pysftp.Connection(
        host=config.upload.host,
        username=config.upload.username,
        password=config.upload.password,
        cnopts=cnopts
    ) as sftp:
        try:
            sftp.chdir(config.upload.path)
        except IOError:
            sftp.mkdir(config.upload.path)
            sftp.chdir(config.upload.path)

        sftp.put(path)

        return f'{config.upload.host}' \
            + sftp.getcwd() \
            + f'/{os.path.basename(path)}'


def upload_via_s3(config, path):
    amazon_config = Config(
        region_name=config.upload.host,
    )

    s3 = boto3.client(
        's3',
        config=amazon_config,
        aws_access_key_id=config.upload.username,
        aws_secret_access_key=config.upload.password
    )

    try:
        response = s3.upload_file(
            path,
            config.upload.path,
            os.path.basename(path))
        return response
    except ClientError:
        return None
