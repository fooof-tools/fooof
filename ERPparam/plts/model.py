"""Plots for the ERPparam object.

Notes
-----
This file contains plotting functions that take as input a ERPparam object.
"""

import numpy as np

from ERPparam.core.utils import nearest_ind
from ERPparam.core.modutils import safe_import, check_dependency
from ERPparam.sim.gen import gen_periodic
from ERPparam.utils.data import trim_spectrum
from ERPparam.utils.params import compute_fwhm
from ERPparam.plts.spectra import plot_spectra
from ERPparam.plts.settings import PLT_FIGSIZES, PLT_COLORS
from ERPparam.plts.utils import check_ax, check_plot_kwargs, savefig
from ERPparam.plts.style import style_spectrum_plot, style_plot, style_erp_plot

plt = safe_import('.pyplot', 'matplotlib')

###################################################################################################
###################################################################################################

@check_dependency(plt, 'matplotlib')
def plot_ERPparam(model, ax=None, y_label=None):
    """Plot ERP and model fit results."""

    # create figure
    if ax is None:
        fig, ax = plt.subplots(1,1, figsize=PLT_FIGSIZES['spectral'])

    # plot signal
    ax.plot(model.time, model.signal, alpha=0.5, label='ERP')

    # plot fit
    if model.peak_params_ is not None:
        # plot full model fit
        ax.plot(model.time, model._peak_fit, linestyle='--', color='k', label='Gaussian fit')
    
        # plot peak indices
        ax.scatter(model.time[model.peak_indices_[:,1]], model.signal[model.peak_indices_[:,1]], color='r', label='Peak fit')
        half_mag_indices = np.concatenate((model.peak_indices_[:,0], model.peak_indices_[:,2]))
        ax.scatter(model.time[half_mag_indices], model.signal[half_mag_indices], color='b', label='Half-mag fit')
    
    # label
    if y_label is not None:
        ax.set(xlabel="time (s)", ylabel=y_label)
    else:
        ax.set(xlabel="time (s)", ylabel="amplitude")
    ax.legend()

    # style
    style_erp_plot(ax)
    plt.show()
