# This is a Dockerfile for ...

# Use the Python base image
ARG VARIANT="3.11-bullseye"
FROM mcr.microsoft.com/devcontainers/python:0-${VARIANT} AS dev-base

USER vscode

# Define the version of Poetry to install (default is 1.5.1)
# Define the directory of python virtual environment
ARG PYTHON_VIRTUALENV_HOME=/home/vscode/meche-copilot-py-env \
    POETRY_VERSION=1.5.1

ENV POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_NO_INTERACTION=true 

# Create a Python virtual environment for Poetry and install it
RUN python3 -m venv ${PYTHON_VIRTUALENV_HOME} && \
    $PYTHON_VIRTUALENV_HOME/bin/pip install --upgrade pip && \
    $PYTHON_VIRTUALENV_HOME/bin/pip install poetry==${POETRY_VERSION}

ENV PATH="$PYTHON_VIRTUALENV_HOME/bin:$PATH" \
    VIRTUAL_ENV=$PYTHON_VIRTUALENV_HOME

# Setup for bash
RUN poetry completions bash >> /home/vscode/.bash_completion && \
    echo "export PATH=$PYTHON_VIRTUALENV_HOME/bin:$PATH" >> ~/.bashrc

# Set the working directory for the app
WORKDIR /workspaces/meche-copilot

# Use a multi-stage build to install dependencies
FROM dev-base AS dev-dependencies

ARG PYTHON_VIRTUALENV_HOME

# Copy the rest of the source code (this layer will be invalidated and rebuilt whenever the source code changes)
COPY . .

# Install camelot dependencies (https://camelot-py.readthedocs.io/en/master/user/install-deps.html#install-deps)
USER root
RUN apt-get update && apt-get install -y ghostscript python3-tk
RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6
USER vscode

# Install the Poetry dependencies (this layer will be cached as long as the dependencies don't change)
RUN poetry install --no-interaction --no-ansi --with test,eval,docs
