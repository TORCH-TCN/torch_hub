import ast
import re

from torch_web.collections import specimens
from torch_web.workflows.workflow_api import torch_task


@torch_task("Extract Catalog Number")
def check_catalog_number(specimen: specimens.Specimen, catalog_number_regex=None):
    """
    Extracts the catalog number from the specimen's file name.
    
    :param str catalog_number_regex: 
    """

    specimen.catalog_number = specimen.name
    if catalog_number_regex is not None:
        for x in ast.literal_eval(catalog_number_regex):
            c = re.search(x, specimen.name)
            if c is not None and c.group("catNum") is not None:
                specimen.catalog_number = c.group("catNum")
                break
    
    return specimen
