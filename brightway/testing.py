# -*- coding: utf-8 -*-
from . import config
from brightway import projects
import wrapt


@wrapt.decorator
def bwtest(wrapped, instance, args, kwargs):
    config['test'] = True
    projects.use_temp_directory()
    return wrapped(*args, **kwargs)
