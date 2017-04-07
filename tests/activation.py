from . import temp_projects, augmented_mapping


def test_create_project(temp_projects, augmented_mapping):
    temp_projects.create("foo", backend="tests", switch=False)

def test_select_project(temp_projects, augmented_mapping):
    temp_projects.create("foo", backend="tests", switch=False)
    temp_projects.select("foo")
    assert temp_projects.current.name == 'foo'

def test_create_switch_project(temp_projects, augmented_mapping):
    temp_projects.create("foo", backend="tests")
    assert temp_projects.current.name == 'foo'
