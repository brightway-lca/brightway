from brightway_projects.errors import InvalidName
from brightway_projects.testing import bwtest
from brightway_projects.processing import (
    chunked,
    COMMON_DTYPE,
    create_calculation_package,
    create_datapackage_metadata,
    create_numpy_structured_array,
    format_datapackage_resource,
    NAME_RE,
)
from pathlib import Path
import numpy as np
import pytest
import tempfile


fixtures_dir = Path(__file__, "..").resolve() / "fixtures"


def test_chunked():
    c = chunked(range(600), 250)
    for x in next(c):
        pass
    assert x == 249
    for x in next(c):
        pass
    assert x == 499
    for x in next(c):
        pass
    assert x == 599


def test_create_array():
    with tempfile.TemporaryDirectory() as td:
        fp = Path(td) / "array.npy"
        data = [
            tuple(list(range(11)) + [False, False]),
            tuple(list(range(12, 23)) + [True, True]),
        ]
        create_numpy_structured_array(data, fp)
        result = np.load(fp)
        assert result.shape == (2,)
        assert result.dtype == COMMON_DTYPE
        assert np.allclose(result["row_value"], [0, 12])
        assert np.allclose(result["flip"], [False, True])


def test_create_array_format_function():
    def func(x, dtype):
        return (2, 4, 1, 3, 5, 7, 6, 8, 9, 11, 10, False, True)

    with tempfile.TemporaryDirectory() as td:
        fp = Path(td) / "array.npy"
        create_numpy_structured_array(range(10), fp, format_function=func)
        result = np.load(fp)
        assert result.shape == (10,)
        assert result.dtype == COMMON_DTYPE
        assert result["row_value"].sum() == 20


def test_create_array_specify_nrows():
    with tempfile.TemporaryDirectory() as td:
        fp = Path(td) / "array.npy"
        data = [tuple(list(range(11)) + [False, False])] * 200
        create_numpy_structured_array(data, fp, nrows=200)
        result = np.load(fp)
        assert result.shape == (200,)
        assert result["row_value"].sum() == 0


def test_create_array_specify_nrows_too_many():
    with tempfile.TemporaryDirectory() as td:
        fp = Path(td) / "array.npy"
        data = [tuple(list(range(11)) + [False, False])] * 200
        with pytest.raises(ValueError):
            create_numpy_structured_array(data, fp, nrows=100)


def test_create_array_chunk_data():
    with tempfile.TemporaryDirectory() as td:
        fp = Path(td) / "array.npy"
        data = [tuple(list(range(11)) + [False, False])] * 90000
        create_numpy_structured_array(data, fp)
        result = np.load(fp)
        assert result.shape == (90000,)
        assert result["row_value"].sum() == 0


def test_format_datapackage_metadata():
    expected = {"profile": "data-package", "name": "a", "id": "b", "licenses": "c"}
    result = create_datapackage_metadata("a", [], id_="b", metadata={"licenses": "c"})
    assert result["created"]
    for k, v in expected.items():
        assert result[k] == v


def test_name_re():
    assert NAME_RE.match("hey_you")
    assert not NAME_RE.match("hey_you!")


def test_format_datapackage_metadata_no_id():
    result = create_datapackage_metadata("a", [])
    assert result["id"]
    assert len(result["id"]) > 16


def test_format_datapackage_metadata_default_licenses():
    result = create_datapackage_metadata("a", [])
    assert result["licenses"] == [
        {
            "name": "ODC-PDDL-1.0",
            "path": "http://opendatacommons.org/licenses/pddl/",
            "title": "Open Data Commons Public Domain Dedication and License v1.0",
        }
    ]


def test_format_datapackage_metadata_invalid_name():
    with pytest.raises(InvalidName):
        create_datapackage_metadata("woo!", {})


def test_format_datapackage_resource():
    given = {
        "dirpath": fixtures_dir,
        "filename": "basic_array.npy",
        "name": "test-name",
        "matrix": "technosphere",
        "description": "some words",
        "foo": "bar",
    }
    expected = {
        "format": "npy",
        "mediatype": "application/octet-stream",
        "path": "basic_array.npy",
        "name": "test-name",
        "md5": "45aebe85c3a7b11d0427a98c07a4b90d",
        "profile": "data-resource",
        "matrix": "technosphere",
        "description": "some words",
        "foo": "bar",
    }
    assert format_datapackage_resource(given) == expected


def test_calculation_package():
    resources = [{
        'name': 'first-resource',
        'matrix': 'technosphere',
        'data': [
            tuple(list(range(11)) + [False, False]),
            tuple(list(range(12, 23)) + [True, True]),
        ],
    }]
    with tempfile.TemporaryDirectory() as td:
        fp = create_calculation_package(td, "test-package", resources)
        # Test data in fp


def test_calculation_package_name_conflict():
    pass


def test_calculation_package_specify_id():
    pass


def test_calculation_package_metadata():
    pass
