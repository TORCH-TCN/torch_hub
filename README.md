# TORCH Hub

This repository is currently a reference implementation of a Prefect-based architecture with 1 flow and 3 tasks.

When you run this reference implementation:

- all files in the directory will be read 
- each file will be uploaded to the location specified in the config
- a log file `newfiles.txt` will be added to the same directory with a full list of the new URLs for all uploaded files

This demonstrates a full working end-to-end Prefect workflow for a group of files.

In addition, two execution flows have been implemented:

- Local, Linear, & Synchronous: Processes files one by one in sequence (no -p argument provided)
- Parallel and Multithreaded: Processes files in parallel using a built-in Dask Executor (-p argument provided)

## Installation

All dependencies are listed in requirements.txt:
```bash
    pip install -r requirements.txt
```

## How to run

Once the dependencies are installed, run the workflow as follows:

```bash
    python3 torch.py -d c:\users\me\FilesToProcess -c .\config\example-config.json -p
```

Arguments to the application are as follows:

- `-d` (or `--directory`): The directory name to process
- `-c` (or `--config`): The JSON config file to use 
- `-p` (or `--parallel`): Process files in parallel using a built-in Dask Executor
- `-h` (or `--help`): See documentation for this app