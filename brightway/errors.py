class BrightwayError(Exception):
    pass


class MissingBackend(BrightwayError):
    """Missing backend for given project"""
    pass
