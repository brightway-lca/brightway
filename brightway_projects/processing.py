from .errors import InvalidName
from .filesystem import md5, safe_filename
from pathlib import Path
import datetime
import itertools
import json
import numpy as np
import re
import tempfile
import uuid
import zipfile

# Max signed 32 bit integer, compatible with Windows
MAX_SIGNED_32BIT_INT = 2147483647
COMMON_DTYPE = [
    ("row_value", np.uint32),
    ("col_value", np.uint32),
    ("row_index", np.uint32),
    ("col_index", np.uint32),
    ("uncertainty_type", np.uint8),
    ("amount", np.float32),
    ("loc", np.float32),
    ("scale", np.float32),
    ("shape", np.float32),
    ("minimum", np.float32),
    ("maximum", np.float32),
    ("negative", np.bool),
    ("flip", np.bool),
]
NAME_RE = re.compile(r"^[\w\-\.]*$")


def chunked(iterable, chunk_size):
    # Black magic, see https://stackoverflow.com/a/31185097
    # and https://docs.python.org/3/library/functions.html#iter
    iterable = iter(iterable)  # Fix e.g. range from restarting
    return iter(lambda: list(itertools.islice(iterable, chunk_size)), [])


def dictionary_formatter(row):
    """Format processed array row from dictionary input"""
    return (
        row['row'],
        # 1-d matrix
        row.get('col', row['row']),
        MAX_SIGNED_32BIT_INT,
        MAX_SIGNED_32BIT_INT,
        row.get("uncertainty_type", 0),
        row['amount'],
        row.get('loc', row['amount']),
        row.get('scale', np.NaN),
        row.get('shape', np.NaN),
        row.get('minimum', np.NaN),
        row.get('maximum', np.NaN),
        row.get("negative", False),
        row.get("flip", False)
    )


def create_numpy_structured_array(iterable, filepath, nrows=None, format_function=None):
    """"""
    if format_function is None:
        format_function = lambda x, y: x

    if nrows:
        array = np.zeros(nrows, dtype=COMMON_DTYPE)
        for i, row in enumerate(iterable):
            if i > (nrows - 1):
                raise ValueError("More rows than `nrows`")
            array[i] = format_function(row, COMMON_DTYPE)
    else:
        arrays, BUCKET = [], 25000
        array = np.zeros(BUCKET, dtype=COMMON_DTYPE)
        for chunk in chunked(iterable, BUCKET):
            for i, row in enumerate(chunk):
                array[i] = format_function(row, COMMON_DTYPE)
            if i < BUCKET - 1:
                array = array[: i + 1]
                arrays.append(array)
            else:
                arrays.append(array)
                array = np.zeros(BUCKET, dtype=COMMON_DTYPE)
        array = np.hstack(arrays)

    array.sort(order=("row_value", "col_value", "uncertainty_type", "amount"))
    if filepath:
        np.save(filepath, array, allow_pickle=False)
        return filepath
    else:
        return array


def create_datapackage_metadata(name, resources, id_=None, metadata=None):
    """Format metadata for a processed array datapackage.

    All metadata elements should follow the `datapackage specification <https://frictionlessdata.io/specs/data-package/>`__.

    Licenses are specified as a list in ``metadata``. The default license is the `Open Data Commons Public Domain Dedication and License v1.0 <http://opendatacommons.org/licenses/pddl/>`__.

    Args:
        name (str): Name of this data package
        resources (iterable): List of resources following requirements in ``format_datapackage_resource``
        id_ (str, optional): Unique ID of this data package
        metadata (dict, optional): Additional metadata, such as the licenses for this package

    Returns:
        A dictionary ready for writing to a ``datapackage.json`` file.

    TODO: Write validation tests for all metadata elements.

    """
    DEFAULT_LICENSES = [
        {
            "name": "ODC-PDDL-1.0",
            "path": "http://opendatacommons.org/licenses/pddl/",
            "title": "Open Data Commons Public Domain Dedication and License v1.0",
        }
    ]

    if not NAME_RE.match(name):
        raise InvalidName(
            "Provided name violates datapackage spec (https://frictionlessdata.io/specs/data-package/)"
        )

    if metadata is None:
        metadata = {}

    return {
        "profile": "data-package",
        "name": name,
        "id": id_ or uuid.uuid4().hex,
        "licenses": metadata.get("licenses", DEFAULT_LICENSES),
        "resources": [format_datapackage_resource(obj) for obj in resources],
        "created": datetime.datetime.utcnow().isoformat("T") + "Z",
    }


