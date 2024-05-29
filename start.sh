#!/bin/bash
source /home/ubuntu/ayudatek-template/venv/bin/activate
cd /home/ubuntu/ayudatek-template
python manage.py makemigrations
python manage.py migrate
exec python manage.py runserver
