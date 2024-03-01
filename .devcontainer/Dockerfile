FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

# Install needed tools for compiling the Psycopg2 Python package, Poetry and
# the project development dependencies.
RUN apt-get update && \
    apt-get install -y build-essential python3-dev libpq-dev && \
    python -m pip install --upgrade pip && \
    pip install poetry
