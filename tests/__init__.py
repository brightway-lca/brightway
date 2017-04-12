from brightway import backend_mapping
from brightway.projects import ProjectManager
import pytest
import shutil
import tempfile


class MockBackendConfig:
    def __init__(self):
        self.dirpath = None

    def activate(self, dirpath):
        self.dirpath = dirpath

    def deactivate(self):
        self.dirpath = None


@pytest.fixture
def temp_projects(scope="function"):
    td = tempfile.mkdtemp()

    config = MockBackendConfig()
    backend_mapping['tests'] = config

    yield ProjectManager(td)
    if config.dirpath:
        config.deactivate()
    shutil.rmtree(td)
