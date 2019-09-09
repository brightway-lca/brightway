from brightway import bwtest, projects


def test_testing_fixture(bwtest):
    assert projects.base_dir
