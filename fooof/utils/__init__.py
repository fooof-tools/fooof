"""Utilities sub-module for FOOOF."""

from .debug import sys_info
from .params import compute_knee_frequency
from .io import load_fooof, load_fooofgroup
from .data import trim_spectrum, compute_pointwise_error
from .reports import methods_report_info, methods_report_text
