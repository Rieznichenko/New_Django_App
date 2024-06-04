#!/bin/bash

# Activate the virtual environment
source /home/ubuntu/ayudatek-template/venv/bin/activate

# Start Celery worker
celery -A gpt_discord worker --loglevel=info &

# Start Celery beat
celery -A gpt_discord beat --loglevel=info &
