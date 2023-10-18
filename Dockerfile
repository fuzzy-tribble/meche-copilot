# This is a Dockerfile for ...

ARG POETRY_HOME=/opt/poetry

# Base image
FROM python:3.11 AS builder

# Define the version of Poetry to install
ARG POETRY_VERSION=1.5.1

# Define the directory to install Poetry to (default is /opt/poetry)
ARG POETRY_HOME

# Create a Python virtual environment for Poetry and install it
RUN python3 -m venv ${POETRY_HOME} && \
    $POETRY_HOME/bin/pip install --upgrade pip && \
    $POETRY_HOME/bin/pip install poetry==${POETRY_VERSION}

# Test if Poetry is installed in the expected path
RUN echo "Poetry version:" && $POETRY_HOME/bin/poetry --version

# Set working directory
WORKDIR /app

# Use multi-stage build to install dependencies
FROM builder as dependencies

ARG POETRY_HOME

# Copy only the dependency files for installation
COPY pyproject.toml poetry.lock* poetry.toml ./

# Install camelot dependencies (https://camelot-py.readthedocs.io/en/master/user/install-deps.html#install-deps)
RUN apt-get update && apt-get install -y ghostscript python3-tk

# Install the Poetry dependencies (this layer will be cached as long as the dependencies don't change)
RUN $POETRY_HOME/bin/poetry install --no-interaction --no-ansi --with test
# TODO - I think this install should be --without test,lint,typing,eval,docs

# Use a multi-stage build to run tests
FROM dependencies AS tests

# Copy the rest of the app source code (this layer will be invalidated and rebuilt whenever the source code changes)
COPY . .

RUN /opt/poetry/bin/poetry install --no-interaction --no-ansi --with test

# Set the entrypoint to run tests using Poetry
ENTRYPOINT ["/opt/poetry/bin/poetry", "run", "pytest"]

# Set the default command to run all unit tests
CMD ["tests/foo_test.py"]

# # Use a multi-stage build to run the app
# FROM dependencies AS app