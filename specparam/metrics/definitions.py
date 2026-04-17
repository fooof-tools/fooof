"""Collect together library of available built in metrics."""

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

# Collect available error metrics
ERROR_METRICS = {

    # log spacing
    'mae' : error_mae,
    'mse' : error_mse,
    'rmse' : error_rmse,
    'medae' : error_medae,

    # linear spacing
    'maelin' : error_maelin,
}

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

# Collect available error metrics
GOF_METRICS = {

    # log spacing
    'rsquared' : gof_rsquared,
    'adjrsquared' : gof_adjrsquared,

    # linear spacing
    'rsquaredlin' : gof_rsquaredlin,
}

###################################################################################################
## COLLECT ALL METRICS TOGETHER

# Collect a store of all available metrics
METRICS = {
    'error' : ERROR_METRICS,
    'gof' : GOF_METRICS,
}

###################################################################################################
## CHECKER FUNCTION

def check_metric_definition(metric):
    """Check a metric definition.

    Parameters
    ----------
    metric : Metric or dict or str
        Definition for a metric to check.
        If dict, should have keys corresponding to a metric definition.
        If str, should be the label corresponding to a defined metric (see `check_metrics`).

    Returns
    -------
    Metric
        Metric definition.
    """

    if isinstance(metric, dict):
        metric = Metric(**metric)
    elif isinstance(metric, str):
        category, label = metric.split('_')
        metric = check_selection(label, METRICS[category], Metric)
    else:
        metric = check_selection(metric, [], Metric)

    return metric
