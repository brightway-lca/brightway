from brightway import backend_mapping
from brightway.projects import ProjectManager
import pytest
import shutil
import tempfile


class MockBackendConfig:
    def __init__(self):
        self.path = None

    def activate(self, dirpath):
        self.path = dirpath

    def deactivate(self):
        self.path = None


config = MockBackendConfig()
backend_mapping['tests'] = config


@pytest.fixture
def temp_projects(scope="function"):
    td = tempfile.mkdtemp()
    yield ProjectManager(td)
    if config.dirpath:
        config.deactivate()
    shutil.rmtree(td)
