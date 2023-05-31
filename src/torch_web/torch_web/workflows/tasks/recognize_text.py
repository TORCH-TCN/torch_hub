from torch_web.collections import collections
from torch_web.workflows.workflows import torch_task
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials

import os
import time



@torch_task("Get Text from Image")
def recognize_text(specimen: collections.Specimen):
    """
    Recognizes texts in an image using Microsoft Cognitive Services Computer Vision API.

    Args:
        image_path (str): Path to the image file.
        subscription_key (str): Subscription key for Azure Cognitive Services.
        endpoint (str): Endpoint for Azure Cognitive Services.

    Returns:
        list: A list of recognized texts extracted from the image.
    """

    endpoint = "https://britcomputervision.cognitiveservices.azure.com/"
    subscription_key = os.environ.get('AZURE_COMPUTER_VISION_KEY')
    client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))
    
    # Call API with URL and raw response (allows you to get the operation location)
    read_response = client.read(specimen.upload_path, raw=True)

    # Get the operation location (URL with an ID at the end) from the response
    read_operation_location = read_response.headers["Operation-Location"]
    
    # Grab the ID from the URL
    operation_id = read_operation_location.split("/")[-1]

    # Call the "GET" API and wait for it to retrieve the results 
    while True:
        read_result = client.get_read_result(operation_id)
        if read_result.status not in ['notStarted', 'running']:
            break
        time.sleep(1)

    # Print the detected text, line by line
    results = {}
    i = 0
    if read_result.status == OperationStatusCodes.succeeded:
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                key = str(i)
                i += 1
                results[key] = line.text

    return results