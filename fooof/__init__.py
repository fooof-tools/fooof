"""FOOOF - Fitting Oscillations & One-Over F"""

from .version import __version__

# deprecation of fooof for specparam
from warnings import warn, simplefilter
simplefilter('always') # make sure user sees it once, on every import
warn_text = 'Warning: The fooof package is being deprecated in favor of the\
 spectral parameterization (specparam) package. This version of fooof is\
 functional, however we recommend upgrading to specparam, because this 1.1\
 version of fooof will not have continuing development. All new features and\
 development will be done on the specparam package.'
warn(warn_text, DeprecationWarning, stacklevel=2)

from .bands import Bands
from .objs import FOOOF, FOOOFGroup
from .objs.utils import fit_fooof_3d
