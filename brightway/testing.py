# -*- coding: utf-8 -*-
from . import projects, project_database, backend_mapping
from pathlib import Path
import pytest


class FakeBackend:
    __brightway_common_api__ = True
    activated = deactivated = created = copied = None
    deleted = exported = imported = None

    def activate_project(self, obj):
        self.activated = obj

    def deactivate_project(self, obj):
        self.deactivated = obj

    def create_project(self, obj):
        self.created = obj

    def copy_project(self, old, new):
        self.copied_old = old
        self.copied_new = new

    def delete_project(self, obj):
        self.deleted = obj

    def export_project(self, obj, filepath):
        self.exported = obj
        self.exported_filepath = filepath

    def import_project(self, obj, filepath):
        self.imported = obj
        self.imported_filepath = filepath


@pytest.fixture
def bwtest(monkeypatch, tmp_path):
    project_database._change_path(tmp_path / "projects.test.db")
    ld = tmp_path / "__logs__"
    ld.mkdir()
    monkeypatch.setattr(projects, "base_dir", tmp_path)
    monkeypatch.setattr(projects, "base_log_dir", ld)
    monkeypatch.setitem(backend_mapping, "tests", FakeBackend())
    return tmp_path


