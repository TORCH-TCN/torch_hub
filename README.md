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

App specific configs: The current version needs a `config.json` file inside the `src/torch` folder with the following format

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
Workflow configs should be added inside the `src/torch/tasks` folder, example: `workflow_name_config.json`, this file should be loaded from the workflow function as necessary

## How to run

Once the dependencies are installed, run the app as follows:
Navigate to the `src` folder and run
```bash
python3 torch.py
```
or you can also run at Visual Studio Code, make sure the `launch.json` file is at the same directory as the `torch.py`, open the `torch.py` and select the `Run and Debug` menu

## Prefect server

Observe your flow runs in the Prefect UI
Fire up the Prefect UI locally by entering this command in your terminal:
```bash
prefect orion start
```
Follow the link in your terminal to see the dashboard.
