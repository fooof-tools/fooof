"""Custom error definitions for FOOOF."""

class FOOOFError(Exception):
    """Base class for errors in the FOOOF module."""

class FitError(FOOOFError):
    """Error for a failure to fit."""

class NoDataError(FOOOFError):
    """Error for if data is missing."""

class DataError(FOOOFError):
    """Error for if there is a problem with the data."""

class InconsistentDataError(FOOOFError):
    """Error for if the data is inconsistent."""

class IncompatibleSettingsError(FOOOFError):
    """Error for if settings are incompatible."""

class NoModelError(FOOOFError):
    """Error for if the model is not fit."""
