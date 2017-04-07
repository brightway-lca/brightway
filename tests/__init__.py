from .backend_mock import config
from brightway import backend_mapping
from brightway.projects import ProjectManager
import pytest
import shutil
import tempfile


@pytest.fixture
def temp_projects(scope="function"):
    td = tempfile.mkdtemp()
    yield ProjectManager(td)
    shutil.rmtree(td)


@pytest.fixture
def augmented_mapping():
    for key in list(backend_mapping):
        del backend_mapping[key]
    backend_mapping['tests'] = config
