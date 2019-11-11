# -*- coding: utf-8 -*-
from pathlib import Path
import os
import appdirs


def get_base_directories():
    envvar = os.getenv("BRIGHTWAY_DIR")
    if envvar:
        envvar = Path(envvar).resolve()
        if not envvar.is_dir():
            raise OSError(
                (
                    "BRIGHTWAY_DIR variable is {}, but this is not" " a valid directory"
                ).format(envvar)
            )
        else:
            print(
                "Using environment variable BRIGHTWAY_DIR for data "
                "directory:\n{}".format(envvar)
            )
            logs_dir = envvar / "logs"
            logs_dir.mkdir(exist_ok=True)
            return envvar, logs_dir

    return (
        Path(appdirs.user_data_dir("brightway", "bw", version="3")),
        Path(appdirs.user_log_dir("brightway", "bw", version="3")),
    )
