"""Custom error definitions for FOOOF."""

class FOOOFError(Exception):
    """Base class for errors in the FOOOF module."""
    pass

class FitError(FOOOFError):
    """Error for a failure to fit."""
    pass

class NoDataError(FOOOFError):
    """Error for if data is missing."""
    pass

class DataError(FOOOFError):
    """Error if there is a problem with the data."""
    pass

class InconsistentDataError(FOOOFError):
    """Error for if the data is inconsistent."""
    pass

class IncompatibleSettingsError(FOOOFError):
    """Error for if settings are incompatible."""
    pass

class NoModelError(FOOOFError):
    """Error for if the model is not fit."""
    pass
