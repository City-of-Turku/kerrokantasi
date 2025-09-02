# Dockerfile for Kerrokantasi backend
# Attemps to provide for both local development and server usage

FROM python:3.7-bullseye as appbase

RUN useradd -ms /bin/bash -d /kerrokantasi kerrokantasi

WORKDIR /kerrokantasi

# Can be used to inquire about running app
# eg. by running `echo $APP_NAME`
ENV APP_NAME kerrokantasi
# This is server out by Django itself, but aided
# by whitenoise by adding cache headers and also delegating
# much of the work to WSGI-server
ENV STATIC_ROOT /srv/static
# For some reason python output buffering buffers much longer
# while in Docker. Maybe the buffer is larger?
ENV PYTHONUNBUFFERED True

# less & netcat-openbsd are there for in-container manual debugging
# kerrokantasi needs gdal
RUN apt-get update && apt-get install -y postgresql-client less netcat-openbsd gettext locales gdal-bin python-gdal python3-gdal dialog openssh-server

# we need the Finnish locale built
RUN sed -i 's/^# *\(fi_FI.UTF-8\)/\1/' /etc/locale.gen
RUN locale-gen

RUN pip install --no-cache-dir uwsgi

# Sentry CLI for sending events from non-Python processes to Sentry
# eg. https://docs.sentry.io/cli/send-event/#bash-hook
RUN curl -sL https://sentry.io/get-cli/ | bash

# Copy requirements files to image for preloading dependencies
# in their own layer
COPY requirements.txt ./

# deploy/requirements.txt must reference the base requirements
RUN pip install --no-cache-dir -r requirements.txt

# Enable SSH
RUN echo "root:Docker!" | chpasswd
COPY sshd_config /etc/ssh/

COPY . .

# Statics are kept inside container image for serving using whitenoise
ENV DEBUG=True
RUN mkdir -p /srv/static && python manage.py collectstatic

# Keep media in its own directory outside home, in case home
# directory forms some sort of attack route
# Usually this would be some sort of volume
# RUN mkdir -p /srv/media && chown hauki:hauki /srv/media

# Add cron

RUN echo '22 2 * * * cd /var/www/kerrokantasi-back/app/; /var/www/kerrokantasi-back/venv37/bin/python manage.py clean_expired_users' >> /etc/crontab
RUN printenv > /etc/environment

RUN chmod a+x ./deploy/entrypoint.sh
ENTRYPOINT ["deploy/entrypoint.sh"]

# Both production and dev servers listen on port 8000
EXPOSE 8000

# Next, the development & testing extras
FROM appbase as development

RUN pip install --no-cache-dir -r requirements-dev.txt

# And the production image
FROM appbase as production

ENV DEBUG=False
