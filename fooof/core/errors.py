"""Custom error definitions."""

class SpecParamError(Exception):
    """Base class for custom errors."""

class FitError(SpecParamError):
    """Error for a failure to fit."""

class NoDataError(SpecParamError):
    """Error for if data is missing."""

class DataError(SpecParamError):
    """Error for if there is a problem with the data."""

class InconsistentDataError(SpecParamError):
    """Error for if the data is inconsistent."""

class IncompatibleSettingsError(SpecParamError):
    """Error for if settings are incompatible."""

class NoModelError(SpecParamError):
    """Error for if the model is not fit."""
