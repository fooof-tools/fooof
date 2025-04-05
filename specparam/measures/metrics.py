"""Collect together library of available built in metrics."""

from specparam.objs.metrics import Metric
from specparam.measures.error import (compute_mean_abs_error, compute_mean_squared_error,
                                      compute_root_mean_squared_error, compute_median_abs_error)
from specparam.measures.gof import compute_r_squared, compute_adj_r_squared

###################################################################################################
###################################################################################################

METRICS = {

    # Available error metrics
    'error_mae' : Metric('error', 'mae', compute_mean_abs_error),
    'error_mse' : Metric('error', 'mse', compute_mean_squared_error),
    'error_rmse' : Metric('error', 'rmse', compute_root_mean_squared_error),
    'error_medae' : Metric('error', 'medae', compute_median_abs_error),

    # Available GOF / r-squared metrics
    'gof_rsquared' : Metric('gof', 'rsquared', compute_r_squared),
    #'gof_adjrsquared' : Metric('gof', 'adjrsquared', compute_adj_r_squared,
    #                           {'results' : 'n_params_'}),
}
