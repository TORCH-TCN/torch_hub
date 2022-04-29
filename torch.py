from multiprocessing.dummy import freeze_support
import argparse
from prefect.executors import DaskExecutor, LocalExecutor
from flows.process_file import process_file


if __name__ == '__main__':
    freeze_support()

    description = "Runs the TORCH workflow on a file or directory."

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-d", '--directory', help="the directory to process")
    parser.add_argument("-p", '--parallel',
                        help="process files in parallel",
                        action="store_true")

    args = parser.parse_args()

    print(args)

    process_file.run(path=args.directory,
                     executor=DaskExecutor() if args.parallel
                     else LocalExecutor())
