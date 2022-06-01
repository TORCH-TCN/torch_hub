from multiprocessing.dummy import freeze_support
import argparse
from prefect.executors import DaskExecutor, LocalExecutor
from config.TorchConfig import TorchConfig
from flows.process_specimen import process_specimen
from torch.config.TorchDatabase import TorchDatabase
# from flows.herbar_flow import herbar_flow

if __name__ == '__main__':
    freeze_support()

    description = "Runs the TORCH workflow on a file or directory."

    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("-d", '--directory',
                        required=True,
                        help="Path to the directory that contains the images"
                        "to be analyzed.")

    parser.add_argument("-c", '--config', help="the config file to use",
                        default='config/config.json')

    parser.add_argument("-p", '--parallel',
                        help="process files in parallel",
                        action="store_true")

    parser.add_argument("-o", "--output", nargs='?',
                        default='primary',
                        const='secondary',
                        help="Path to the directory where log file is written."
                        "By default (no -o switch used) log will be written to"
                        "location of script."
                        "If just the -o switch is used, log is written to"
                        "directory indicated in source argument."
                        "An absolute or relative path may also be provided.")

    parser.add_argument("-n", "--no_rename", required=False,
                        action='store_true',
                        help="Files will not be renamed, only log"
                        "file generated.")

    parser.add_argument("-v", "--verbose", required=False, action='store_true',
                        help="Detailed output for each file processed.")

    args = parser.parse_args()
    config = TorchConfig.from_json(args.config)
    db = TorchDatabase(config['SQLALCHEMY_DATABASE_URI'])

    # todo adapt to pass parameters through config
    # herbar_flow.run(path=args.directory,
    #                 default_prefix=args.default_prefix,
    #                 no_rename=args.no_rename,
    #                 code=args.code,
    #                 verbose=args.verbose,
    #                 jpeg_rename=args.jpeg_rename,
    #                 executor=DaskExecutor() if args.parallel
#                     else LocalExecutor())

    process_specimen.run(path=args.directory,
                         config=config,
                         db=db,
                         executor=DaskExecutor() if args.parallel
                         else LocalExecutor())
