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
    space='log',
)

error_mse = Metric(
    category='error',
    measure='mse',
    description='Mean squared error of the model fit to the data.',
    func=compute_mean_squared_error,
    space='log',
)

error_rmse = Metric(
    category='error',
    measure='rmse',
    description='Root mean squared error of the model fit to the data.',
    func=compute_root_mean_squared_error,
    space='log',
)

error_medae = Metric(
    category='error',
    measure='medae',
    description='Median absolute error of the model fit to the data.',
    func=compute_median_abs_error,
    space='log',
)

error_maelin = Metric(
    category='error',
    measure='maelin',
    description='Mean absolute error of the model fit to the data, in linear space.',
    func=compute_mean_abs_error,
    space='linear',
)

###################################################################################################
## GOF

gof_rsquared = Metric(
    category='gof',
    measure='rsquared',
    description='R-squared between the model fit and the data.',
    func=compute_r_squared,
    space='log',
)

gof_rsquaredlin = Metric(
    category='gof',
    measure='rsquaredlin',
    description='R-squared between the model fit and the data, in linear space.',
    func=compute_r_squared,
    space='linear',
)

gof_adjrsquared = Metric(
    category='gof',
    measure='adjrsquared',
    description='Adjusted R-squared between the model fit and the data.',
    func=compute_adj_r_squared,
    kwargs={'n_params' : lambda data, results: \
            results.params.periodic.params.size + results.params.aperiodic.params.size},
    space='log',
)

###################################################################################################
## COLLECT ALL METRICS TOGETHER

METRICS = {

    # Error metrics - log spacing
    'error_mae' : error_mae,
    'error_mse' : error_mse,
    'error_rmse' : error_rmse,
    'error_medae' : error_medae,

    # Error metrics - linear spacing
    'error_maelin' : error_maelin,

    # GOF / r-squared metrics - log spacing
    'gof_rsquared' : gof_rsquared,
    'gof_adjrsquared' : gof_adjrsquared,

    # GOF / r-squared metrics - linear spacing
    'gof_rsquaredlin' : gof_rsquaredlin,

}


def check_metrics():
    """Check the set of available metrics."""

    print('Available metrics:')
    for metric in METRICS.values():
        print('    {:8s} {:12s} : {:s}'.format(metric.category, metric.measure, metric.description))


check_metric_definition = partial(check_selection, options=METRICS, definition=Metric)
