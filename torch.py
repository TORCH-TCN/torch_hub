from multiprocessing.dummy import freeze_support
import argparse
from prefect.executors import DaskExecutor, LocalExecutor
from config.TorchConfig import TorchConfig
from flows.process_specimen import process_specimen


if __name__ == '__main__':
    freeze_support()

    description = "Runs the TORCH workflow on a file or directory."

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-d", '--directory', help="the directory to process")
    parser.add_argument("-c", '--config', help="the config file to use")
    parser.add_argument("-p", '--parallel',
                        help="process files in parallel",
                        action="store_true")

    args = parser.parse_args()

    print(args)

    process_specimen.run(path=args.directory,
                         config=TorchConfig.from_json(args.config),
                         executor=DaskExecutor() if args.parallel
                         else LocalExecutor())
