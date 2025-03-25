"""Define common base objects."""

from copy import deepcopy

import numpy as np

from specparam.utils.array import unlog
from specparam.utils.checks import check_inds
from specparam.modes.modes import Modes
from specparam.modes.items import OBJ_DESC
from specparam.data.utils import get_results_by_ind
from specparam.io.utils import get_files
from specparam.io.files import load_json, load_jsonlines
from specparam.io.models import save_model, save_group, save_event
from specparam.modutils.errors import NoDataError, FitError
from specparam.modutils.docs import (copy_doc_func_to_method, docs_get_section,
                                     replace_docstring_sections)
from specparam.objs.data import BaseData
from specparam.objs.utils import run_parallel_group, run_parallel_event, pbar
from specparam.objs.metrics import Metrics
from specparam.reports.strings import gen_modes_str, gen_settings_str, gen_issue_str

###################################################################################################
###################################################################################################

class CommonBase():
    """Define CommonBase object."""

    def __init__(self, verbose):
        """Initialize object."""

        self.metrics = Metrics()
        self.metrics.set_defaults()

        self.verbose = verbose


    def copy(self):
        """Return a copy of the current object."""

        return deepcopy(self)


    def fit(self, freqs=None, power_spectrum=None, freq_range=None):
        """Fit a power spectrum as a combination of periodic and aperiodic components.

        Parameters
        ----------
        freqs : 1d array, optional
            Frequency values for the power spectrum, in linear space.
        power_spectrum : 1d array, optional
            Power values, which must be input in linear space.
        freq_range : list of [float, float], optional
            Frequency range to restrict power spectrum to.
            If not provided, keeps the entire range.

        Raises
        ------
        NoDataError
            If no data is available to fit.
        FitError
            If model fitting fails to fit. Only raised in debug mode.

        Notes
        -----
        Data is optional, if data has already been added to the object.
        """

        # If freqs & power_spectrum provided together, add data to object.
        if freqs is not None and power_spectrum is not None:
            self.add_data(freqs, power_spectrum, freq_range)

        # Check that data is available
        if not self.data.has_data:
            raise NoDataError("No data available to fit, can not proceed.")

        # In rare cases, the model fails to fit, and so uses try / except
        try:

            # If not set to fail on NaN or Inf data at add time, check data here
            #   This serves as a catch all for curve_fits which will fail given NaN or Inf
            #   Because FitError's are by default caught, this allows fitting to continue
            if not self.data._check_data:
                if np.any(np.isinf(self.data.power_spectrum)) or \
                    np.any(np.isnan(self.data.power_spectrum)):
                    raise FitError("Model fitting was skipped because there are NaN or Inf "
                                   "values in the data, which preclude model fitting.")

            # Call the fit function from the algorithm object
            self.algorithm._fit()

            # Compute post-fit metrics
            self.metrics.compute_metrics(self.data, self.results)

            # TEMP: alias metric results into updated management
            self.results.error_ = self.metrics['error-mae'].output
            self.results.r_squared_ = self.metrics['gof-r_squared'].output

        except FitError:

            # If in debug mode, re-raise the error
            if self.algorithm._debug:
                raise

            # Clear any interim model results that may have run
            #   Partial model results shouldn't be interpreted in light of overall failure
            self.results._reset_results(True)

            # Print out status
            if self.verbose:
                print("Model fitting was unsuccessful.")


    def get_data(self, component='full', space='log'):
        """Get a data component.

        Parameters
        ----------
        component : {'full', 'aperiodic', 'peak'}
            Which data component to return.
                'full' - full power spectrum
                'aperiodic' - isolated aperiodic data component
                'peak' - isolated peak data component
        space : {'log', 'linear'}
            Which space to return the data component in.
                'log' - returns in log10 space.
                'linear' - returns in linear space.

        Returns
        -------
        output : 1d array
            Specified data component, in specified spacing.

        Notes
        -----
        The 'space' parameter doesn't just define the spacing of the data component
        values, but rather defines the space of the additive data definition such that
        `power_spectrum = aperiodic_component + peak_component`.
        With space set as 'log', this combination holds in log space.
        With space set as 'linear', this combination holds in linear space.
        """

        if not self.data.has_data:
            raise NoDataError("No data available to fit, can not proceed.")
        assert space in ['linear', 'log'], "Input for 'space' invalid."

        if component == 'full':
            output = self.data.power_spectrum if space == 'log' \
                else unlog(self.data.power_spectrum)
        elif component == 'aperiodic':
            output = self.results._spectrum_peak_rm if space == 'log' else \
                unlog(self.data.power_spectrum) / unlog(self.results._peak_fit)
        elif component == 'peak':
            output = self.results._spectrum_flat if space == 'log' else \
                unlog(self.data.power_spectrum) - unlog(self.results._ap_fit)
        else:
            raise ValueError('Input for component invalid.')

        return output


    def print_modes(self, description=False, concise=False):
        """Print out the current fit modes.

        Parameters
        ----------
        description : bool, optional, default: False
            Whether to print out a description with current fit modes.
        concise : bool, optional, default: False
            Whether to print the report in a concise mode, or not.
        """

        print(gen_modes_str(self, description, concise))


    def print_settings(self, description=False, concise=False):
        """Print out the current settings.

        Parameters
        ----------
        description : bool, optional, default: False
            Whether to print out a description with current settings.
        concise : bool, optional, default: False
            Whether to print the report in a concise mode, or not.
        """

        print(gen_settings_str(self, description, concise))


    @staticmethod
    def print_report_issue(concise=False):
        """Prints instructions on how to report bugs and/or problematic fits.

        Parameters
        ----------
        concise : bool, optional, default: False
            Whether to print the report in a concise mode, or not.
        """

        print(gen_issue_str(concise))


    def _add_from_dict(self, data):
        """Add data to object from a dictionary.

        Parameters
        ----------
        data : dict
            Dictionary of data to add to self.
        """

        for key in data.keys():
            if getattr(self, key, False) is not False:
                setattr(self, key, data[key])
            elif getattr(self.data, key, False) is not False:
                setattr(self.data, key, data[key])
            elif getattr(self.results, key, False) is not False:
                setattr(self.results, key, data[key])


    def _check_loaded_modes(self, data):
        """Check if fit modes added, and update the object as needed.

        Parameters
        ----------
        data : dict
            A dictionary of data that has been added to the object.
        """

        # TEMP / ToDo: not quite clear if this is the right place
        #   And/or - might want a clearer process to 'reset' Modes

        if 'aperiodic_mode' in data and 'periodic_mode' in data:
            self.modes = Modes(aperiodic=data['aperiodic_mode'],
                               periodic=data['periodic_mode'])



# class CommonBase2D(CommonBase):

#     def __init__(self):
#         pass


# class BaseObject2D(CommonBase):
#     """Define Base object for fitting models to 2D data."""

#     def __init__(self, verbose=True):
#         """Initialize BaseObject2D object."""

#         CommonBase.__init__(self, verbose=verbose)


# class BaseObject2DT(BaseObject2D):
#     """Define Base object for fitting models to 2D data - tranpose version."""

#     def __init__(self, verbose=True):
#         """Initialize BaseObject2DT object."""

#         BaseObject2D.__init__(self, verbose=verbose)


# class BaseObject3D(BaseObject2DT):
#     """Define Base object for fitting models to 3D data."""

#     def __init__(self, verbose=True):
#         """Initialize BaseObject3D object."""

#         BaseObject2DT.__init__(self, verbose=verbose)
