from bw_projects.base_dir import get_base_directories
import os
import pytest
import tempfile


@pytest.fixture()
def clean():
    yield
    del os.environ["BRIGHTWAY_DIR"]


def test_clean_environment_beginning():
    with pytest.raises(KeyError):
        os.environ["BRIGHTWAY_DIR"]


def test_from_env_var(clean):
    with tempfile.TemporaryDirectory() as td:
        os.environ["BRIGHTWAY_DIR"] = str(td)
        base, logs = get_base_directories()
        assert str(td) in str(base)


def test_invalid_env_var(clean):
    os.environ["BRIGHTWAY_DIR"] = "nothing special"
    with pytest.raises(OSError):
        get_base_directories()


def test_clean_environment_ending():
    with pytest.raises(KeyError):
        os.environ["BRIGHTWAY_DIR"]


def test_directories():
    data, logs = get_base_directories()
    assert os.path.isdir(data)
    assert os.path.isdir(logs)