def format_datapackage_resource(res):
    """Format metadata for a `datapackage resource <https://frictionlessdata.io/specs/data-resource/>`__.

    ``res`` should be a dictionary with the following keys:

        name (str): Simple name or identifier to be used for this matrix data
        filename (str): Filename for saved Numpy array
        matrix (str): The name of the matrix to build. See the documentation for ``bw_calc`` for more details.
        dirpath (pathlib.Path): The directory where the datapackage and resource files are saved.

    ``res`` can also have `optional keys <https://frictionlessdata.io/specs/data-resource/>`__ like ``description``, and ``title``.

    Returns:
        A dictionary ready for JSON serialization in the datapackage format.

    TODO: Think about declaring a custom JSON schema for our datapackages, see:

        * https://frictionlessdata.io/specs/profiles/
        * https://frictionlessdata.io/schemas/data-resource.json
        * https://json-schema.org/

    """
    SKIP = {"dirpath", "filename", "data", "nrows", "format_function"}
    obj = {
        # Datapackage generic
        "format": "npy",
        "mediatype": "application/octet-stream",
        "path": res["filename"],
        "name": res["name"],
        "profile": "data-resource",
        # Brightway specific
        "matrix": res["matrix"],
    }
    # Not needed if in-memory
    if res.get("dirpath"):
        obj["md5"] = md5(res["dirpath"] / res["filename"])
    for key, value in res.items():
        if key not in obj and key not in SKIP:
            obj[key] = value
    return obj


def create_calculation_package(
    directory, name, resources, id_=None, metadata=None, replace=True, compress=True, in_memory=False
):
    """Create a calculation package for use in ``brightway_calc``.

    The ``format_function`` should return a tuple of data that fits the structured array datatype, i.e.

        ("row_value", np.uint32),
        ("col_value", np.uint32),
        ("row_index", np.uint32),
        ("col_index", np.uint32),
        ("uncertainty_type", np.uint8),
        ("amount", np.float32),
        ("loc", np.float32),
        ("scale", np.float32),
        ("shape", np.float32),
        ("minimum", np.float32),
        ("maximum", np.float32),
        ("negative", np.bool),
        ("flip", np.bool),

    Args:
        name (str): Name of this calculation package
        resources (iterable): Resources is an iterable of dictionaries with the keys:
            name (str): Simple name or identifier to be used for this matrix data
            matrix (str): The name of the matrix to build. See the documentation for ``bw_calc`` for more details.
            data (iterable): The numerical data to be stored
            nrows (int, optional):  The number of rows in ``array``. Will be counted if not provided, but with an efficiency penalty.
            format_function (callable, optional): Function that formats data to structured array columns.
        id_ (str, optional): Unique ID of this calculation package
        metadata (dict, optional): Additional metadata such as licenses, RNG seeds, etc.
        repalce (bool, optional): Replace an existing calculation package with the same name

    Returns:
        Absolute filepath to calculation package (zip file)

    """
    assert not (in_memory and compress), "In-memory zipfile creation not currently supported (see https://github.com/brightway-lca/brightway_calc/issues/1)"

    if in_memory:
        result, directory = {}, None
    else:
        directory = Path(directory)
        assert directory.is_dir()

    if compress:
        archive = directory / (safe_filename(name) + ".zip")
        if archive.is_file():
            if replace:
                archive.unlink()
            else:
                raise ValueError("This calculation package already exists")

        base_td = tempfile.TemporaryDirectory()
        td = Path(base_td.name)
    else:
        td = directory

    for resource in resources:
        filename = uuid.uuid4().hex + ".npy"
        array = create_numpy_structured_array(
            iterable=resource["data"],
            filepath=td / filename if td else None,
            nrows=resource.get("nrows"),
            format_function=resource.get("format_function"),
        )
        resource["dirpath"] = td
        resource["filename"] = filename
        if in_memory:
            result[filename] = array

    datapackage = create_datapackage_metadata(
        name=name, resources=resources, id_=id_, metadata=metadata
    )
    if in_memory:
        result['datapackage'] = datapackage
    else:
        with open(td / "datapackage.json", "w", encoding="utf-8") as f:
            json.dump(datapackage, f, indent=2, ensure_ascii=False)

    if compress:
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for file in td.iterdir():
                if file.is_file():
                    zf.write(file, arcname=file.name)
        del base_td
        return archive
    elif in_memory:
        return result
    else:
        return directory
