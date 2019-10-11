from .errors import InvalidName, DuplicateDtypeLabel
from .filesystem import md5
from copy import deepcopy
from pathlib import Path
import datetime
import json
import numpy as np
import os
import re
import shutil
import uuid

# Max signed 32 bit integer, compatible with Windows
MAX_SIGNED_32BIT_INT = 2147483647


def create_numpy_structured_array(
    iterable, nrows, filepath, format_function=None, dtype=None, add_row_col=True
):
    """"""
    BASE_DTYPE = [
        ('row_value', np.uint32),
        ('col_value', np.uint32),
        ('row_index', np.uint32),
        ('col_index', np.uint32),
        ('uncertainty_type', np.uint8),
        ('amount', np.float32),
        ('loc', np.float32),
        ('scale', np.float32),
        ('shape', np.float32),
        ('minimum', np.float32),
        ('maximum', np.float32),
        ('negative', np.bool),
        ('flip', np.bool),
    ]
    if format_function is None:
        format_function = default_formatter
    if dtype is None:
        dtype = BASE_DTYPE
    else:
        dtype = list(dtype)
    if add_row_col:
        if not any(line[0] == "row_index" for line in dtype):
            dtype.append(('row_index', np.uint32))
        if not any(line[0] == "col_index" for line in dtype):
            dtype.append(('col_index', np.uint32))
    dtype.sort()
    array = np.zeros(nrows, dtype=dtype)
    for i, row in enumerate(iterable):
        array[i] = default_formatter(row, dtype)

    np.save(filepath, array, allow_pickle=False)


# def create_presamples_package(matrix_data=None, parameter_data=None, name=None,
#         id_=None, overwrite=False, dirpath=None, seed=None):
#     """Create and populate a new presamples package

#      The presamples package minimally contains a datapackage file with metadata on the
#      datapackage itself and its associated resources (stored presample arrays and
#      identification of what the values in the arrays represent).

#      Parameters
#      ----------
#         matrix_data: list, optional
#             list of tuples containing raw matrix data (presamples array, indices, matrix label)
#         parameter_data: list, optional
#             list of tuples containing raw parameter data (presamples array, names, label)
#         name: str, optional
#             A human-readable name for these samples.
#         \id_: str, optional
#             Unique id for this collection of presamples. Optional, generated automatically if not set.
#         overwrite: bool, default=False
#             If True, replace an existing presamples package with the same ``\id_`` if it exists.
#         dirpath: str, optional
#             An optional directory path where presamples can be created. If None, a subdirectory in the ``project`` folder.
#         seed: {None, int, "sequential"}, optional
#             Seed used by indexer to return array columns in random order. Can be an integer, "sequential" or None.

#     Notes
#     ----
#     Both ``matrix_data`` and ``parameter_data`` are optional, but at least one needs to be passed.
#     The documentation gives more details on these input arguments.

#     Both matrix and parameter data should have the same number of possible values (i.e same number of samples).

#     The documentations provide more information on the format for these two arguments.

#     Returns
#     -------
#     id_: str
#         The unique ``id_`` of the presamples package
#     dirpath: str
#         The absolute path of the created directory.


#     """
#     id_ = id_ or uuid.uuid4().hex
#     name = name or id_

#     if dirpath is not None:
#         assert os.path.isdir(dirpath), "`dirpath` must be a directory"
#         assert os.access(dirpath, os.W_OK), "`dirpath` must be a writable directory"
#         dirpath = os.path.abspath(dirpath)
#     dirpath = get_presample_directory(id_, overwrite, dirpath=dirpath)

#     num_iterations = None
#     datapackage = {
#         "name": str(name),
#         "id": id_,
#         "profile": "data-package",
#         "seed": seed,
#         "resources": []
#     }

#     if not matrix_data and not parameter_data:
#         raise ValueError("Must specify at least one of `matrix_data` and `parameter_data`")

#     def elems(lst, label):
#         """Yield elements from ``lst``. If an element is a model instance, iterate over its components."""
#         for elem in lst:
#             if hasattr(elem, label):
#                 for obj in getattr(elem, label):
#                     yield obj
#             else:
#                 yield elem

#     # Not defined if matrix_data is empty
#     index = -1
#     for index, row in enumerate(elems(matrix_data or [], "matrix_data")):
#         samples, indices, kind, *other = row
#         samples = to_2d(to_array(samples))

#         if num_iterations is None:
#             num_iterations = samples.shape[1]
#         if samples.shape[1] != num_iterations:
#             raise InconsistentSampleNumber("Inconsistent number of samples: "
#                 "{} and {}".format(samples.shape[1], num_iterations))

#         indices, metadata = format_matrix_data(indices, kind, *other)

