# -*- coding: utf-8 -*-
from . import projects, project_database, backend_mapping
from pathlib import Path
import pytest


class FakeBackend:
    __brightway_common_api__ = True
    activated = deactivated = created = copied = None
    deleted = exported = imported = None

    def activate_project(self, obj):
        self.activated = name

    def deactivate_project(self, obj):
        self.deactivated = name

    def create_project(self, obj):
        self.created = name

    def copy_project(self, old, new_name):
        self.copied = name

    def delete_project(self, obj):
        self.deleted = name

    def export_project(self, obj, filepath):
        self.exported = name

    def import_project(self, obj, filepath):
        self.imported = name


@pytest.fixture
def bwtest(monkeypatch, tmp_path):
    project_database._change_path(tmp_path / "projects.test.db")
    ld = tmp_path / "__logs__"
    ld.mkdir()
    monkeypatch.setattr(projects, "base_dir", tmp_path)
    monkeypatch.setattr(projects, "base_log_dir", ld)
    monkeypatch.setitem(backend_mapping, "tests", FakeBackend())
    return tmp_path


