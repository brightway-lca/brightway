from ..errors import InvalidName
import datetime
import itertools
import numpy as np
import re
import uuid


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
        row["row"],
        # 1-d matrix
        row.get("col", row["row"]),
        MAX_SIGNED_32BIT_INT,
        MAX_SIGNED_32BIT_INT,
        row.get("uncertainty_type", 0),
        row["amount"],
        row.get("loc", row["amount"]),
        row.get("scale", np.NaN),
        row.get("shape", np.NaN),
        row.get("minimum", np.NaN),
        row.get("maximum", np.NaN),
        row.get("negative", False),
        row.get("flip", False),
    )


def create_numpy_structured_array(
    iterable, filepath=None, nrows=None, format_function=None
):
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


def create_datapackage_metadata(
    name, resources, resource_function, id_=None, metadata=None
):
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
        "resources": [resource_function(obj) for obj in resources],
        "created": datetime.datetime.utcnow().isoformat("T") + "Z",
    }
