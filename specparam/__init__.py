"""Spectral parameterization."""

from .version import __version__

from .bands import Bands
from .models import SpectralModel, SpectralGroupModel, SpectralTimeModel, SpectralTimeEventModel
from .models.utils import fit_models_3d
