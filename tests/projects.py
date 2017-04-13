# -*- coding: utf-8 -*-
from . import temp_projects
from brightway import backend_mapping
from brightway.projects import Project
import os
import platform

windows = platform.system() == "Windows"


def test_setup(temp_projects):
    assert not temp_projects.current
    temp_projects.create("foo", backend="tests")
    assert 'tests' in backend_mapping
    p = Project.get(name='foo')
    assert not p.data
    assert p.backend == 'tests'
    assert "projects.db" in os.listdir(temp_projects.base_dir)

def test_create_project(temp_projects):
    temp_projects.create("foo", backend="tests", switch=False)

def test_select_project(temp_projects):
    temp_projects.create("foo", backend="tests", switch=False)
    temp_projects.select("foo")
    assert temp_projects.current.name == 'foo'

def test_create_switch_project(temp_projects):
    temp_projects.create("foo", backend="tests")
    assert temp_projects.current.name == 'foo'

def test_create_project(temp_projects):
    temp_projects.create("foo", backend="tests")
    assert os.path.isdir(temp_projects.dir)

@pytest.mark.skipif(windows, reason="Windows hates fun")
def test_really_funny_project_names(temp_projects):
    NAMES = [
        "Roses are [0;31mred[0m, violets are [0;34mblue. Hope you enjoy terminal hue",
        "👾 🙇 💁 🙅 🙆 🙋 🙎 🙍 ",
    ]
    error_found = False
    for name in NAMES:
        try:
            temp_projects.create(name, backend="tests")
            assert os.path.isdir(projects.dir)
            print("This is OK:", name)
        except:
            print("This is not OK:", name)
            error_found = True
    if error_found:
        raise ValueError("Invaid project name")

def test_funny_project_names(temp_projects):
    NAMES = [
        "Powerلُلُصّبُلُلصّبُررً ॣ ॣh ॣ ॣ冗",
        "True",
        "None",
        "1.0/0.0",
        "0xabad1dea",
        "!@#$%^&*()`~",
        "<>?:'{}|_+",
        ",./;'[]\-=",
        "Ω≈ç√∫˜µ≤≥÷",
        "田中さんにあげて下さい",
        "｀ｨ(´∀｀∩",
        "הָיְתָהtestالصفحات التّحول",
        "　",
    ]
    for name in NAMES:
        temp_projects.create(name, backend="tests")
        assert os.path.isdir(projects.dir)

def test_create_project(temp_projects):
    temp_projects.create("foo", backend="tests")
    assert projects.report
