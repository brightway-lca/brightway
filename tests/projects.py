# -*- coding: utf-8 -*-
from brightway_projects import projects, Project, backend_mapping
from brightway_projects.testing import bwtest
import os
import platform
import pytest


windows = platform.system() == "Windows"


def test_setup(bwtest):
    assert not projects.current
    projects.create(name="foo", backends=['tests'])
    p = Project.get(name='foo')
    assert not p.data
    assert "projects.test.db" in os.listdir(bwtest)
    assert "__logs__" in os.listdir(bwtest)

def test_select_project(bwtest):
    backend = backend_mapping['tests']
    projects.create("foo", backends=["tests"], switch=False)
    assert backend.created.name == 'foo'
    assert not backend.activated
    projects.select("foo")
    assert backend.activated.name == 'foo'
    assert projects.current.name == 'foo'

def test_create_and_switch_project(bwtest):
    backend = backend_mapping['tests']
    assert not backend.activated
    projects.create("foo", backends=["tests"])
    assert backend.activated.name == 'foo'
    assert backend.created.name == 'foo'
    assert projects.current.name == 'foo'

def test_create_project_creates_dir(bwtest):
    projects.create("foo", backends=["tests"])
    assert os.path.isdir(projects.dir)

@pytest.mark.skipif(windows, reason="Windows hates fun")
def test_really_funny_project_names(bwtest):
    NAMES = [
        "Roses are [0;31mred[0m, violets are [0;34mblue. Hope you enjoy terminal hue",
        "👾 🙇 💁 🙅 🙆 🙋 🙎 🙍 ",
    ]
    error_found = False
    for name in NAMES:
        try:
            projects.create(name, backends=["tests"])
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
        projects.create(name, backends=["tests"])
        assert os.path.isdir(projects.dir)

def test_project_report(bwtest):
    projects.create("foo", backends=["tests"])
    assert projects.report()
