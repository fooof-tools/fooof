"""FOOOF - Group fitting object and methods."""

import os
from json import JSONDecodeError
from multiprocessing import Pool, cpu_count

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
from functools import partial

from fooof import FOOOF
from fooof.strings import gen_results_str_fg
from fooof.plts import plot_scatter_1, plot_scatter_2, plot_hist

###################################################################################################
###################################################################################################

class FOOOFGroup(FOOOF):

    def __init__(self, *args, **kwargs):

        FOOOF.__init__(self, *args, **kwargs)

        self.psds = np.array([])

        self._reset_group_results()


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
        n_jobs : int
            Number of jobs to run in parallel. 1 is no parallelization. -1 indicates to use all cores.

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
            Number of jobs to run in parallel. 1 is no parallelization. -1 indicates to use all cores.

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

        self._reset_dat(clear_freqs=False)


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
        out = np.array([getattr(dat, name) for dat in self.group_results])

        # Some data can end up as a list of separate arrays. If so, concatenate it all into one 2d array
        if isinstance(out[0], np.ndarray):
            out = np.concatenate([arr.reshape(1, len(arr)) if arr.ndim == 1 else arr for arr in out], 0)

        # Select out a specific column, if requested
        if ind is not None:
            out = out[:, ind]

        return out


    def plot(self, save_fig=False, save_name='FOOOF_fit', save_path=''):
        """Plot a multiplot figure of several aspects of the group data.

        Parameters
        ----------
        save_fig : boolean, optional
            Whether to save out a copy of the plot. default : False
        save_name : str, optional
            Name to give the saved out file.
        save_path : str, optional
            Path to directory in which to save. If not provided, saves to current directory.
        """

        fig = plt.figure(figsize=(14, 10))
        gs = gridspec.GridSpec(2, 2, wspace=0.35, hspace=0.25, height_ratios=[1, 1.2])

        # Background parameters plot
        ax0 = plt.subplot(gs[0, 0])
        self._plot_bg(ax0)

        # Goodness of fit plot
        ax1 = plt.subplot(gs[0, 1])
        self._plot_gd(ax1)

        # Oscillations plot
        ax2 = plt.subplot(gs[1, :])
        self._plot_osc_cens(ax2)

        if save_fig:
            plt.savefig(os.path.join(save_path, save_name + '.png'))


    def create_report(self, save_name='FOOOFGroup_Report', save_path=''):
        """Generate and save out a report for the FOOOF Group results.

        Parameters
        ----------
        save_name : str, optional
            Name to give the saved out file.
        save_path : str, optional
            Path to directory in which to save. If not provided, saves to current directory.
        """

        # Set the font description for saving out text with matplotlib
        font = {'family': 'monospace',
                'weight': 'normal',
                'size': 16}

        # Initialize figure
        fig = plt.figure(figsize=(16, 20))
        gs = gridspec.GridSpec(3, 2, wspace=0.35, hspace=0.25, height_ratios=[1.5, 1.0, 1.2])

        # First / top: text results
        ax0 = plt.subplot(gs[0, :])
        #results_str = self._gen_results_str()
        results_str = gen_results_str_fg(self)
        ax0.text(0.5, 0.0, results_str, font, ha='center')
        ax0.set_frame_on(False)
        ax0.set_xticks([])
        ax0.set_yticks([])

        # Background parameters plot
        ax1 = plt.subplot(gs[1, 0])
        self._plot_bg(ax1)

        # Goodness of fit plot
        ax2 = plt.subplot(gs[1, 1])
        self._plot_gd(ax2)

        # Oscillations plot
        ax3 = plt.subplot(gs[2, :])
        self._plot_osc_cens(ax3)

        # Save out the report
        plt.savefig(os.path.join(save_path, save_name + '.pdf'))
        plt.close()


    def save(self, save_file='fooof_group_results', save_path='', save_results=False, save_settings=False):
        """Save out results and/or settings from FOOOFGroup object. Saves out to a JSON file.

        Notes
        -----
        - save_data is not availabe with FOOOFGroup, as data are not stored after fitting.
        """

        if save_results:
            with open(os.path.join(save_path, save_file + '.json'), 'w') as f_obj:
                for ind in range(len(self.group_results)):
                    fm = FOOOF.from_group(self, ind, regenerate=False)
                    fm.save(save_file=f_obj, save_results=True, save_settings=save_settings)

        if save_settings:
            self._save(save_file=save_file, save_path=save_path, save_settings=True)


    def load(self, file_name='fooof_group_results', file_path=''):
        """Load FOOOFGroup data from file, reconstructing the group_results.

        Parameters
        ----------
        file_name : str
            File from which to load data.
        file_path : str, optional
            Path to directory from which to load from. If not provided, saves to current directory.
        """

        # Clear results so as not to have possible prior results interfere
        self._reset_group_results()

        # Load from jsonlines file
        with open(os.path.join(file_path, file_name + '.json'), 'r') as f_obj:

            while True:

                # For each line, grab the FOOOFResults
                try:
                    self._load(f_obj)
                    self.group_results.append(self._get_results())

                # Break off when get a JSON error - end of the file
                except JSONDecodeError:
                    break

        # Reset peripheral data from last loaded result, keeping freqs info
        self._reset_dat(False)


    def from_group(self, ind, regenerate=False):
        """Return a FOOOF object from specified data in a FOOOFGroup object.

        Parameters
        ----------
        fg : FOOOFGroup() object
            An object with FOOOFResults available.
        ind : int
            The index of the FOOOFResult in FOOOFGroup.group_results to load.

        Returns
        -------
        inst : FOOOF() object
            The FOOOFResult data loaded into a FOOOF object.

        Notes
        -----
        - This method overloads what is a classmethod in FOOOF object base.
        """

        # Initialize a FOOOF object, with same settings as current FOOOFGroup
        fm = FOOOF(self.bandwidth_limits, self.max_n_oscs, self.min_amp,
                   self.amp_std_thresh, self.bg_use_knee, self.verbose)

        # Add data and results for specified single PSD
        #  Note that the PSD is inverted back to linear,
        #    as it will be logged (again) within the method
        fm.add_data(self.freqs, np.power(10, self.psds[ind]))
        fm.add_results(self.group_results[ind], regenerate=regenerate)

        return fm

    def print_results(self):

        print(gen_results_str_fg(self))


    def _fit(self, *args, **kwargs):
        """Create an alias to FOOOF.fit for FOOOFGroup object, for internal use."""

        super().fit(*args, **kwargs)


    def _get_results(self):
        """Create an alias to FOOOF.get_results for FOOOFGroup object, for internal use."""

        return super().get_results()


    def _save(self, *args, **kwargs):
        """Create an alias to FOOOF.save for FOOOFGroup object, for internal use."""

        super().save(*args, **kwargs)


    def _load(self, *args, **kwargs):
        """Create an alias to FOOOF.load for FOOOFGroup object, for internal use."""

        super().load(*args, **kwargs)


    def _plot_bg(self, ax=None):
        """Plot background fit parameters, in a scatter plot.

        Parameters
        ----------
        ax : matplotlib.Axes, optional
            Figure axes upon which to plot.
        """

        if self.bg_use_knee:
            plot_scatter_2(self.get_all_data('background_params', 1), 'Knee',
                           self.get_all_data('background_params', 2), 'Slope',
                           'Background Fit', ax=ax)
        else:
            plot_scatter_1(self.get_all_data('background_params', 1), 'Slope',
                           'Background Fit', ax=ax)


    def _plot_gd(self, ax=None):
        """Plot goodness of fit results, in a scatter plot.

        Parameters
        ----------
        ax : matplotlib.Axes, optional
            Figure axes upon which to plot.
        """

        plot_scatter_2(self.get_all_data('error'), 'Error',
                       self.get_all_data('r2'), 'R^2', 'Goodness of Fit', ax=ax)


    def _plot_osc_cens(self, ax=None):
        """Plot oscillation center frequencies, in a histogram.

        Parameters
        ----------
        ax : matplotlib.Axes, optional
            Figure axes upon which to plot.
        """

        plot_hist(self.get_all_data('oscillation_params', 0),
                  'Center Frequency', 'Oscillations', ax=ax)


FOOOFGroup.__doc__ = FOOOF.__doc__


def _par_fit(psd, fg):
    """Helper function for running in parallel."""

    fg._fit(psd=psd)
    return fg._get_results()
