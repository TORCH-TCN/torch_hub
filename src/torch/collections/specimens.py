import glob
import os
from uuid import uuid4
from sqlalchemy import (
    Integer,
    String,
    Column,
    DateTime,
    ForeignKey,
    Text,
)

# from config.database.TorchDatabase import Entity
from torch import db
from sqlalchemy.sql import func


class Specimen(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True)
    uploaded_date = Column(DateTime(timezone=True), default=func.now())
    med_image_url = Column(Text)  # possible change this to string?
    thumbnail_url = Column(Text)
    barcode = Column(String(20))
    collection_id = Column(Integer, ForeignKey("collection.id"))
    catalog_number = Column(String(150))
    flow_run_id = Column(String(150))


def get_specimens_by_batch_id(batch_id):
    root = "static/uploads/{}".format(batch_id)
    files = []

    if not os.path.isdir(root):
        return files

    for file in glob.glob("{}/*.*".format(root)):
        fname = file.split(os.sep)[-1]
        files.append(fname)


def upload_specimens(files):
    # Create a unique "session ID" for this particular batch of uploads.
    batch_id = str(uuid4())

    target = "webapp/static/uploads/{}".format(batch_id)
    os.mkdir(target)

    for upload in files:
        filename = upload.filename.rsplit("/")[0]
        destination = "/".join([target, filename])
        print("Accept incoming file:", filename)
        print("Save it to:", destination)
        upload.save(destination)

    return batch_id
