"""FOOOFGroup object and associated code for using the FOOOF model on 2D groups of power spectra.

Notes
-----
FOOOFGroup object docs are imported from FOOOF object at runtime.
Methods without defined docstrings import docs at runtime, from aliased external functions.
"""

from functools import partial
from multiprocessing import Pool, cpu_count

import numpy as np

from fooof import FOOOF
from fooof.plts.fg import plot_fg
from fooof.core.reports import save_report_fg
from fooof.core.strings import gen_results_fg_str
from fooof.core.io import save_fg, load_jsonlines
from fooof.core.info import get_indices
from fooof.core.modutils import copy_doc_func_to_method, copy_doc_class, safe_import

###################################################################################################
###################################################################################################

# Set docstring attribute section to add when copying FOOOF docs -> FOOOFGroup
#  This section will be appended to the FOOOF Attributes section when copying over
ATT_ADD = """
    power_spectra : 2d array
        Input matrix of power spectra values, in linear space, as [n_power_spectra, n_freqs].
    group_results : list of FOOOFResults
        Results of FOOOF model fit for each power spectrum."""


@copy_doc_class(FOOOF, 'Attributes', ATT_ADD)
class FOOOFGroup(FOOOF):

    def __init__(self, *args, **kwargs):

        FOOOF.__init__(self, *args, **kwargs)

        self.power_spectra = None

        self._reset_group_results()


    def __iter__(self):

        for result in self.group_results:
            yield result


    def __len__(self):

        return len(self.group_results)


    def __getitem__(self, index):

        return self.group_results[index]


    def _reset_data_results(self, clear_freqs=True, clear_spectrum=True,
                            clear_results=True, clear_spectra=True):
        """Set (or reset) data & results attributes to empty.

        Parameters
        ----------
        clear_freqs : bool, optional, default: True
            Whether to clear frequency attributes.
        clear_power_spectrum : bool, optional, default: True
            Whether to clear power spectrum attribute.
        clear_results : bool, optional, default: True
            Whether to clear model results attributes.
        clear_spectra : bool, optional, default: True
            Whether to clear power spectra attribute.
        """

        super()._reset_data_results(clear_freqs, clear_spectrum, clear_results)
        if clear_spectra:
            self.power_spectra = None


    def _reset_group_results(self, length=0):
        """Set (or reset) results to be empty.

        Parameters
        ----------
        length : int, optional, default: 0
            Length of list of empty lists to initialize. If 0, creates a single empty list.
        """

        self.group_results = [[]] * length


    def add_data(self, freqs, power_spectra, freq_range=None):
        """Add data (frequencies and power spectrum values) to FOOOFGroup object.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the power spectra, in linear space.
        power_spectra : 2d array, shape=[n_power_spectra, n_freqs]
            Matrix of power values, in linear space.
        freq_range : list of [float, float], optional
            Frequency range to restrict power spectra to. If not provided, keeps the entire range.

        Notes
        -----
        If called on an object with existing data and/or results
        they will be cleared by this method call.
        """

        # If any data is already present, then clear data & results
        #   This is to ensure object consistency of all data & results
        if np.any(self.freqs):
            self._reset_data_results()
            self._reset_group_results()

        self.freqs, self.power_spectra, self.freq_range, self.freq_res = \
            self._prepare_data(freqs, power_spectra, freq_range, 2, self.verbose)


    def report(self, freqs=None, power_spectra=None, freq_range=None, n_jobs=1):
        """Run FOOOF across a group, and display a report, comprising a plot, and printed results.

        Parameters
        ----------
        freqs : 1d array, optional
            Frequency values for the power_spectra, in linear space.
        power_spectra : 2d array, shape: [n_power_spectra, n_freqs], optional
            Matrix of power spectrum values, in linear space.
        freq_range : list of [float, float], optional
            Desired frequency range to run FOOOF on. If not provided, fits the entire given range.
        n_jobs : int, optional, default: 1
            Number of jobs to run in parallel.
            1 is no parallelization. -1 uses all available cores.

        Notes
        -----
        Data is optional if data has been already been added to FOOOF object.
        """

        self.fit(freqs, power_spectra, freq_range, n_jobs=n_jobs)
        self.plot()
        self.print_results(False)


    def fit(self, freqs=None, power_spectra=None, freq_range=None, n_jobs=1):
        """Run FOOOF across a group of power_spectra.

        Parameters
        ----------
        freqs : 1d array, optional
            Frequency values for the power_spectra, in linear space.
        power_spectra : 2d array, shape: [n_power_spectra, n_freqs], optional
            Matrix of power spectrum values, in linear space.
        freq_range : list of [float, float], optional
            Desired frequency range to run FOOOF on. If not provided, fits the entire given range.
        n_jobs : int, optional, default: 1
            Number of jobs to run in parallel.
            1 is no parallelization. -1 uses all available cores.

        Notes
        -----
        Data is optional if data has been already been added to FOOOF object.
        """

        # If freqs & power spectra provided together, add data to object.
        if freqs is not None and power_spectra is not None:
            self.add_data(freqs, power_spectra, freq_range)

        # Run linearly
        if n_jobs == 1:
            self._reset_group_results(len(self.power_spectra))
            for ind, power_spectrum in \
                _progress(enumerate(self.power_spectra), self.verbose, len(self)):
                self._fit(power_spectrum=power_spectrum)
                self.group_results[ind] = self._get_results()

        # Run in parallel
        else:
            self._reset_group_results()
            n_jobs = cpu_count() if n_jobs == -1 else n_jobs
            with Pool(processes=n_jobs) as pool:
                self.group_results = list(_progress(pool.imap(partial(_par_fit, fg=self),
                                                              self.power_spectra),
                                                    self.verbose, len(self.power_spectra)))

        self._reset_data_results(clear_freqs=False, clear_spectra=False)


    def get_results(self):
        """Return the results run across a group of power spectra."""

        return self.group_results


    def get_params(self, name, col=None):
        """Return model fit parameters for specified feature(s).

        Parameters
        ----------
        name : {'aperiodic_params', 'peak_params', 'gaussian_params', 'error', 'r_squared'}
            Name of the data field to extract across the group.
        col : {'CF', 'PW', 'BW', 'offset', 'knee', 'exponent'} or int, optional
            Column name / index to extract from selected data, if requested.
            Only used for name of {'aperiodic_params', 'peak_params', 'gaussian_params'}.

        Returns
        -------
        out : ndarray
            Requested data.

        Notes
        -----
        For further description of the data you can extract, check the FOOOFResults documentation.
        """

        if not self.group_results:
            raise RuntimeError('No model fit data is available to extract - can not proceed.')

        # If col specified as string, get mapping back to integer
        if isinstance(col, str):
            col = get_indices(self.aperiodic_mode)[col]

        # Pull out the requested data field from the group data
        # As a special case, peak_params are pulled out in a way that appends
        #  an extra column, indicating from which FOOOF run each peak comes from
        if name in ('peak_params', 'gaussian_params'):
            out = np.array([np.insert(getattr(data, name), 3, index, axis=1)
                            for index, data in enumerate(self.group_results)])
            # This updates index to grab selected column, and the last colum
            #  This last column is the 'index' column (FOOOF object source)
            if col is not None:
                col = [col, -1]
        else:
            out = np.array([getattr(data, name) for data in self.group_results])

        # Some data can end up as a list of separate arrays.
        #   If so, concatenate it all into one 2d array
        if isinstance(out[0], np.ndarray):
            out = np.concatenate([arr.reshape(1, len(arr)) \
                if arr.ndim == 1 else arr for arr in out], 0)

        # Select out a specific column, if requested
        if col is not None:
            out = out[:, col]

        return out


    @copy_doc_func_to_method(plot_fg)
    def plot(self, save_fig=False, file_name='FOOOFGroup_plot', file_path=None):

        plot_fg(self, save_fig, file_name, file_path)


    @copy_doc_func_to_method(save_report_fg)
    def save_report(self, file_name='FOOOFGroup_report', file_path=None):

        save_report_fg(self, file_name, file_path)


    @copy_doc_func_to_method(save_fg)
    def save(self, file_name='FOOOFGroup_results', file_path=None, append=False,
             save_results=False, save_settings=False, save_data=False):

        save_fg(self, file_name, file_path, append, save_results, save_settings, save_data)


    def load(self, file_name='FOOOFGroup_results', file_path=None):
        """Load FOOOFGroup data from file, reconstructing the group_results.

        Parameters
        ----------
        file_name : str, optional
            File from which to load data.
        file_path : str, optional
            Path to directory from which to load from.
            If not provided, loads from current directory.
        """

        # Clear results so as not to have possible prior results interfere
        self._reset_group_results()

        for ind, data in enumerate(load_jsonlines(file_name, file_path)):

            self._add_from_dict(data)

            # Only load settings from first line (rest will be duplicates, if there)
            if ind == 0:
                self._check_loaded_settings(data)

            self._check_loaded_results(data)
            self.group_results.append(self._get_results())

        # Reset peripheral data from last loaded result, keeping freqs info
        self._reset_data_results(False)


    def get_fooof(self, ind, regenerate=False):
        """Return a FOOOF object from specified model in a FOOOFGroup object.

        Parameters
        ----------
        ind : int
            The index of the FOOOFResults in FOOOFGroup.group_results to load.
        regenerate : bool, optional, default: False
            Whether to regenerate the model fits from the given fit parameters.

        Returns
        -------
        inst : FOOOF() object
            The FOOOFResults data loaded into a FOOOF object.
        """

        # Initialize a FOOOF object, with same settings as current FOOOFGroup
        fm = FOOOF(*self.get_settings(), verbose=self.verbose)

        # Add data for specified single power spectrum, if available
        #  The power spectrum is inverted back to linear, as it's re-logged when added to FOOOF
        if np.any(self.power_spectra):
            fm.add_data(self.freqs, np.power(10, self.power_spectra[ind]))
        # If no power spectrum data available, copy over data information & regenerate freqs
        else:
            fm.add_meta_data(self.get_meta_data())

        # Add results for specified power spectrum, regenerating full fit if requested
        fm.add_results(self.group_results[ind])
        if regenerate:
            fm._regenerate_model()

        return fm


    def print_results(self, concise=False):
        """Print out FOOOFGroup results.

        Parameters
        ----------
        concise : bool, optional, default: False
            Whether to print the report in a concise mode, or not.
        """

        print(gen_results_fg_str(self, concise))


    def _fit(self, *args, **kwargs):
        """Create an alias to FOOOF.fit for FOOOFGroup object, for internal use."""

        super().fit(*args, **kwargs)


    def _get_results(self):
        """Create an alias to FOOOF.get_results for FOOOFGroup object, for internal use."""

        return super().get_results()

    def _check_width_limits(self):
        """Check and warn about bandwidth limits / frequency resolution interaction."""

        # Only check & warn on first power spectrum (to avoid spamming stdout for each spectrum).
        if self.power_spectra[0, 0] == self.power_spectrum[0]:
            super()._check_width_limits()

