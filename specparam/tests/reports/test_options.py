"""Tests for specparam.reports.options."""

from specparam.reports.options import *

###################################################################################################
###################################################################################################

def test_check_algorithms():

    check_algorithms()

def test_check_metrics():

    check_metrics()
    check_metrics('gof')
    check_metrics('error')

def test_check_modes():

    check_modes()
    check_modes('aperiodic', True)
    check_modes('periodic', True)

def test_check_converters():

    check_converters()
    check_converters('aperiodic')
    check_converters('periodic')
