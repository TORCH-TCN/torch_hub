import shutil
import os
from torch_web.workflows.workflows import torch_task


@torch_task("Copy File")
def copy_file(path: str):
    split_path = os.path.splitext(path)
    new_file_name = split_path[0] + '-copy' + split_path[1]
    shutil.copyfile(path, new_file_name)

    return new_file_name
