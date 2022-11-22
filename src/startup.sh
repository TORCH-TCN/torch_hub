#!/bin/bash
apt-get update
apt-get install zbar-tools
gunicorn --bind=0.0.0.0 --timeout 600 app:app