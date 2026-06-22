"""Test functions for specparam.compare.compare."""

from specparam import SpectralModel

from specparam.compare.compare import *

###################################################################################################
###################################################################################################

def test_model_comparison():

    mc1 = ModelComparison()
    assert isinstance(mc1, ModelComparison)

    # Test initializing with some models
    models = [SpectralModel(aperiodic_mode='fixed', periodic_mode='gaussian'),
              SpectralModel(aperiodic_mode='knee', periodic_mode='gaussian')]
    mc2 = ModelComparison(models)
    assert isinstance(mc2, ModelComparison)
    assert len(mc2) == len(models)
    for model in mc2:
        assert model

    # Test data gets linked / results do not
    for ind, model in enumerate(mc2.models[:-1]):
        model.data is mc2.models[ind+1].data
        model.results is not mc2.models[ind+1].results

def test_model_comparison_fit(tdata):

    mc = ModelComparison(\
        [SpectralModel(aperiodic_mode='fixed', periodic_mode='gaussian'),
         SpectralModel(aperiodic_mode='knee', periodic_mode='gaussian'),
    ])

    mc.fit(tdata.freqs, tdata.get_data('full', 'linear'))
    for model in mc:
        assert model.results.has_model

def test_model_comparison_reporting(tmodelcomp, tdata, skip_if_no_mpl):

    mc = tmodelcomp.copy()

    mc.report(tdata.freqs, tdata.get_data('full', 'linear'))

    mc.print()
    mc.plot()
