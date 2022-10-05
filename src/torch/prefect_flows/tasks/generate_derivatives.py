from pathlib import Path
from prefect import task
from PIL import Image
from torch.collections.specimens import Specimen, SpecimenImage
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import prefect
from prefect.orion.schemas.states import Failed
from tasks.save_specimen import save_specimen

@task
def generate_derivatives(specimen: Specimen, flow_config, app_config):

    engine = create_engine(app_config["SQLALCHEMY_DATABASE_URI"], future=True)
    flow_run_id = prefect.context.get_run_context().task_run.flow_run_id.hex

    with Session(engine) as session:

        try:
            local_specimen = session.merge(specimen) #thread-safe
            
            derivatives_to_add = {
                size: config
                for size, config in flow_config["GENERATE_DERIVATIVES"]["SIZES"].items()
                if is_missing(local_specimen.images, size)
            }

            for derivative in derivatives_to_add.keys():
                new_derivative = generate_derivative(
                    local_specimen, derivative, derivatives_to_add[derivative]
                )
                local_specimen.images.append(new_derivative)

            session.commit()

            save_specimen(local_specimen,app_config,flow_run_id)
        except:
            session.commit()
            save_specimen(specimen,app_config,flow_run_id,'Failed','generate_derivatives')
            return Failed(message=f"Unable to create derivatives for specimen {specimen.id}-{specimen.name}")
        finally:
            session.close()


def is_missing(images, size):
    return not any(image.size == size for image in images)


def generate_derivative(specimen: Specimen, size, flow_config) -> SpecimenImage:
    full_image_path = Path(specimen.upload_path)
    derivative_file_name = full_image_path.stem + "_" + size + full_image_path.suffix
    derivative_path = str(full_image_path.parent.joinpath(derivative_file_name))

    try:
        img = Image.open(specimen.upload_path)
        
        if size != 'FULL':
            img.thumbnail((flow_config["WIDTH"], flow_config["WIDTH"]))
        
        img.save(derivative_path)
        
        return SpecimenImage(
            specimen_id=specimen.id,
            size=size,
            height=flow_config["WIDTH"] if size != 'FULL' else img.height,
            width=flow_config["WIDTH"] if size != 'FULL' else img.width,
            url=derivative_path
        )
    except Exception as e:
        print("Unable to create derivative:", e)
        return None
