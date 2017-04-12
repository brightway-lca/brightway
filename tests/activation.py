from . import temp_projects
from brightway import backend_mapping
from brightway.projects import Project


def test_setup(temp_projects):
    temp_projects.create("foo", backend="tests")
    assert 'tests' in backend_mapping
    p = Project.get(name='foo')
    assert not p.data
    assert p.backend == 'tests'

def test_create_project(temp_projects):
    temp_projects.create("foo", backend="tests", switch=False)

def test_select_project(temp_projects):
    temp_projects.create("foo", backend="tests", switch=False)
    temp_projects.select("foo")
    assert temp_projects.current.name == 'foo'

def test_create_switch_project(temp_projects):
    temp_projects.create("foo", backend="tests")
    assert temp_projects.current.name == 'foo'
