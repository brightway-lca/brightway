# -*- coding: utf-8 -*-
from . import projects, project_database, backend_mapping
from pathlib import Path
import pytest
import tempfile


class FakeBackend:
    __brightway_common_api__ = True
    __brightway_common_api_version__ = 1
    activated = created = copied = None
    deleted = exported = imported = None

    def activate_project(self, obj):
        self.activated = obj

    def deactivate_project(self):
        self.activated = None

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
def bwtest(monkeypatch):
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        project_database._change_path(td / "projects.test.db")
        ld = td / "__logs__"
        ld.mkdir()
        monkeypatch.setattr(projects, "base_dir", td)
        monkeypatch.setattr(projects, "base_log_dir", ld)
        monkeypatch.setattr(projects, "current", None)
        monkeypatch.setitem(backend_mapping, "tests", FakeBackend())
        yield td
        for key in list(backend_mapping):
            backend_mapping[key].deactivate_project()
            del backend_mapping[key]
        project_database.close()
