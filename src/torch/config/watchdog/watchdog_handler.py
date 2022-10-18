import watchdog.events
import watchdog.observers


class HubHandler(watchdog.events.PatternMatchingEventHandler):
    def __init__(self, workflowid, path):
        super().__init__(
            patterns=["*.png", "*.dng", "*.jpg", "*.jpeg"],
            ignore_patterns=None,
            ignore_directories=False,
            case_sensitive=True,
        )

        path = "../../static/watch-uploads/"
        self.workflowid = workflowid
        observer = watchdog.observers.Observer()
        observer.schedule(self, path, recursive=True)
        observer.start()
        observer.join()

    def on_created(self, event):
        print(f"file created at {event.src_path} - run workflow {self.workflowid}")
        # todo trigger the respective workflow everytime a file is added to this path
        return super().on_created(event)

    def on_deleted(self, event):
        print(f"file deleted at {event.src_path}")
        return super().on_deleted(event)
