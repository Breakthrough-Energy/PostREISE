# Dockerfile for production docker instance of Django server
# We put it on the top level in order to access static assets in the front end
# This is a multi-stage build so that we don't have to install Node in the
# final container

# Stage 1: create front end build artifacts
# TODO: make library compatible with node >= 18
FROM node:16 as frontend-build-deps

WORKDIR /frontend
COPY ./frontend/package.json ./frontend/yarn.lock ./
RUN yarn
COPY ./frontend /frontend
RUN yarn build


# Stage 2: set up ssh, set up python, copy over static files
FROM python:3.9.2

ENV SSH_PASSWD "root:Docker!"
ENV DJANGO_SETTINGS_MODULE "cenacs.settings.production"

# Set up SSH
RUN apt-get update && apt-get install -y --no-install-recommends \
  dialog \
  openssh-server \
  && rm -rf /var/lib/apt/lists/* \
  && echo "$SSH_PASSWD" | chpasswd

COPY sshd_config /etc/ssh/

# Install Python dependencies
WORKDIR /app/backend
COPY ./backend/requirements.txt ./backend/manage.py /app/backend/
COPY ./backend/cenacs /app/backend/cenacs/
RUN pip3 install --upgrade pip -r requirements.txt

# Move all static files other than index.html to root for whitenoise middleware
# Add the rest of the code
WORKDIR /app/frontend
COPY --from=frontend-build-deps /frontend/build /app/frontend/build

WORKDIR /app/frontend/build
RUN mkdir root \
  && mv *.ico *.json root \
  && mkdir /app/backend/staticfiles

WORKDIR /app

# Dummy env vars are included here to avoid raising an error
# when generating static files.
RUN SECRET_KEY=buildOnlySecretKey \
  COSMOS_KEY=buildOnlyCosmosKey \
  COSMOS_DB_NAME=buildOnlyCosmosDbName \
  COSMOS_ENDPOINT=buildOnlyCosmosEndpoint \
  PRODUCTION_HOST=buildOnlyProductionHost \
  CRM_AUTHORITY=buildOnlyEnvVar \
  CRM_CLIENT_ID=buildOnlyEnvVar \
  CRM_ENDPOINT=buildOnlyEnvVar \
  CRM_SCOPE=buildOnlyEnvVar \
  CRM_SECRET=buildOnlyEnvVar \
  AZURE_INSTRUMENTATION_KEY=buildOnlyEnvVar \
  python3 backend/manage.py collectstatic --noinput

# Export $PORT from env and port 2222 for ssh
EXPOSE $PORT 2222

RUN adduser --system --home=/app \
  --no-create-home --disabled-password --group \
  --shell=/bin/bash cenacs

RUN chgrp -R cenacs /app
RUN chmod -R o= /app

COPY init.sh /usr/local/bin/
RUN chmod u=rwx,g=,o= /usr/local/bin/init.sh

ENTRYPOINT ["init.sh"]
