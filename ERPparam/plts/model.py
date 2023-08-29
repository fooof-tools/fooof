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
def plot_ERPparam(self, ax=None, y_label=None):
    """Plot ERP and model fit results."""

    # create figure
    if ax is None:
        fig, ax = plt.subplots(1,1, figsize=PLT_FIGSIZES['spectral'])

    # plot signal
    ax.plot(self.time, self.signal, alpha=0.5, label='ERP')

    # plot fit
    if self.peak_params_ is not None:
        ax.plot(self.time, self._peak_fit, linestyle='--', color='k', label='Gaussian fit')
        ax.scatter(self.peak_params_[:,0], self.peak_params_[:,1], color='r', label='Peak fit')
    
    # label
    if y_label is not None:
        ax.set(xlabel="time (s)", ylabel=y_label)
    else:
        ax.set(xlabel="time (s)", ylabel="amplitude")
    ax.legend()

    # style
    style_erp_plot(ax)
    plt.show()

