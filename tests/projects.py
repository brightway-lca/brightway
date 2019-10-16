# -*- coding: utf-8 -*-
from brightway_projects import projects, Project, backend_mapping
from brightway_projects.projects import ProjectManager
from brightway_projects.errors import MissingBackend
from brightway_projects.testing import bwtest
import os
import platform
import pytest
import tempfile


windows = platform.system() == "Windows"

# Project class


def test_project_model_create(bwtest):
    with tempfile.TemporaryDirectory() as td:
        Project.create(name="foo", directory=td)


def test_project_model_comparison(bwtest):
    with tempfile.TemporaryDirectory() as td:
        p1 = Project.create(name="foo", directory=td)
        p2 = Project.create(name="bar", directory=td)
        assert p2 < p1

    with pytest.raises(TypeError):
        p1 < 42


def test_project_model_str_repr(bwtest):
    with tempfile.TemporaryDirectory() as td:
        p = Project.create(name="foo", directory=td)
        assert str(p)
        assert repr(p)


def test_project_model_ordering(bwtest):
    with tempfile.TemporaryDirectory() as td:
        p1 = Project.create(name="foo", directory=td)
        p2 = Project.create(name="bar", directory=td)
        assert sorted([p1, p2])
        assert p2 < p1

    with pytest.raises(TypeError):
        p2 > 7


# projects manager

## basic setup


def test_setup(bwtest):
    assert not projects.current
    assert not projects.dir
    projects.create_project(name="foo", backends=["tests"])
    assert os.path.isdir(projects.base_dir)
    assert os.path.isdir(projects.base_log_dir)
    p = Project.get(name="foo")
    assert not p.data
    assert "projects.test.db" in os.listdir(bwtest)
    assert "__logs__" in os.listdir(bwtest)


def test_setup_default_project(bwtest):
    assert not projects.dir
    assert not projects.current
    projects.create_project(name="foo", backends=["tests"], default=True)
    p2 = ProjectManager(projects.base_dir, projects.base_log_dir)
    assert p2.current


## magic methods


def test_projects_iteration(bwtest):
    projects.create_project(name="foo", backends=["tests"])
    projects.create_project(name="bar", backends=["tests"])
    projects.create_project(name="baz", backends=["tests"])
    count = 0
    for x in projects:
        count += 1
    assert count == 3


def test_projects_iteration_skips_disabled(bwtest):
    projects.create_project(name="foo", backends=["tests"])
    projects.create_project(name="bar", backends=["tests"])
    assert len(projects) == 2
    p = Project.get(name="bar")
    p.enabled = False
    p.save()
    for proj in projects:
        assert proj.name != "bar"


def test_projects_len(bwtest):
    projects.create_project(name="foo", backends=["tests"])
    projects.create_project(name="bar", backends=["tests"])
    assert len(projects) == 2
    projects.create_project(name="baz", backends=["tests"])
    assert len(projects) == 3


def test_projects_len_skips_disabled(bwtest):
    projects.create_project(name="foo", backends=["tests"])
    projects.create_project(name="bar", backends=["tests"])
    assert len(projects) == 2
    projects.create_project(name="baz", backends=["tests"])
    assert len(projects) == 3
    p = Project.get(name="bar")
    p.enabled = False
    p.save()
    assert len(projects) == 2


def test_representation(bwtest):
    assert repr(projects)
    assert str(projects)
    projects.create_project(name="foo", backends=["tests"])
    assert repr(projects)
    assert str(projects)
    for x in range(25):
        projects.create_project(name=f"project-{x}", backends=["tests"])
    assert repr(projects)
    assert str(projects)


def test_contains(bwtest):
    assert "foo" not in projects
    projects.create_project(name="foo", backends=["tests"])
    assert "foo" in projects


# .dir


def test_dot_dir(bwtest):
    assert not projects.dir
    projects.create_project(name="foo", backends=["tests"])
    assert projects.dir == projects.current.directory
    assert projects.dir.is_dir()


# .select


def test_select_project(bwtest):
    backend = backend_mapping["tests"]
    projects.create_project("foo", backends=["tests"], switch=False)
    assert backend.created.name == "foo"
    assert not backend.activated
    projects.select("foo")
    assert backend.activated.name == "foo"
    assert projects.current.name == "foo"


# .activate, .deactivate


def test_activate_deactivate(bwtest):
    backend = backend_mapping["tests"]
    projects.create_project("foo", backends=["tests"])
    projects.deactivate()
    assert not backend.activated
    assert projects.current is None
    projects.current = Project.get(name="foo")
    assert not backend.activated
    projects.activate()
    assert backend.activated


# .create_project


def test_create_and_switch_project(bwtest):
    backend = backend_mapping["tests"]
    assert not backend.activated
    projects.create_project("foo", backends=["tests"])
    assert backend.activated.name == "foo"
    assert backend.created.name == "foo"
    assert projects.current.name == "foo"


def test_create_project_creates_dir(bwtest):
    projects.create_project("foo", backends=["tests"])
    assert projects.dir.is_dir()


def test_create_project_already_exists(bwtest):
    projects.create_project("foo", backends=["tests"])
    assert projects.create_project("foo", backends=["tests"]) is None


@pytest.mark.skipif(windows, reason="Windows hates fun")
def test_really_funny_project_names(bwtest):
    NAMES = [
        "Roses are [0;31mred[0m, violets are [0;34mblue. Hope you enjoy terminal hue",
        "👾 🙇 💁 🙅 🙆 🙋 🙎 🙍 ",
    ]
    error_found = False
    for name in NAMES:
        try:
            projects.create_project(name, backends=["tests"])
            assert os.path.isdir(projects.dir)
            print("This is OK:", name)
        except:
            print("This is not OK:", name)
            error_found = True
    if error_found:
        raise ValueError("Invaid project name")


def test_funny_project_names(bwtest):
    NAMES = [
        "Powerلُلُصّبُلُلصّبُررً ॣ ॣh ॣ ॣ冗",
        "True",
        "None",
        "1.0/0.0",
        "0xabad1dea",
        "!@#$%^&*()`~",
        "<>?:'{}|_+",
        r",./;'[]\-=",
        "Ω≈ç√∫˜µ≤≥÷",
        "田中さんにあげて下さい",
        "｀ｨ(´∀｀∩",
        "הָיְתָהtestالصفحات التّحول",
        "　",
    ]
    for name in NAMES:
        projects.create_project(name, backends=["tests"])
        assert os.path.isdir(projects.dir)


# .delete_project


def test_delete_project_and_deactivate(bwtest):
    projects.create_project("foo", backends=["tests"])
    assert projects.dir.is_dir()
    assert projects.current
    projects.delete_project(projects.current)
    assert projects.current is None


def test_delete_project_not_current(bwtest):
    projects.create_project("foo", backends=["tests"])
    projects.create_project("bar", backends=["tests"])
    assert projects.dir.is_dir()
    assert projects.current
    projects.delete_project("foo")
    assert projects.current
    assert "foo" not in projects


def test_delete_project_error(bwtest):
    projects.create_project("foo", backends=["tests"])
    with pytest.raises(ValueError):
        projects.delete_project("bar")


def test_delete_project_name_string(bwtest):
    projects.create_project("foo", backends=["tests"])
    assert projects.dir.is_dir()
    assert projects.current
    projects.delete_project("foo")
    assert projects.current is None


# .report


def test_project_report(bwtest):
    projects.create_project("foo", backends=["tests"])
    assert projects.report()
