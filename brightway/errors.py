class BrightwayError(Exception):
    pass


class MissingBackend(BrightwayError):
    """The backend for this project is not currently installed."""
    pass
