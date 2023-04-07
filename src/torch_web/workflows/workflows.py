import functools
import inspect

from apiflask import Schema
from sqlalchemy import Column, Integer, String, ForeignKey, func, Text, JSON, exists, select

from apiflask.fields import List, Nested
from torch_web import Base
from sqlalchemy.orm import Mapped, relationship
torch_task_registry = []



class TorchTasksResponse(Schema):
    tasks = List(Nested(TorchTask))

    
def torch_task(name, description=None):
    def decorate(func):
        global torch_task_registry
        spec = inspect.signature(func)
        parameters = { k: str(v.default) if v.default is not inspect.Parameter.empty else None for k, v in spec.parameters.items() if k != 'specimen' }
        torch_task_registry.append({ 'name': name, 'description': description, 'func_name': func.__name__, 'parameters': parameters })

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return result

        return wrapper
    return decorate