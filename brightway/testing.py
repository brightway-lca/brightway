# -*- coding: utf-8 -*-
from . import projects, project_database
from pathlib import Path
import pytest


@pytest.fixture
def bwtest(monkeypatch, tmp_path):
    project_database._change_path(tmp_path / "projects.test.db")
    bd = lambda : tmp_path
    ld = lambda : tmp_path / "__logs__"
    ld().mkdir()
    monkeypatch.setattr(projects, "base_dir", bd)
    monkeypatch.setattr(projects, "base_log_dir", ld)
    return tmp_path
