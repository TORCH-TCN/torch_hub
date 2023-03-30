import functools
import inspect

from apiflask import APIBlueprint, Schema
from apiflask.fields import Integer, String, List, Nested, Dict, DateTime

workflow_bp = APIBlueprint("workflows", __name__, url_prefix="/workflows")
torch_task_registry = []


class TorchTask(Schema):
    func_name = String()
    name = String()
    description = String(nullable=True)
    parameters = Dict(String(), String())


class TorchTasksResponse(Schema):
    all_tasks = List(Nested(TorchTask))
    collection_tasks = List(Nested(TorchTask))

    
def torch_task(name, description=None):
    def decorate(func):
        global torch_task_registry
        spec = inspect.signature(func)
        parameters = { k: str(v.default) if v.default is not inspect.Parameter.empty else None for k, v in spec.parameters.items() }
        torch_task_registry.append({ 'name': name, 'description': description, 'func_name': func.__name__, 'parameters': parameters })

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return result

        return wrapper
    return decorate

@workflow_bp.get("/")
@workflow_bp.output(TorchTasksResponse)
@workflow_bp.doc(operation_id='GetAllTasks')
def workflows_getall():
    from workflows.tasks import check_catalog_number
    global torch_task_registry
    return { 'all_tasks': torch_task_registry }


def workflows_execute():
    func_list = ["a", "b"]
    for name in func_list:
        func = getattr('workflows.tasks', name)
        print(func(0))