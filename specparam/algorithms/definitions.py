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


def check_algorithms():
    """Check the set of available fit algorithms."""

    print('Available algorithms:')
    for algorithm in ALGORITHMS.values():
        algorithm = algorithm()
        print('    {:12s} : {:s}'.format(algorithm.name, algorithm.description))


check_algorithm_definition = partial(check_selection, definition=Algorithm)
