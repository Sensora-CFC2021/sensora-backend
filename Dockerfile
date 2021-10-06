# Use an official Python runtime as a parent image
FROM python:3.7

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# cron
RUN apt-get update && apt-get -y install cron

COPY crontab /etc/cron.d/crontab

RUN chmod 0644 /etc/cron.d/crontab
RUN /usr/bin/crontab /etc/cron.d/crontab


# Adding backend directory to make absolute filepaths consistent across services
WORKDIR /usr/share/nginx/html/backend

# Install Python dependencies
COPY requirements.txt /usr/share/nginx/html/backend
RUN pip install -r requirements.txt
RUN pip install gunicorn

COPY . .

#RUN touch cron.log
RUN chmod +x run_cron.sh

# Make port 8000 available for the app
EXPOSE 8000

