import argparse
from watchdog_handler import HubHandler

if __name__ == "__main__":
    description = "Create an observer to the given directory and runs the TORCH workflow when a file is added"

    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "-d",
        "--directory",
        required=True,
        help="Path to the directory that should be watched",
    )

    parser.add_argument(
        "-w",
        "--workflowid",
        required=True,
        help="Prefect workflow ID that will be triggered when a file is added",
    )

    args = parser.parse_args()

    print(args.directory)
    # todo create a command or agument to activate from database (table WorkflowSettings)

    HubHandler(args.workflowid, args.directory)
