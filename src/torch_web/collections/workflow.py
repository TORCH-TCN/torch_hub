from torch_web import db
from torch_web.prefect_flows import process_specimen
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from torch_web.collections.specimens import Specimen, SpecimenImage
from sqlalchemy import select
from pathlib import Path
import os


def run_workflow(collection, file: FileStorage, config):
    specimen, execute_workflow = upsert_specimen(collection, file, config)

    if execute_workflow:
        notify_specimen_update(specimen, "Running", socketio)

        if collection.workflow == "process_specimen":
            state = process_specimen(collection, specimen, config, return_state=True)
        else:
            raise NotImplementedError

        notify_specimen_update(specimen, state.name, socketio)


def upsert_specimen(collection, file, config):
    s_filename = secure_filename(file.filename)
    filename = s_filename.split(".")[0]
    extension = s_filename.split(".")[1]

    target_dir = os.path.join(config['BASE_DIR'], "static", "uploads", collection.collection_folder)
    Path(target_dir).mkdir(parents=True, exist_ok=True)

    execute_workflow = True

    specimen = db.session.scalars(select(Specimen).filter(Specimen.name == filename)).first()

    destination = os.path.join(target_dir, s_filename)

    if os.path.exists(destination):
        return specimen, False

    file.save(destination)

    if specimen is not None:
        if extension.lower() == "dng":
            specimen.has_dng = 1
            execute_workflow = False

        else:
            execute_workflow = specimen.flow_run_id is not None

    else:
        specimen = Specimen(
            name=filename, upload_path=destination, collection_id=collection.id
        )
        db.session.add(specimen)
        db.session.commit()

    upsert_specimen_image(specimen, destination, extension.lower())

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


def notify_specimen_update(specimen, state, socketio):
    db.session.refresh(specimen)
    socketio.emit(
        "notify",
        {
            "id": specimen.id,
            "name": specimen.name,
            "cardimg": specimen.card_image(),
            "create_date": str(specimen.create_date),
            "flow_run_state": state,
            "failed_task": specimen.failed_task,
        },
    )
