"""Functionality to check available algorithm definitions."""

from specparam.reports.strings import _format

###################################################################################################
###################################################################################################

def check_algorithms(concise=False):
    """Check the set of available fit algorithms."""

    from specparam.algorithms.definitions import ALGORITHMS

    str_lst = []
    str_lst.extend(['AVAILABLE ALGORITHMS', ''])

    for algorithm in ALGORITHMS.values():
        algorithm = algorithm()
        str_lst.append('{:s} : {:s}'.format(algorithm.name, algorithm.description))

    print(_format(str_lst, concise))
