"""Define collection of fitting algorithms."""

from specparam.algorithms.spectral_fit import SpectralFitAlgorithm

###################################################################################################
###################################################################################################

# Collect available fitting algorithms
ALGORITHMS = {
    'spectral_fit' : SpectralFitAlgorithm,
}
