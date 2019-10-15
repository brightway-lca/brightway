from ..errors import InconsistentFields, NonUnique


def greedy_set_cover(data, exclude=None):
    """Find unique set of attributes that uniquely identifies each element in ``data``.

    Feature selection is a well known problem, and is analogous to the `set cover problem <https://en.wikipedia.org/wiki/Set_cover_problem>`__, for which there is a `well known heuristic <https://en.wikipedia.org/wiki/Set_cover_problem#Greedy_algorithm>`__.

    Args:
        data (iterable): List of dictionaries with the same fields.
        exclude (iterable): Fields to exclude during search for uniqueness. ``id`` is Always excluded.

    Returns:
        Set of attributes (strings)

    Raises:
        NonUnique: The given fields are not enough to ensure uniqueness
    """
    if exclude is None:
        exclude = {"id"}
    else:
        exclude = set(exclude)
        exclude.add("id")


def as_unique_attributes(data, exclude=None, include=None):
    """Format ``data`` as unique set of attributes and values for use in ``create_processed_datapackage``.

    Note: Each element in ``data`` must have the attributes ``id``.

        data = [
            {},
        ]

    Args:
        data (iterable): List of dictionaries with the same fields.
        exclude (iterable): Fields to exclude during search for uniqueness. ``id`` is Always excluded.
        include (iterable): Fields to include when returning, even if not unique

    Returns:
        (list of field names as strings, dictionary of data ids to values for given field names)

    Raises:
        InconsistentFields: Not all features provides all fields.
    """
    include = set([]) if include is None else set(include)
    fields = greedy_set_cover(data, exclude)

    if len({set(obj.keys()) for obj in data}) > 1:
        raise InconsistentFields

    def formatter(obj, fields, include):
        return {
            key: value
            for key, value in obj.items()
            if (key in fields or key in include or key == "id")
        }

    return (fields, [formatter(obj, fields, include) for obj in data])


def create_processed_datapackage(
    array,
    rows,
    cols,
    filepath=None,
    id_=None,
    metadata=None,
    replace=True,
    compress=True,
    in_memory=False,
):
    """Create a datapackage with numpy structured arrays and metadata.

    Exchanging large, dense datasets like MRIO tables is not efficient if each exchange must be listed separately. Instead, we would prefer to exchange the processed arrays used to build the matrices directly. However, these arrays use integer indices which are not consistent across computers or even Brightway projects. This function includes additional metadata to solve this problem, mapping these integer ids to enough attributes to uniquely identify each feature. Separate metadata files are included for each column in the array (i.e. the row and column indices).

    Args:
        array (numpy structured array): The numeric data. Usually generated via ``create_numpy_structured_array``.
        rows (dict): Dictionary mapping integer indices in ``row_value`` to a dictionary of attributes.
        cols (dict): Dictionary mapping integer indices in ``col_value`` to a dictionary of attributes.

    Returns:
        Something :)
    """
    pass
