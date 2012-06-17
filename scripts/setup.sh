#!/bin/bash

set -e

# config
SOURCE_DIRECTORY=.
HOSTNAME=inquisition.example.com
INQUISITION_ROOT=/srv/www/inquisition

# dependencies
aptitude -q=9 -y install supervisor nginx python-virtualenv 

# deployment directory
export INQUISITION_ROOT
mkdir -p $INQUISITION_ROOT
cp -R $SOURCE_DIRECTORY/* $INQUISITION_ROOT/

# virtualenv
cd $INQUISITION_ROOT
virtualenv .
source bin/activate
pip install -r requirements.txt

# nginx config
cat > /etc/nginx/sites-available/inquisition <<EOF
server {
    listen 80;

    server_name $HOSTNAME;

    access_log  /var/log/nginx/inquisition-access.log;
    error_log  /var/log/nginx/inquisition-error.log;

    location / {
        proxy_pass         http://127.0.0.1:8000/;
        proxy_redirect     off;

        proxy_set_header   Host             \$host;
        proxy_set_header   X-Real-IP        \$remote_addr;
        proxy_set_header   X-Forwarded-For  \$proxy_add_x_forwarded_for;
    }
}
EOF
ln -s /etc/nginx/sites-available/inquisition /etc/nginx/sites-enabled/inquisition

# Supervisor config
cat > /etc/supervisor/conf.d/inquisition.conf <<EOF
[program:inquisition]
command=/srv/www/inquisition/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app
directory=$INQUISITION_ROOT
user=nobody
autostart=true
autorestart=true
redirect_stderr=True
EOF

# Restart the things
/etc/init.d/supervisor stop
/etc/init.d/supervisor start
/etc/init.d/nginx restart