#         if samples.shape[0] != indices.shape[0]:
#             error = "Shape mismatch between samples and indices: {}, {}, {}"
#             raise ShapeMismatch(error.format(samples.shape, indices.shape, kind))

#         result = write_matrix_data(samples, indices, metadata, kind, dirpath, index, id_)
#         datapackage['resources'].append(result)

#     names = [
#         name for _, names, _ in elems(parameter_data or [], "parameter_data")
#         for name in names
#     ]

#     num_names = len(names)
#     num_unique_names = len(set(names))
#     if num_names != num_unique_names:
#         # Only get names if necessary
#         seen = []
#         dupes = []
#         for name in names:
#             if name not in seen:
#                 seen.append(name)
#             else:
#                 dupes.append(name)
#         raise NameConflicts(
#             "{} named parameters, but only {} unique names. Non-unique names: {}".format(
#             num_names, num_unique_names, dupes
#         ))

#     offset = (index + 1) if index != -1 else 0
#     for index, row in enumerate(elems(parameter_data or [], "parameter_data")):
#         samples, names, label = row

#         samples = to_2d(to_array(samples))
#         if not len(names) == samples.shape[0]:
#             raise ShapeMismatch("Shape mismatch between samples and names: "
#                 "{}, {}".format(samples.shape, len(names)))

#         if num_iterations is None:
#             num_iterations = samples.shape[1]
#         if samples.shape[1] != num_iterations:
#             raise InconsistentSampleNumber("Inconsistent number of samples: "
#                 "{} and {}".format(samples.shape[1], num_iterations))

#         result = write_parameter_data(samples, names, label, dirpath,
#                                             offset + index, id_)
#         datapackage['resources'].append(result)

#     datapackage['ncols'] = num_iterations

#     with open(dirpath / "datapackage.json", "w", encoding='utf-8') as f:
#         json.dump(datapackage, f, indent=2, ensure_ascii=False)

#     return id_, dirpath


def create_datapackage_metadata(name, id_, resources, metadata=None):
    """Format metadata for a processed array datapackage.

    All metadata elements should follow the `datapackage specification <https://frictionlessdata.io/specs/data-package/>`__.

    Licenses are specified as a list in ``metadata``. The default license is the `Open Data Commons Public Domain Dedication and License v1.0 <http://opendatacommons.org/licenses/pddl/>`__.

    Args:
        name (str): Name of this data package
        id_ (str): Unique ID of this data package
        resources (iterable): List of resources following requirements in ``format_datapackage_resource``
        metadata (dict): Additional metadata, such as the licenses for this package

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

    name_re = re.compile("^[\w\-\.]*$")
    if not name_re.match(name):
        raise InvalidName(
            "Provided name violates datapackage spec (https://frictionlessdata.io/specs/data-package/)"
        )

    if metadata is None:
        metadata = {}

    return {
        "profile": "data-package",
        "name": name,
        "id": id_,
        "licenses": metadata.get("licenses", DEFAULT_LICENSES),
        "resources": [format_datapackage_resource(obj) for obj in resources],
        "created": datetime.datetime.utcnow().isoformat("T") + "Z",
    }


def format_datapackage_resource(res):
    """Format metadata for a `datapackage resource <https://frictionlessdata.io/specs/data-resource/>`__.

    ``res`` should be a dictionary with the following keys:

        name (str): Simple name or identifier to be used for this matrix data
        filename (str): Filename for saved Numpy array
        array (numpy.ndarray): The Numpy array to be saved
        matrix (str): The name of the matrix to build. See the documentation for ``bw_calc`` for more details.
        dirpath (pathlib.Path): The directory where the datapackage and resource files will be saved.

    ``res`` can also have the following `optional keys <https://frictionlessdata.io/specs/data-resource/>`__: ``description`` and ``title``.

    Returns:
        A dictionary ready for JSON serialization in the datapackage format.

    TODO: Think about declaring a custom JSON schema for our datapackages, see:

        * https://frictionlessdata.io/specs/profiles/
        * https://frictionlessdata.io/schemas/data-resource.json
        * https://json-schema.org/

    """
    OPTIONAL_KEYS = {"description", "title"}
    obj = {
        # Datapackage generic
        "format": "npy",
        "mediatype": "application/octet-stream",
        "path": res["filename"],
        "name": res["name"],
        "md5": md5(res["dirpath"] / res["filename"]),
        "profile": "data-resource",
        # Brightway specific
        "dtype": str(res["array"].dtype),
        "matrix": res["matrix"],
        "shape": res["array"].shape,
    }
    for key, value in res.items():
        if key in OPTIONAL_KEYS:
            obj[key] = value
    return obj
