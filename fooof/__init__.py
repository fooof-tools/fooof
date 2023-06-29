"""FOOOF - Fitting Oscillations & One-Over F"""

from .version import __version__

# Deprecation of fooof / move to specparam message
#   Note: this warning is for fooof v1.1 specifically, and should be removed in specparam 2.0
from warnings import warn, simplefilter
simplefilter('always')  # make sure user sees it once, on every import
DEPRECATION_TEXT = ("\nThe `fooof` package is being deprecated and replaced by the "
    "`specparam` (spectral parameterization) package."
    "\nThis version of `fooof` (1.1) is fully functional, but will not be further updated."
    "\nNew projects are recommended to update to using `specparam` (see Changelog for details).")
warn(DEPRECATION_TEXT, DeprecationWarning, stacklevel=2)

from .bands import Bands
from .objs import FOOOF, FOOOFGroup
from .objs.utils import fit_fooof_3d
