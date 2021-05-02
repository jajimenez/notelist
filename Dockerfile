# Notelist 0.1.0 Dockerfile - Jose A. Jimenez (jajimenezcarm@gmail.com)
#
# Build the image:
#     docker image build -t notelist .
#
# Run a container in the background from the image:
#     docker container run --name notelist -d -p 5000:5000 \
#         -e NOTELIST_DB_URI=<uri> notelist
#
#     uri: Database URI (string). Example: sqlite:////usr/src/notelist.db
#
# Create all the tables of the database for the running container:
#     docker container exec -it notelist upgrade-db
#
# Create an application user for the running container:
#     docker container exec -it notelist create-user <username> <password> \
#         <admin> <enabled> <name> <email>
#
#     username: Username (string).
#     password: Password (string).
#     admin: Whether the user is an administrator or not (integer: 0 or 1).
#     enabled: Whether the user is enabled or not (integer: 0 or 1).
#     name: Name or full name (string, optional).
#     email: E-mail (string, optional).

# Base image
FROM python:3.9-slim

# Set working directory
WORKDIR /tmp

# Update the APT index, install packages needed for building Psycopg (needed
# for PostgreSQL) and delete APT temporary files.
RUN apt-get update && \
    apt-get install -y build-essential python3-dev libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Build and install the Wheel and Psycopg2 Python packages, uninstall unneeded
# APT packages and delete APT temporary files.
RUN pip install --no-cache-dir wheel psycopg2==2.8.6 && \
    apt-get purge -y build-essential python3-dev libpq-dev && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Copy Notelist source files
COPY . .

# Generate Notelist wheel package, install it and delete source files.
RUN python setup.py bdist_wheel && \
    pip install --no-cache-dir ./dist/notelist-* && \
    rm -rf *

# Set Flask environment variable
ENV FLASK_APP=notelist

# Create scripts
ENV BIN_DIR=/usr/bin
ENV UPGRADE_DB_SCRIPT=$BIN_DIR/upgrade-db
ENV CREATE_USER_SCRIPT=$BIN_DIR/create-user

RUN echo '#!/bin/bash\nflask db upgrade -d $(flask path migrations)' > $UPGRADE_DB_SCRIPT && \
    echo '#!/bin/bash\nflask user create $1 $2 $3 $4 $5 $6' > $CREATE_USER_SCRIPT && \
    chmod +x $UPGRADE_DB_SCRIPT && \
    chmod +x $CREATE_USER_SCRIPT

# Set working directory
WORKDIR /

# Run the Gunicorn WSGI web server for Notelist on port 5000 with 4 worker
# processes.
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--access-logfile", \
    "/usr/src/access.log", "--error-logfile", "/usr/src/error.log", \
    "notelist:app"]
