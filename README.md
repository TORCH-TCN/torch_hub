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

App specific configs: The current version needs a `config.json` file inside the `src/torch` folder with the following format (use [config_example.json](src/torch/config_example.json) as a template)

```json
{ 
    "SECRET_KEY": "",
    "SQLALCHEMY_DATABASE_URI": "sqlite:///torch-hub.db",
    "SQLALCHEMY_DATABASE_URI_PREFECT": "sqlite:///src/torch/torch-hub.db",
    "SECURITY_REGISTERABLE": true,
    "SECURITY_PASSWORD_SALT": "",
    "SECURITY_SEND_REGISTER_EMAIL": false,
    "SECURITY_RECOVERABLE": true,
    "SECURITY_CHANGEABLE": true,
    "SQLALCHEMY_TRACK_MODIFICATIONS": false,
    "MAIL_SERVER": "",
    "MAIL_USERNAME": "",
    "MAIL_PASSWORD": "",
    "MAIL_DEFAULT_SENDER": "",
    "MAIL_PORT": 587,
    "MAIL_USE_SSL": true,
    "MAIL_USE_TLS": true,
    "APP_URL": "http://localhost:5000",
    "PREFECT_ORION_URL": "http://127.0.0.1:4200/"
}
```

Workflow specific configs:
Workflow configs should be added inside the `src/torch/prefect_flows/configs` folder, example: `workflow_name_config.json`, this file should be loaded from the workflow function as necessary check [flow_template_config.json](src/torch/prefect_flows/configs/flow_template_config.json) and [flow_template.py](src/torch/prefect_flows/templates/flow_template.py). There is a process_specimen workflow on this solution, use the [process_specimen_config_example.json](src/torch/prefect_flows/configs/process_specimen_config_example.json) as template.

## How to create a new workflow
1. Add a new flow file inside `src/torch/prefect_flows/` folder following the [flow template](src/torch/prefect_flows/templates/flow_template.py)
2. Register the new flow on the `run_workflow` function at [workflow.py](src/torch/collections/workflow.py)

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
After running the web app for the first time the database and admin role are created and you should be able to Sign Up and create a new user from the Sign Up page.

To assign the admin role to your user navigate to `src/torch` and access the database `sqlite3 torch-hub.db` and then execute the command `INSERT INTO roles_users (your_user_id, 1)`