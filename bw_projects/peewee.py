from collections.abc import Iterable
from pathlib import Path
from peewee import SqliteDatabase, TextField, BlobField
import json


abspath = lambda x: str(x.absolute()) if isinstance(x, Path) else x


class JSONField(TextField):
    def db_value(self, value):
        return super().db_value(json.dumps(value))

    def python_value(self, value):
        return json.loads(value)


class PathField(TextField):
    def db_value(self, value):
        return super().db_value(abspath(value))

    def python_value(self, value):
        return Path(value)


class TupleField(BlobField):
    def db_value(self, value):
        if not isinstance(value, Iterable):
            raise ValueError("{} is not an iterable".format(value))
        return super().db_value(json.dumps(tuple(value), ensure_ascii=False))

    def python_value(self, value):
        return tuple(json.loads(value))


class SubstitutableDatabase(object):
    def __init__(self, filepath=":memory:", tables=[]):
        self._tables = tables
        self._create_database(filepath)

    def _create_database(self, filepath):
        self._db = SqliteDatabase(
            abspath(filepath) if filepath != ":memory:" else filepath,
            pragmas={"foreign_keys": 1},
        )
        for model in self._tables:
            model.bind(self._db, bind_refs=False, bind_backrefs=False)
        self._db.connect()
        self._db.create_tables(self._tables, safe=True)

    def _change_path(self, filepath):
        self.close()
        self._create_database(filepath)

    def _vacuum(self):
        print("Vacuuming database ")
        self.execute_sql("VACUUM;")

    def __getattr__(self, attr):
        return getattr(self._db, attr)
