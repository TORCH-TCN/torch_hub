from apiflask import APIBlueprint

from torch_web.workflows.workflows import TorchTasksResponse, torch_task_registry
from workflows.tasks import check_catalog_number, check_duplicate, check_orientation, generate_derivatives, upload
from torch_web.collections import collections

workflow_bp = APIBlueprint("workflows", __name__, url_prefix="/workflows")


@workflow_bp.get("/")
@workflow_bp.output(TorchTasksResponse)
@workflow_bp.doc(operation_id='GetAllTasks')
def workflows_getall():
    return { 'tasks': torch_task_registry }


@workflow_bp.post("/<int:collectionid>")
@workflow_bp.input(TorchTasksResponse)
@workflow_bp.output({}, status_code=200)
@workflow_bp.doc(operation_id='UpdateWorkflow')
def workflow_save(collectionid: int, data: TorchTasksResponse):
    collections.update_workflow(collectionid, data['tasks']);
    return ''

def workflows_execute():
    func_list = ["a", "b"]
    for name in func_list:
        func = getattr('workflows.tasks', name)
        print(func(0))