from torch_web.collections import collections
from sqlalchemy import or_, select
from torch_web.workflows.workflows import torch_task
from torch_web import db
from torch_web.collections.collections import SpecimenImage
import imagehash
from PIL import Image


def hash(image: SpecimenImage, hashfunc="average"):
    with Image.open(image.url) as im:
        result = str(imagehash.average_hash(im) if hashfunc == "average" else imagehash.phash(im))
        split_hash = [result[i:i+4] for i in range(0, len(result), 4)]
        image.hash_a = split_hash[0]
        image.hash_b = split_hash[1]
        image.hash_c = split_hash[2]
        image.hash_d = split_hash[3]


@torch_task("Check for Duplicate Image")
def check_duplicate(specimen, max_distance=35):
    """
    Hashes the incoming image and compares it against other hashes to 
    ensure uniqueness in the specimen database
    """
    
    for img in specimen.images:
        try:
            hash(img)
            split_filter = or_(SpecimenImage.hash_a == img.hash_a,
                               SpecimenImage.hash_b == img.hash_b,
                               SpecimenImage.hash_c == img.hash_c,
                               SpecimenImage.hash_d == img.hash_d)

            similar_images = db.session.scalars(select(collections.SpecimenImage).filter(SpecimenImage.id != img.id, SpecimenImage.hash_a is not None, split_filter))
            too_close_images = [sim for sim in similar_images if abs(sim.average_hash() - img.average_hash()) < max_distance]
    
            if len(too_close_images) > 0:
                return f"Specimen image {img.id} is too similar to {too_close_images[0].url}"
        except:
            return f'Unable to compare image {img.id}'

    return specimen
