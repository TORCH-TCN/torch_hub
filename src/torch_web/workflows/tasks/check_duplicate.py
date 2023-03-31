from torch_web.collections import specimens
from sqlalchemy import or_, select
from torch_web.workflows.workflows import torch_task
from torch_web import db
from torch_web.collections.specimens import SpecimenImage

@torch_task("Check for Duplicate Image")
def check_duplicate(img: specimens.SpecimenImage):
    """
    Hashes the incoming image and compares it against other hashes to 
    ensure uniqueness in the specimen database
    """
    
    max_distance = 35
    
    img_hash = specimens.hash(img.url)
    split_hash = [result[i:i+4] for i in range(0, len(img_hash), 4)]
    split_filter = or_(SpecimenImage.hash_a == split_hash[0],
                       SpecimenImage.hash_b == split_hash[1],
                       SpecimenImage.hash_c == split_hash[2],
                       SpecimenImage.hash_d == split_hash[3])

    similar_images = db.session.scalars(select(specimens.SpecimenImage).filter(split_filter))
    too_close_images = [sim for sim in similar_images if abs(sim.average_hash() - img_hash) < max_distance]
    
    if len(too_close_images) > 0:
        return Failed(message=f"Specimen image {img.id} is too similar to {too_close_images[0].url}")

    return img
