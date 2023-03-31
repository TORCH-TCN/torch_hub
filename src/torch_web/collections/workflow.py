from torch_web import db
from torch_web.collections.specimens import Specimen, SpecimenImage
from sqlalchemy import select
import os
import importlib
from prefect import context

def run_workflow(collection, file):
    specimen, execute_workflow = upsert_specimen(collection, file)

    if execute_workflow:
        for task in collection.workflow:
            context.socketio.emit('task_state_changed', (specimen.id, task['func_name'], 'Running'))
            
            module = importlib.import_module('workflows.tasks.' + task['func_name'])
            func = getattr(module, task['func_name'])
            func(specimen, task['parameters']["catalog_number_regex"])
            
            db.session.merge(specimen)
            db.session.commit()
            
            context.socketio.emit('task_state_changed', (specimen.id, task['func_name'], 'Success'))


def upsert_specimen(collection, file):
    filename = os.path.basename(file).split(".")[0]
    extension = os.path.basename(file).split(".")[1]

    execute_workflow = True

    specimen = db.session.scalars(select(Specimen).filter(Specimen.name == filename)).first()

    if specimen is not None:
        if extension.lower() == "dng":
            specimen.has_dng = 1
            execute_workflow = False

        else:
            execute_workflow = specimen.flow_run_id is not None

    else:
        specimen = Specimen(
            name=filename, upload_path=file, collection_id=collection.id
        )
        db.session.add(specimen)
        db.session.commit()

    upsert_specimen_image(specimen, file, extension.lower())

    return specimen, execute_workflow


def upsert_specimen_image(specimen, destination, extension):
    size = "FULL"
    if extension == "dng":
        size = "DNG"

    si = db.session.scalars(select(SpecimenImage)
            .filter(SpecimenImage.specimen_id == specimen.id)
            .filter(SpecimenImage.size == size)).first()

    if si is None:
        new_si = SpecimenImage(specimen_id=specimen.id, url=destination, size=size)
        db.session.add(new_si)
        db.session.commit()


def notify_specimen_update(specimen, state, socketio, progress):
    db.session.refresh(specimen)
    if socketio:
        socketio.emit(
            "notify",
            {
                "id": specimen.id,
                "name": specimen.name,
                "create_date": str(specimen.create_date),
                "flow_run_state": state,
                "failed_task": specimen.failed_task,
            },
        )
    
    if progress:
        progress.add_task(state,)
