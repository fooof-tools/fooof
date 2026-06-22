"""Model comparison object."""

from copy import deepcopy

from specparam.models import SpectralModel
from specparam.plts.compare import plot_model_comparison
from specparam.reports.strings import gen_model_comparison_str
from specparam.modutils.docs import (copy_func_docstring_drop_first,
                                     docs_get_section, replace_docstring_sections)

###################################################################################################
###################################################################################################

class ModelComparison():
    """Model a power spectrum with multiple models.

    Parameters
    ----------
    models : list of SpectralModel
        Model definitions to fit and compare.
    """

    def __init__(self, models=None):
        """Initialize model comparison object."""

        self.models = []
        self.add_models(models)

    @replace_docstring_sections([docs_get_section(SpectralModel.fit.__doc__, 'Parameters')])
    def fit(self, freqs=None, data=None, freq_range=None, prechecks=True):
        """Fit models to a power spectrum.

        Parameters
        ----------
        % copied in from SpectralModel object
        """

        self.models[0].fit(freqs, data, freq_range, prechecks)
        for model in self.models[1:]:
            model.fit(prechecks=False)

    @replace_docstring_sections([docs_get_section(SpectralModel.report.__doc__, 'Parameters')])
    def report(self, freqs=None, data=None, freq_range=None,
               plt_log=False, plot_full_range=False, **plot_kwargs):
        """Run model fit, and display a report, which includes a plot, and printed results.

        Parameters
        ----------
        % copied in from SpectralModel object
        """

        self.fit(freqs, data, freq_range, prechecks)
        self.print('comparison')
        self.plot(plt_log=plt_log,
                  freqs=freqs if plot_full_range else plot_kwargs.pop('plot_freqs', None),
                  power_spectrum=power_spectrum if \
                      plot_full_range else plot_kwargs.pop('plot_power_spectrum', None),
                  freq_range=plot_kwargs.pop('plot_freq_range', None),
                  **plot_kwargs)

    def add_models(self, models, clear=False):
        """Add model definitions.

        Parameters
        ----------
        models : list of SpectralModel
            Model definitions to add to the object.
        clear : bool, optional, default: False
            Whether to clear the object of previous model definitions before adding.
        """

        for model in models:
            self.models.append(deepcopy(model))

        if self.models:
            self.data = deepcopy(models[0].data)
            for model in self.models:
                model.data = self.data
                model.algorithm._reset_subobjects(data=self.data)

    @copy_func_docstring_drop_first(plot_model_comparison)
    def plot(self):

        plot_model_comparison(self)

    def print(self, info='comparison'):
        """Print out result information."""

        if info == 'comparison':
            print(gen_model_comparison_str(self))
        else:
            for model in self.models:
                model.print(info)
