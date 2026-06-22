"""Sub-module for functionality related to parameters and parameter conversions."""

from .converter import AperiodicParamConverter, PeriodicParamConverter

# Link in report function to list available parameter converters
from specparam.reports.options import check_converters

