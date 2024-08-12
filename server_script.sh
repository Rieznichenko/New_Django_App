#!/bin/bash

# Update the package list
echo "Updating package list..."
sudo apt-get update

# Install necessary packages
echo "Installing required packages..."
sudo apt-get install -y python3 python3-venv python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx curl supervisor redis-server

# Start and enable Redis service
echo "Starting and enabling Redis..."
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Set the virtual environment name
VENV_NAME="venv"

# Check if the virtual environment exists and delete it if it does
if [ -d "$VENV_NAME" ]; then
    echo "Removing existing virtual environment..."
    rm -rf "$VENV_NAME"
fi

# Create a new virtual environment
echo "Creating new virtual environment..."
python3 -m venv "$VENV_NAME"

# Activate the virtual environment
source "$VENV_NAME/bin/activate"

# Install requirements
if [ -f "requirements.txt" ]; then
    echo "Installing requirements from requirements.txt..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found!"
fi

# Run Django migrations
echo "Running Django migrations..."
python manage.py migrate

echo "Setup complete. Virtual environment '$VENV_NAME' is ready, activated, and migrations are applied."

# Supervisor configuration for Django, Celery worker, and Celery Beat
SUPERVISOR_CONF_DIR="/etc/supervisor/conf.d"
DJANGO_CONF="$SUPERVISOR_CONF_DIR/django.conf"
CELERY_WORKER_CONF="$SUPERVISOR_CONF_DIR/celery_worker.conf"
CELERY_BEAT_CONF="$SUPERVISOR_CONF_DIR/celery_beat.conf"

# Create Supervisor config for Django
echo "Creating Supervisor config for Django..."
sudo tee "$DJANGO_CONF" > /dev/null <<EOL
[program:django]
command=/home/ayudatek-template/$VENV_NAME/bin/python /home/ayudatek-template/manage.py runserver 0.0.0.0:8000
directory=/home/ayudatek-template
autostart=true
autorestart=true
stderr_logfile=/var/log/django.err.log
stdout_logfile=/var/log/django.out.log
EOL

# Create Supervisor config for Celery worker
echo "Creating Supervisor config for Celery worker..."
sudo tee "$CELERY_WORKER_CONF" > /dev/null <<EOL
[program:celery_worker]
command=/home/ayudatek-template/$VENV_NAME/bin/celery -A gpt_discord worker --loglevel=info
directory=/home/ayudatek-template
autostart=true
autorestart=true
stderr_logfile=/var/log/celery_worker.err.log
stdout_logfile=/var/log/celery_worker.out.log
EOL

# Create Supervisor config for Celery Beat
echo "Creating Supervisor config for Celery Beat..."
sudo tee "$CELERY_BEAT_CONF" > /dev/null <<EOL
[program:celery_beat]
command=/home/ayudatek-template/$VENV_NAME/bin/celery -A gpt_discord beat --loglevel=info
directory=/home/ayudatek-template
autostart=true
autorestart=true
stderr_logfile=/var/log/celery_beat.err.log
stdout_logfile=/var/log/celery_beat.out.log
EOL

# Update Supervisor to read new configuration
echo "Updating Supervisor configuration..."
sudo supervisorctl reread
sudo supervisorctl update

# Nginx configuration
NGINX_CONF_DIR="/etc/nginx/sites-available"
NGINX_CONF_FILE="$NGINX_CONF_DIR/ayudatek_template.conf"

# Create Nginx configuration file
echo "Creating Nginx configuration..."
sudo tee "$NGINX_CONF_FILE" > /dev/null <<EOL
upstream backend {
    server localhost:8000;
}

server {
    listen 443 ssl;
    server_name ia.humanytek.com;

    ssl_certificate /etc/ssl/certs/ssl-cert-snakeoil.pem;
    ssl_certificate_key /etc/ssl/private/ssl-cert-snakeoil.key;

    location / {
        proxy_pass http://backend/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;

        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Nginx-Proxy true;

        proxy_redirect off;
    }
}
EOL

# Create a symbolic link to enable the site
echo "Enabling Nginx configuration..."
sudo ln -s "$NGINX_CONF_FILE" /etc/nginx/sites-enabled/

# Test Nginx configuration
echo "Testing Nginx configuration..."
sudo nginx -t

# Restart services
echo "Restarting services..."
sudo systemctl restart nginx
sudo systemctl restart supervisor

echo "All services restarted successfully."
