"""Tests for specparam.results.utils."""

from specparam.results.utils import *

###################################################################################################
###################################################################################################

# Test func for parallel tests
def inc(val):
    return val + 1

def test_run_parallel():

    data = [1, 2, 3, 4]

    results1 = run_parallel(inc, data, 2, None)
    assert results1 == [2, 3, 4, 5]

    results2 = run_parallel(inc, data, -1, None)
    assert results2 == [2, 3, 4, 5]

def test_pbar_no_tqdm():

    iterable = [1, 2, 3, 4]
    out = pbar(iterable, None, len(iterable))
    for el in out:
        pass

def test_pbar_with_tqdm(skip_if_no_tqdm):

    iterable = [1, 2, 3, 4]
    out = pbar(iterable, 'tqdm', len(iterable))
    for el in out:
        pass
