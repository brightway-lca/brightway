class BrightwayError(Exception):
    pass


class MissingBackend(BrightwayError):
    """Missing backend for given project"""

    pass


class InvalidName(BrightwayError):
    """Name fails datapackage requirements:

    A short url-usable (and preferably human-readable) name of the package. This MUST be lower-case and contain only alphanumeric characters along with ".", "_" or "-" characters."""

    pass


class DuplicateDtypeLabel(BrightwayError):
    """Dtype has conflicting labels"""

    pass
