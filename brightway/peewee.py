# -*- coding: utf-8 -*-
from peewee import SqliteDatabase, Model, TextField
from playhouse.shortcuts import RetryOperationalError
import os
import json


class JSONField(TextField):
    def db_value(self, value):
        return super(JSONField, self).db_value(
            json.dumps(value)
        )

    def python_value(self, value):
        return json.loads(value)


class RetryDatabase(RetryOperationalError, SqliteDatabase):
    pass