###################################################################################################
###################################################################################################

def _par_fit(power_spectrum, fg):
    """Helper function for running in parallel."""

    fg._fit(power_spectrum=power_spectrum)

    return fg._get_results()


def _progress(iterable, verbose, n_to_run):
    """Add a progress bar to an iterable to be processed.

    Parameters
    ----------
    iterable : list or iterable
        Iterable object to potentially apply progress tracking to.
    verbose : 'tqdm', 'tqdm_notebook' or boolean
        Which type of verbosity to do.
    n_to_run : int
        Number of jobs to complete.

    Returns
    -------
    pbar : iterable or tqdm object
        Iterable object, with TQDM progress functionality, if requested.

    Notes
    -----
    The explicit n_to_run input is required as tqdm requires this in the parallel case.
    The `tqdm` object that is potentially returned acts the same as the underlying iterable,
    with the addition of printing out progress everytime items are requested.
    """

    # Check verbose specifier is okay
    tqdm_options = ['tqdm', 'tqdm_notebook']
    if not isinstance(verbose, bool) and not verbose in tqdm_options:
        #print('Verbose option not understood. Proceeding without any.')
        raise ValueError('Verbose option not understood.')

    if verbose:

        # Progress bar options, using tqdm
        if verbose in tqdm_options:

            # Get tqdm, and set which approach to use from tqdm
            #   Approch to use from tqdm should be what's specified in 'verbose'
            tqdm_mod = safe_import('tqdm')
            tqdm_type = verbose

            # Pulls out the specific tqdm approach to be used from the tqdm module, if available
            tqdm = getattr(tqdm_mod, tqdm_type) if tqdm_mod else None

            if not tqdm:
                print('tqdm requested but is not installed. Proceeding without progress bar.')
                pbar = iterable
            else:
                pbar = tqdm(iterable, desc='Running FOOOFGroup:', total=n_to_run,
                            dynamic_ncols=True)

        # If 'verbose' was just 'True', print out a marker of what is being run (no progress bar)
        else:
            print('Running FOOOFGroup across {} power spectra.'.format(n_to_run))
            pbar = iterable

    else:
        pbar = iterable

    return pbar
