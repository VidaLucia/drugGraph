class RxNormError(Exception):
    """Base exception for RxNorm-related failures."""
    pass
class RxNormUnavailableError(RxNormError):
    """Raised when RxNorm cannot be reached or returns a server error."""
    pass
class RxNormResponseError(RxNormError):
    """Raised when RxNorm returns malformed or unexpected data."""
    pass