"""Collect together library of available built in metrics."""

from functools import partial

from specparam.metrics.metrics import Metric
from specparam.metrics.error import (compute_mean_abs_error, compute_mean_squared_error,
                                     compute_root_mean_squared_error, compute_median_abs_error)
from specparam.metrics.gof import compute_r_squared, compute_adj_r_squared
from specparam.utils.checks import check_selection

###################################################################################################
## ERROR METRICS

error_mae = Metric(
    category='error',
    measure='mae',
    description='Mean absolute error of the model fit to the data.',
    func=compute_mean_abs_error,
)

error_mse = Metric(
    category='error',
    measure='mse',
    description='Mean squared error of the model fit to the data.',
    func=compute_mean_squared_error
)

error_rmse = Metric(
    category='error',
    measure='rmse',
    description='Root mean squared error of the model fit to the data.',
    func=compute_root_mean_squared_error,
)

error_medae = Metric(
    category='error',
    measure='medae',
    description='Median absolute error of the model fit to the data.',
    func=compute_median_abs_error,
)

###################################################################################################
## GOF

gof_rsquared = Metric(
    category='gof',
    measure='rsquared',
    description='R-squared between the model fit and the data.',
    func=compute_r_squared,
)

gof_adjrsquared = Metric(
    category='gof',
    measure='adjrsquared',
    description='Adjusted R-squared between the model fit and the data.',
    func=compute_adj_r_squared,
    kwargs={'n_params' : lambda data, results: \
            results.params.periodic.params.size + results.params.aperiodic.params.size},
)

###################################################################################################
## COLLECT ALL METRICS TOGETHER

METRICS = {

    # Available error metrics
    'error_mae' : error_mae,
    'error_mse' : error_mse,
    'error_rmse' : error_rmse,
    'error_medae' : error_medae,

    # Available GOF / r-squared metrics
    'gof_rsquared' : gof_rsquared,
    'gof_adjrsquared' : gof_adjrsquared,

}


def check_metrics():
    """Check the set of available metrics."""

    print('Available metrics:')
    for metric in METRICS.values():
        print('    {:8s} {:12s} : {:s}'.format(metric.category, metric.measure, metric.description))


check_metric_definition = partial(check_selection, definition=Metric)
