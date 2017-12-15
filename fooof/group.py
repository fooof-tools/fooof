"""FOOOF - Group fitting object and methods.

Notes
-----
- FOOOFGroup object docs are imported from FOOOF object at runtime.
- Methods without defined docstrings import docs at runtime, from aliased external functions.
"""

from functools import partial
from multiprocessing import Pool, cpu_count

import numpy as np

from fooof import FOOOF
from fooof.plts.fg import plot_fg
from fooof.core.reports import create_report_fg
from fooof.core.strings import gen_results_str_fg
from fooof.core.io import save_fg, load_jsonlines
from fooof.core.modutils import get_obj_desc, docs_drop_param

###################################################################################################
###################################################################################################

class FOOOFGroup(FOOOF):

    def __init__(self, *args, **kwargs):

        FOOOF.__init__(self, *args, **kwargs)

        self.psds = np.array([])

        self._reset_group_results()


    def __iter__(self):

        for result in self.group_results:
            yield result


    def __len__(self):

        return len(self.group_results)


    def _reset_group_results(self, length=0):
        """Set (or reset) results to be empty.

        Parameters
        ----------
        length : int, optional
            Length of list of empty lists to initialize. If 0, single empty list. default: 0
        """

        self.group_results = [[]] * length


    def add_data(self, freqs, psds, freq_range=None):
        """Add data (frequencies and PSD values) to FOOOFGroup object.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the PSD, in linear space.
        psd : 2d array
            Matrix of PSD values, in linear space. Shape should be [n_psds, n_freqs].
        freq_range : list of [float, float], optional
            Frequency range to restrict PSD to. If not provided, keeps the entire range.
        """

        if freqs.ndim != 1 or psds.ndim != 2:
            raise ValueError('Inputs are not the right dimensions.')

        self.freqs, self.psds, self.freq_range, self.freq_res = \
            self._prepare_data(freqs, psds, freq_range, self.verbose)


    def model(self, freqs=None, psds=None, freq_range=None, n_jobs=1):
        """Run FOOOF across a group of PSDs, then plot and print results.

        Parameters
        ----------
        freqs : 1d array, optional
            Frequency values for the PSDs, in linear space.
        psds : 2d array, optional
            Matrix of PSD values, in linear space. Shape should be [n_psds, n_freqs].
        freq_range : list of [float, float], optional
            Desired frequency range to run FOOOF on. If not provided, fits the entire given range.
        n_jobs : int, optional
            Number of jobs to run in parallel. default: 1
                1 is no parallelization. -1 uses all available cores.

        Notes
        -----
        Data is optional if data has been already been added to FOOOF object.
        """

        self.fit(freqs, psds, freq_range, n_jobs=n_jobs)
        self.plot()
        self.print_results()


    def fit(self, freqs=None, psds=None, freq_range=None, n_jobs=1):
        """Run FOOOF across a group of PSDs.

        Parameters
        ----------
        freqs : 1d array, optional
            Frequency values for the PSDs, in linear space.
        psds : 2d array, optional
            Matrix of PSD values, in linear space. Shape should be [n_psds, n_freqs].
        freq_range : list of [float, float], optional
            Desired frequency range to run FOOOF on. If not provided, fits the entire given range.
        n_jobs : int, optional
            Number of jobs to run in parallel. default: 1
                1 is no parallelization. -1 uses all available cores.

        Notes
        -----
        Data is optional if data has been already been added to FOOOF object.
        """

        # If freqs & psd provided together, add data to object.
        if isinstance(freqs, np.ndarray) and isinstance(psds, np.ndarray):
            self.add_data(freqs, psds, freq_range)

        # Run linearly
        if n_jobs == 1:
            self._reset_group_results(len(self.psds))
            for ind, psd in enumerate(self.psds):
                self._fit(psd=psd)
                self.group_results[ind] = self._get_results()

        # Run in parallel
        else:
            self._reset_group_results()
            n_jobs = cpu_count() if n_jobs == -1 else n_jobs
            pool = Pool(processes=n_jobs)
            self.group_results = pool.map(partial(_par_fit, fg=self), self.psds)
            pool.close()

        self._reset_data(clear_freqs=False)


    def get_results(self):
        """Return the results run across a group of PSDs."""

        return self.group_results


    def get_all_data(self, name, ind=None):
        """Return all data for a specified attribute across the group.

        Parameters
        ----------
        name : str
            Name of the data field to extract across the group.
        ind : int, optional
            Column index to extract from selected data, if requested.

        Returns
        -------
        out : ndarray
            Requested data.
        """

        # Pull out the requested data field from the group data
        out = np.array([getattr(data, name) for data in self.group_results])

        # Some data can end up as a list of separate arrays.
        #   If so, concatenate it all into one 2d array
        if isinstance(out[0], np.ndarray):
            out = np.concatenate([arr.reshape(1, len(arr)) \
                if arr.ndim == 1 else arr for arr in out], 0)

        # Select out a specific column, if requested
        if ind is not None:
            out = out[:, ind]

        return out


    def plot(self, save_fig=False, file_name='FOOOF_group_fit', file_path=''):

        plot_fg(self, save_fig, file_name, file_path)


    def create_report(self, file_name='FOOOFGroup_Report', file_path=''):

        create_report_fg(self, file_name, file_path)


    def save(self, file_name='fooof_group_results', file_path='', append=False,
             save_results=False, save_settings=False, save_data=False):

        save_fg(self, file_name, file_path, append, save_results, save_settings, save_data)


    def load(self, file_name='fooof_group_results', file_path=''):
        """Load FOOOFGroup data from file, reconstructing the group_results.

        Parameters
        ----------
        file_name : str, optional
            File from which to load data.
        file_path : str, optional
            Path to directory from which to load from. If not provided, saves to current directory.
        """

        # Clear results so as not to have possible prior results interfere
        self._reset_group_results()

        for ind, data in enumerate(load_jsonlines(file_name, file_path)):

            self._add_from_dict(data)

            # Only load settings from first line (rest will be duplicates, if there)
            if ind == 0:
                self._check_loaded_settings(data)

            self._check_loaded_results(data, False)
            self.group_results.append(self._get_results())

        # Reset peripheral data from last loaded result, keeping freqs info
        self._reset_data(False)


    def get_fooof(self, ind, regenerate=False):
        """Return a FOOOF object from specified PSD / model in a FOOOFGroup object.

        Parameters
        ----------
        ind : int
            The index of the FOOOFResult in FOOOFGroup.group_results to load.
        regenerate : bool, optional
            Whether to regenerate the model fits from the given fit parameters. default : False

        Returns
        -------
        inst : FOOOF() object
            The FOOOFResult data loaded into a FOOOF object.
        """

        # Initialize a FOOOF object, with same settings as current FOOOFGroup
        fm = FOOOF(self.bandwidth_limits, self.max_n_oscs, self.min_amp,
                   self.amp_std_thresh, self.bg_use_knee, self.verbose)

        # Add data for specified single PSD, if available
        #  The PSD is inverted back to linear, as it's re-logged when added to FOOOF
        if np.any(self.psds):
            fm.add_data(self.freqs, np.power(10, self.psds[ind]))

        # Add results for specified PSD, regenerating full fit if requested
        fm.add_results(self.group_results[ind], regenerate=regenerate)

        return fm


    def print_results(self):
        """Print out FOOOFGroup results."""

        print(gen_results_str_fg(self))


    def _fit(self, *args, **kwargs):
        """Create an alias to FOOOF.fit for FOOOFGroup object, for internal use."""

        super().fit(*args, **kwargs)


    def _get_results(self):
        """Create an alias to FOOOF.get_results for FOOOFGroup object, for internal use."""

        return super().get_results()

    def _check_bw(self):
        """Check and warn about bandwidth limits / frequency resolution interaction."""

        # Only check & warn on first PSD (to avoid spamming stdout for every PSD)
        if self.psds[0, 0] == self.psd[0]:
            super()._check_bw()


# DOCS: Copy over docs from FOOOF to FOOOFGroup
FOOOFGroup.__doc__ = FOOOF.__doc__

# DOCS: Copy over docs for an aliased functions to the method docstrings
for func_name in get_obj_desc()['alias_funcs']:
    getattr(FOOOFGroup, func_name).__doc__ = \
        docs_drop_param(eval(func_name + '_' + 'fg').__doc__)


# Helper Functions
def _par_fit(psd, fg):
    """Helper function for running in parallel."""

    fg._fit(psd=psd)
    return fg._get_results()
