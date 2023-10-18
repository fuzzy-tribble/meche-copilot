"""
Pytest configuration file for unit tests.
"""

import pytest
import os
import shutil
from pathlib import Path

TEST_OUTPUT_DIR = Path('./_test_results')

def pytest_sessionstart(session):
    if os.path.exists(TEST_OUTPUT_DIR):
        shutil.rmtree(TEST_OUTPUT_DIR)
    os.mkdir(TEST_OUTPUT_DIR)

def pytest_addoption(parser):
    # a hook for adding command line options
    parser.addoption("--vis", action="store_true", default=False, help="Enable debug visualizations (output to data/.cache)")

@pytest.fixture(scope="session")
def visualize(pytestconfig):
    vis = True if pytestconfig.getoption("--vis") else False
    return vis

@pytest.fixture(scope="session")
def session():
    from meche_copilot.utils.config import load_config, find_config
    from meche_copilot.schemas import SessionConfig, Session
    
    config = SessionConfig.from_yaml(find_config('session-config.yaml'))
    sess = Session.from_config(config=config)

    return sess