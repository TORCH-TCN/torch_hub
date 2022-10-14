# from https://github.com/aws-samples/amazon-textract-code-samples/blob/master/python/01-detect-text-local.py
from prefect import Flow, task
import prefect
from torch.collections.specimens import Specimen, SpecimenImage
from torch.prefect_flows.tasks.save_specimen import save_specimen
from prefect.orion.schemas.states import Completed, Failed

import json
import boto3

@task
def ocr(specimen:Specimen, app_config, flow_config):
    flow_run_id = prefect.context.get_run_context().task_run.flow_run_id.hex
    #file_path_string = os.path.join(root, specimen.upload_path)
    file_path = Path(specimen.upload_path)
    # Document
    #documentName = "okla_images_ALL_OK_stamps_A/OKLA104946_area_cropped_jNcPTx9M6cWAZQXupcRgoM.jpg"

    # Read document content
    with open(file_path, 'rb') as document:
        imageBytes = bytearray(document.read())

    # Amazon Textract client
    textract = boto3.client('textract')

    # Call Amazon Textract
    response = textract.detect_document_text(Document={'Bytes': imageBytes})

    #print(response)

    # Print detected text
    response_json = json.dumps(response)
    print(response_json)
    """
    with open('aws_output.jsonl', 'w') as outfile:
        #for entry in response_json:
        json.dump(response_json, outfile)
        outfile.write('\n')
    """

