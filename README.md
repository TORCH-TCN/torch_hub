# TORCH Hub

This repository has a flask app that triggers and manages a prefect workflow


## Requirements

Requires Python 3.10*

## Installation

All dependencies are listed in requirements.txt:
```bash
pip install -r requirements.txt
```

## Configuration

App specific configs: The current version needs a `.env` file inside the `src/torch` folder. Use [.env.sample](src/.env.sample) as a template.

Workflow specific configs:
Workflow configs should be added inside the `src/torch/prefect_flows/configs` folder, example: `workflow_name_config.json`, this file should be loaded from the workflow function as necessary check [flow_template_config.json](src/torch_hub/prefect_flows/configs/flow_template_config.json) and [flow_template.py](src/torch_hub/prefect_flows/templates/flow_template.py). There is a process_specimen workflow on this solution, use the [process_specimen_config_example.json](src/torch_hub/prefect_flows/configs/process_specimen_config_example.json) as template.

## How to create a new workflow
1. Add a new flow file inside `src/torch/prefect_flows/` folder following the [flow template](src/torch_hub/prefect_flows/templates/flow_template.py)
2. Register the new flow on the `run_workflow` function at [workflow.py](src/torch_hub/collections/workflow.py)

## How to run

Once the dependencies are installed, run the app as follows:
Navigate to the `src` folder and run
```bash
python3 app.py
```
or you can also run at Visual Studio Code, make sure the `launch.json` file is at the same directory as the `app.py`, open the `app.py` and select the `Run and Debug` menu

## Prefect server

Observe your flow runs in the Prefect UI
Fire up the Prefect UI locally by entering this command in your terminal:
```bash
prefect orion start
```
Follow the link in your terminal to see the dashboard.

## Adding an admin user
After running the web app for the first time, the database and admin role are created automatically, and you should be able to Sign Up and create a new user from the Sign-Up page.

To assign the admin role to your user navigate to `src/torch` and access the database `sqlite3 torch-hub.db` and then execute the command `INSERT INTO roles_users (your_user_id, 1)`