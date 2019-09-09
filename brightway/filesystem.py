# -*- coding: utf-8 -*-
from pathlib import Path
import hashlib
import os
import re
import appdirs
import unicodedata
import warnings

re_slugify = re.compile('[^\w\s-]', re.UNICODE)


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
    dirpath.mkdir(parents=True, exist_ok=True)


def get_dir_size(dirpath):
    """Modified from http://stackoverflow.com/questions/12480367/how-to-generate-directory-size-recursively-in-python-like-du-does.

    Does not follow symbolic links"""
    return sum(
        sum(os.path.getsize(os.path.join(root, name))
        for name in files
    ) for root, dirs, files in os.walk(dirpath)) / 1e9
