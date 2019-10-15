from ..filesystem import md5, safe_filename
from .utils import create_datapackage_metadata, create_numpy_structured_array
from pathlib import Path
import json
import tempfile
import uuid
import zipfile


def format_calculation_resource(res):
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
        name=name, resources=resources, resource_function=format_calculation_resource, id_=id_, metadata=metadata
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
