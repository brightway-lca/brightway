class BrightwayError(Exception):
    pass


class MissingBackend(BrightwayError):
    """Missing backend for given project"""

    pass


class DuplicateDtypeLabel(BrightwayError):
    """Dtype has conflicting labels"""

    pass
