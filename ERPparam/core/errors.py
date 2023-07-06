"""Custom error definitions for ERPparam."""

class ERPparamError(Exception):
    """Base class for errors in the ERPparam module."""

class FitError(ERPparamError):
    """Error for a failure to fit."""

class NoDataError(ERPparamError):
    """Error for if data is missing."""

class DataError(ERPparamError):
    """Error for if there is a problem with the data."""

class InconsistentDataError(ERPparamError):
    """Error for if the data is inconsistent."""

class IncompatibleSettingsError(ERPparamError):
    """Error for if settings are incompatible."""

class NoModelError(ERPparamError):
    """Error for if the model is not fit."""
