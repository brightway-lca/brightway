from bw_projects.peewee import (
    JSONField,
    PathField,
    SubstitutableDatabase,
    TupleField,
)
from peewee import Model
from pathlib import Path
import os
import pytest
import tempfile


def test_peewee_custom_fields():
    class Table(Model):
        jf = JSONField()
        pf = PathField()
        tf = TupleField()

    SubstitutableDatabase(tables=[Table])
    Table.create(jf={"some data": 42}, tf=[1, 2, 3], pf=os.getcwd())
    o = Table.get()
    assert isinstance(o.pf, Path)
    assert o.tf == (1, 2, 3)
    assert o.jf == {"some data": 42}


def test_tuplefield_error():
    class Table(Model):
        tf = TupleField()

    SubstitutableDatabase(tables=[Table])
    with pytest.raises(ValueError):
        Table.create(tf=42)


def test_sd_db_attributes():
    class Table(Model):
        jf = JSONField()

    db = SubstitutableDatabase(tables=[Table])
    assert db.execute_sql("select 1 + 1")


def test_sd_vacuum():
    class Table(Model):
        jf = JSONField()

    db = SubstitutableDatabase(tables=[Table])
    Table.create(jf="late night coding")
    db._vacuum()
