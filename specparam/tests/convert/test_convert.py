"""Test functions for specparam.convert.convert."""

from specparam.convert.convert import *

###################################################################################################
###################################################################################################

def test_convert_aperiodic_params(tfm):

    # Take copy to not change test object
    ntfm = tfm.copy()

    converted = convert_aperiodic_params(ntfm,
        {'offset' : None, 'exponent' : lambda fit_value, model : 1.})
    assert converted[ntfm.modes.aperiodic.params.indices['offset']] == \
        ntfm.results.get_params('aperiodic', 'offset', 'fit')
    assert converted[ntfm.modes.aperiodic.params.indices['exponent']] == 1.

def test_convert_periodic_params(tfm):

    # Take copy to not change test object
    ntfm = tfm.copy()

    converted = convert_periodic_params(ntfm,
        {'cf' : None, 'pw' : lambda fit_value, model, peak_ind : 1., 'bw' : None})
    assert np.array_equal(converted[:, ntfm.modes.periodic.params.indices['pw']],
                          np.array([1.] * ntfm.results.n_peaks))
    for param in ['cf', 'bw']: # test parameters that should not have been changed
        assert np.array_equal(converted[:, ntfm.modes.periodic.params.indices[param]],
                              ntfm.results.get_params('periodic', param, 'fit'))
