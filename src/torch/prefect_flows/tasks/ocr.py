# from https://github.com/aws-samples/amazon-textract-code-samples/blob/master/python/01-detect-text-local.py

from prefect import task
import prefect
from torch.prefect_flows.tasks.save_specimen import save_specimen
from torch.collections.specimens import Specimen
from prefect.orion.schemas.states import Failed
import secrets

import json
from PIL import Image

import boto3


Specimen = None

@task
def textract(specimen:Specimen, app_config):
    flow_run_id = prefect.context.get_run_context().task_run.flow_run_id.hex
    #file_path_string = os.path.join(root, specimen.upload_path)

    # Full uploaded image is generally too big for AWS Textract service
    #file_path = Path(specimen.upload_path)


    # Get FULL resolution image - same dimensions as upload, but compressed
    # must be under 5MB for AWS Textract to work
    specimen_id = specimen.id
    print(specimen_id)
    # When trying to get the image or filter for the FULL image type, I get the following error:
    # sqlalchemy.exc.ProgrammingError: (sqlite3.ProgrammingError) SQLite objects created in a thread can only be used in that same thread. The object was created in thread id 139664593766144 and this is thread id 139663469700864.

    for image in specimen.images:
        print(image)
    #print(specimen.images)

    #img_full = specimen.images.query.filter_by(size='FULL').first()
    #print(img_full)
    #img_full_path = img_full.url
    #print(img_full_path)
    #file_path =img_full_path
    #file_path = specimen.upload_path

"""
    # Document
    #documentName = "okla_images_ALL_OK_stamps_A/OKLA104946_area_cropped_jNcPTx9M6cWAZQXupcRgoM.jpg"

    # Read document content
    print('Opening file:', file_path)
    with open(file_path, 'rb') as document:
        imageBytes = bytearray(document.read())

    # Amazon Textract client
    textract = boto3.client('textract', aws_access_key_id=secrets.aws_access_key_id, aws_secret_access_key=secrets.aws_secret_access_key)

    # Call Amazon Textract
    response = textract.detect_document_text(Document={'Bytes': imageBytes})
    print(response)

    # Print detected text
    response_json = json.dumps(response)
"""

if __name__ == "__main__":
    # test file path
    file_path = '/media/jbest/data2/BRIT_git/torch_hub/src/torch/static/uploads/BRIT-test/fee50aca-a8dd-4cd8-b492-dca6c43ef94c/BRIT384264_FULL.jpg'
    #file_path = '/media/jbest/data2/OKLA_stamp_tests/okla_images_detected_objects_sorted/OKLA/OKLA000100000/OKLA100288_area_cropped_exEf8v8brdd7mXMkbNkisn.jpg'
    print('Opening file:', file_path)
    with open(file_path, 'rb') as document:
        imageBytes = bytearray(document.read())

    # Amazon Textract client
    #textract = boto3.client('textract')
    textract = boto3.client('textract', aws_access_key_id=secrets.aws_access_key_id, aws_secret_access_key=secrets.aws_secret_access_key)


    # Call Amazon Textract
    response = textract.detect_document_text(Document={'Bytes': imageBytes})

    print(response)    