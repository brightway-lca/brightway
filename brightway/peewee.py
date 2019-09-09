# -*- coding: utf-8 -*-
from peewee import SqliteDatabase, Model, TextField
import os
import json
from pathlib import Path


abspath = lambda x: str(x.absolute()) if isinstance(x, Path) else x


class JSONField(TextField):
    def db_value(self, value):
        return super(JSONField, self).db_value(
            json.dumps(value)
        )

    def python_value(self, value):
        return json.loads(value)


class SubstitutableDatabase(object):
    def __init__(self, filepath, tables=[]):
        self._tables = tables
        if filepath is not None:
            self._create_database(filepath)

    def _create_database(self, filepath):
        self._db = SqliteDatabase(abspath(filepath))
        for model in self._tables:
            model.bind(self._db, bind_refs=False, bind_backrefs=False)
        self._db.connect()
        self._db.create_tables(self._tables)

    def _change_path(self, filepath):
        self.close()
        self._create_database(filepath)

    def _add_table(self, model):
        self._tables.append(model)

    def _vacuum(self):
        print("Vacuuming database ")
        self.execute_sql('VACUUM;')

    def __getattr__(self, attr):
        return getattr(self._db, attr)
