# -*- coding: utf-8 -*-
import hashlib
import os
import re
import appdirs
import unicodedata
import warnings

re_slugify = re.compile('[^\w\s-]', re.UNICODE)

BASE_DIR = appdirs.user_data_dir("brightway", "bw")
BASE_LOG_DIR = appdirs.user_log_dir("brightway", "bw")


def safe_filename(string, add_hash=True):
    """Convert arbitrary strings to make them safe for filenames. Substitutes strange characters, and uses unicode normalization.

    if `add_hash`, appends hash of `string` to avoid name collisions.

    From http://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename-in-python"""
    safe = re.sub(
        '[-\s]+',
        '-',
        str(
            re_slugify.sub(
                '',
                unicodedata.normalize('NFKD', str(string))
            ).strip()
        )
    )
    if add_hash:
        if isinstance(string, str):
            string = string.encode("utf8")
        return safe + u"." + hashlib.md5(string).hexdigest()
    else:
        return safe


def create_dir(dirpath):
    """Create directory tree to ``dirpath``; ignore if already exists."""
    if not os.path.isdir(dirpath):
        os.makedirs(dirpath)


def check_dir(directory):
    """Returns ``True`` if given path is a directory and writeable, ``False`` otherwise."""
    return os.path.isdir(directory) and os.access(directory, os.W_OK)


def create_base_project_dir():
    """Create directory for storing data on projects.

    Most projects will be subdirectories.

    Returns a directory path."""
    if os.path.isdir(BASE_DIR):
        if os.access(BASE_DIR, os.W_OK):
            return BASE_DIR
        else:
            WARNING = ("Brightway directory exists, but is read-only. "
                        "Please fix this and restart.")
            warnings.warn(WARNING)
    else:
        os.makedirs(BASE_DIR)
        return BASE_DIR


def create_project_dir(name):
    """Create subdirectory for project ``name``.

    Returns a directory path."""
    dirpath = os.path.join(BASE_DIR, safe_filename(name))
    create_dir(dirpath)
    return dirpath


def get_dir_size(dirpath):
    """Modified from http://stackoverflow.com/questions/12480367/how-to-generate-directory-size-recursively-in-python-like-du-does.

    Does not follow symbolic links"""
    return sum(
        sum(os.path.getsize(os.path.join(root, name))
        for name in files
    ) for root, dirs, files in os.walk(dirpath)) / 1e9
