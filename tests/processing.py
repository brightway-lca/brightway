from brightway_projects.testing import bwtest
from brightway_projects.processing import (
    chunked,
    COMMON_DTYPE,
    create_calculation_package,
    create_datapackage_metadata,
    create_numpy_structured_array,
    format_datapackage_resource,
)
from pathlib import Path
import numpy as np
import pytest
import tempfile


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
        assert np.allclose(result['row_value'], [0, 12])
        assert np.allclose(result['flip'], [False, True])


def test_create_array_format_function():
    def func(x, dtype):
        return (2, 4, 1, 3, 5, 7, 6, 8, 9, 11, 10, False, True)

    with tempfile.TemporaryDirectory() as td:
        fp = Path(td) / "array.npy"
        create_numpy_structured_array(range(10), fp, format_function=func)
        result = np.load(fp)
        assert result.shape == (10,)
        assert result.dtype == COMMON_DTYPE
        assert result['row_value'].sum() == 20


def test_create_array_specify_nrows():
    with tempfile.TemporaryDirectory() as td:
        fp = Path(td) / "array.npy"
        data = [
            tuple(list(range(11)) + [False, False]),
        ] * 200
        create_numpy_structured_array(data, fp, nrows=200)
        result = np.load(fp)
        assert result.shape == (200,)
        assert result['row_value'].sum() == 0


def test_create_array_specify_nrows_too_many():
    with tempfile.TemporaryDirectory() as td:
        fp = Path(td) / "array.npy"
        data = [
            tuple(list(range(11)) + [False, False]),
        ] * 200
        with pytest.raises(ValueError):
            create_numpy_structured_array(data, fp, nrows=100)


def test_create_array_chunk_data():
    with tempfile.TemporaryDirectory() as td:
        fp = Path(td) / "array.npy"
        data = [
            tuple(list(range(11)) + [False, False]),
        ] * 90000
        create_numpy_structured_array(data, fp)
        result = np.load(fp)
        assert result.shape == (90000,)
        assert result['row_value'].sum() == 0


# @bw2test
# def test_sqlite_processed_array_order():
#     database = DatabaseChooser("testy")
#     data = {
#         ("testy", "C"): {},
#         ("testy", "A"): {'type': 'biosphere'},
#         ("testy", "B"): {'exchanges': [
#             {'input': ("testy", "A"),
#              'amount': 1,
#              'type': 'technosphere'},
#             {'input': ("testy", "A"),
#              'amount': 2,
#              'type': 'technosphere'},
#             {'input': ("testy", "C"),
#              'amount': 2,
#              'type': 'biosphere'},
#             {'input': ("testy", "C"),
#              'amount': 3,
#              'type': 'biosphere'},
#             {'input': ("testy", "B"),
#              'amount': 4,
#              'type': 'production'},
#             {'input': ("testy", "B"),
#              'amount': 1,
#              'type': 'production'},
#         ]}
#     }
#     database.write(data)
#     lookup = {k: mapping[("testy", k)] for k in "ABC"}
#     expected = sorted([
#         (lookup['A'], lookup['B'], 1),
#         (lookup['A'], lookup['B'], 2),
#         (lookup['B'], lookup['B'], 1),
#         (lookup['B'], lookup['B'], 4),
#         (lookup['C'], lookup['C'], 1),
#         (lookup['C'], lookup['B'], 2),
#         (lookup['C'], lookup['B'], 3),
#     ])
#     array = np.load(database.filepath_processed())
#     assert array.shape == (7,)
#     result = [(array['input'][x], array['output'][x], array['amount'][x])
#             for x in range(7)]
#     assert expected == result

# @bw2test
# def test_singlefile_processed_array_order():
#     database = DatabaseChooser("testy", "singlefile")
#     data = {
#         ("testy", "C"): {},
#         ("testy", "A"): {'type': 'biosphere'},
#         ("testy", "B"): {'exchanges': [
#             {'input': ("testy", "A"),
#              'amount': 1,
#              'type': 'technosphere'},
#             {'input': ("testy", "A"),
#              'amount': 2,
#              'type': 'technosphere'},
#             {'input': ("testy", "C"),
#              'amount': 2,
#              'type': 'biosphere'},
#             {'input': ("testy", "C"),
#              'amount': 3,
#              'type': 'biosphere'},
#             {'input': ("testy", "B"),
#              'amount': 4,
#              'type': 'production'},
#             {'input': ("testy", "B"),
#              'amount': 1,
#              'type': 'production'},
#         ]}
#     }
#     database.write(data)
#     lookup = {k: mapping[("testy", k)] for k in "ABC"}
#     expected = sorted([
#         (lookup['A'], lookup['B'], 1),
#         (lookup['A'], lookup['B'], 2),
#         (lookup['B'], lookup['B'], 1),
#         (lookup['B'], lookup['B'], 4),
#         (lookup['C'], lookup['C'], 1),
#         (lookup['C'], lookup['B'], 2),
#         (lookup['C'], lookup['B'], 3),
#     ])
#     array = np.load(database.filepath_processed())
#     assert array.shape == (7,)
#     result = [(array['input'][x], array['output'][x], array['amount'][x])
#             for x in range(7)]
#     assert expected == result

# @bw2test
# def test_process_adds_to_mappings():
#     database = DatabaseChooser("testy")
#     database_data = {
#         ("testy", "A"): {'location': 'CH'},
#         ("testy", "B"): {'location': 'DE'},
#     }
#     database.write(database_data)
#     assert ("testy", "A") in mapping and ("testy", "B") in mapping
#     assert "CH" in geomapping and "DE" in geomapping

# @bw2test
# def test_process_unknown_object():
#     database = DatabaseChooser("testy")
#     data = {
#         ("testy", "A"): {},
#         ("testy", "B"): {'exchanges': [
#             {'input': ("testy", "A"),
#              'amount': 1,
#              'type': 'technosphere'},
#             {'input': ("testy", "C"),
#              'amount': 1,
#              'type': 'technosphere'},
#         ]},
#     }
#     with pytest.raises(UnknownObject):
#         database.write(data)
