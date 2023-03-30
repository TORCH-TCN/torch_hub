from prefect import task
from torch_web.collections import specimens
from prefect.orion.schemas.states import Failed
from torch_web.prefect_flows.tasks import save_specimen
from sqlalchemy import create_engine, or_, select
from sqlalchemy.orm import Session



@task
def check_duplicate(img: specimens.SpecimenImage, config):
    max_distance = 35
    
    img_hash = specimens.hash(img.url)
    split_hash = [result[i:i+4] for i in range(0, len(img_hash), 4)]
    split_filter = or_(SpecimenImage.hash_a == split_hash[0],
                       SpecimenImage.hash_b == split_hash[1],
                       SpecimenImage.hash_c == split_hash[2],
                       SpecimenImage.hash_d == split_hash[3])

    engine = create_engine(config["SQLALCHEMY_DATABASE_URI"], future=True)
    with Session(engine) as session:
        similar_images = session.scalars(select(specimens.SpecimenImage).filter(split_filter))
        too_close_images = [sim for sim in similar_images if abs(sim.average_hash() - img_hash) < max_distance]
    
    if len(too_close_images) > 0:
        return Failed(message=f"Specimen image {img.id} is too similar to {too_close_images[0].url}")

    save_specimen.save_specimen_image(img, config)
