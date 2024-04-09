"""Spectral parameterization."""

from .version import __version__

from .bands import Bands
from .objs import SpectralModel, SpectralGroupModel, SpectralTimeModel, SpectralTimeEventModel
from .objs.utils import fit_models_3d
