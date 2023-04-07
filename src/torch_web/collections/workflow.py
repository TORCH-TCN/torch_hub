from torch_web import db
from torch_web.collections.specimens import Specimen, SpecimenImage
from sqlalchemy import select
import os
import importlib
from prefect import context


def notify(func_name, specimen, message):
    context.socketio.emit(func_name, (specimen.id, func_name, message))
    context.socketio.emit('specimen_updated_' + str(specimen.id), (specimen.catalog_number, func_name + ': ' + message))


def run_workflow(collection, file):
    specimen, execute_workflow = upsert_specimen(collection, file)
    context.socketio.emit('specimen_added', specimen.id);

    if execute_workflow:
        for task in collection.workflow:
            notify(task['func_name'], specimen, 'Running')
            
            module = importlib.import_module('workflows.tasks.' + task['func_name'])
            func = getattr(module, task['func_name'])
            func(specimen, **task['parameters'])
            
            db.session.merge(specimen)
            db.session.commit()
            
            notify(task['func_name'], specimen, 'Success')


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
