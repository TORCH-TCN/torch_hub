from torch import db, socketio
from torch.prefect_flows.process_specimen import process_specimen

def run_workflow(collection,specimen,config):
    notify_specimen_update(specimen,"Running")

    match collection.workflow:
        case 'process_specimen':
            state = process_specimen(collection, specimen,config, return_state=True)
        case _:
            raise NotImplementedError 
    
    notify_specimen_update(specimen,state.name)


def notify_specimen_update(specimen,state):
    db.session.refresh(specimen)
    socketio.emit('notify',{"id":specimen.id, "name": specimen.name, "cardimg": specimen.card_image(), "create_date": str(specimen.create_date), "flow_run_state":state, "failed_task": specimen.failed_task})
