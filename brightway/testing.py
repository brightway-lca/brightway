# -*- coding: utf-8 -*-
from . import projects, project_database, backend_mapping
from pathlib import Path
import pytest


class FakeBackend:
    __brightway_common_api__ = True

    def activate_project(self, name):
        pass

    def deactivate_project(self):
        pass

    def create_project(self, name):
        pass

    def copy_project(self, name):
        pass

    def delete_project(self, name):
        pass

    def export_project(self, name):
        pass

    def import_project(self, name):
        pass


@pytest.fixture
def bwtest(monkeypatch, tmp_path):
    project_database._change_path(tmp_path / "projects.test.db")
    ld = tmp_path / "__logs__"
    ld.mkdir()
    monkeypatch.setattr(projects, "base_dir", tmp_path)
    monkeypatch.setattr(projects, "base_log_dir", ld)
    monkeypatch.setitem(backend_mapping, "tests", FakeBackend())
    return tmp_path


