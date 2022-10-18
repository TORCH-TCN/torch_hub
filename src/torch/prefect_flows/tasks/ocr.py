# from https://github.com/aws-samples/amazon-textract-code-samples/blob/master/python/01-detect-text-local.py

from prefect import task
import prefect
from torch.prefect_flows.tasks.save_specimen import save_specimen
from torch.collections.specimens import Specimen, SpecimenImage
from prefect.orion.schemas.states import Failed
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
# for some reason I can't use 'import aws_secrets', getting module not found error
from .aws_secrets import aws_access_key_id, aws_secret_access_key

import json
from PIL import Image

import boto3


Specimen = None


@task
def textract(specimen: Specimen, flow_config, app_config):

    engine = create_engine(app_config["SQLALCHEMY_DATABASE_URI"], future=True)
    flow_run_id = prefect.context.get_run_context().task_run.flow_run_id.hex

    with Session(engine) as session:

        try:
            ocr_specimen = session.merge(specimen) #thread-safe
            
            # Not sure if this is the right/best way to query the SpecimenImage
            # Seems like I should be able to query as below but it didn't work:
            #img_full = ocr_specimen.images.query.filter_by(size='FULL').first()
            img_full = session.query(SpecimenImage).filter_by(specimen_id=ocr_specimen.id).filter_by(size='FULL').first()
            file_path = img_full.url
            print(file_path)

            # Document
            try:
                # Read document content
                print('Opening file:', file_path)
                with open(file_path, 'rb') as document:
                    imageBytes = bytearray(document.read())
            except Exception as e:
                print(e)

            try:
                # Amazon Textract client
                textract = boto3.client('textract', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

                # Call Amazon Textract
                response = textract.detect_document_text(Document={'Bytes': imageBytes})
                print(response)

                # Print detected text
                response_json = json.dumps(response)
            except Exception as e:
                response_json = None
                print(e)

            session.commit()

            save_specimen(ocr_specimen,app_config,flow_run_id)

            return response_json
        except:
            session.commit()
            save_specimen(specimen,app_config,flow_run_id,'Failed','textract')
            return Failed(message=f"Unable to generate OCR for specimen {specimen.id}-{specimen.name}")
        finally:
            session.close()
