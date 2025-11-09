"""Define collection of fitting algorithms."""

from functools import partial

from specparam.utils.checks import check_selection
from specparam.algorithms.algorithm import Algorithm
from specparam.algorithms.spectral_fit import SpectralFitAlgorithm

###################################################################################################
###################################################################################################

# Collect available fitting algorithms
ALGORITHMS = {
    'spectral_fit' : SpectralFitAlgorithm,
}


check_algorithm_definition = partial(check_selection, definition=Algorithm)
