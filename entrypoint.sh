#!/bin/bash
printenv | sed 's/^\(.*\)$/export \1/g'  > /project_env.sh

echo "Collect static files"
python manage.py collectstatic --no-input 
echo "Apply database migrations"
python manage.py migrate 
echo "Starting server"
gunicorn  src.wsgi -c gunicorn.conf.py --daemon

echo "Cron start"
cron -f


