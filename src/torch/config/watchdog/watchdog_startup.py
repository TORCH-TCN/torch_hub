import watchdog.events
import watchdog.observers

class HubHandler(watchdog.events.PatternMatchingEventHandler):
    def __init__(self):
        super().__init__(patterns=['*.png'], ignore_patterns=None, ignore_directories=False,case_sensitive=True)        
    
    def on_created(self, event):
        print(f"file created at {event.src_path}")
        return super().on_created(event)
    
    def on_deleted(self, event):
        print(f"file deleted at {event.src_path}")
        return super().on_deleted(event)


event_handler = HubHandler()
observer = watchdog.observers.Observer()
observer.schedule(event_handler, r'C:\Users\anton\Documents\GitHub\torch_hub\src\torch\file-upload', recursive=True)
observer.start()
observer.join()