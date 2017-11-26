"""FOOOF - Group fitting object and methods."""

import os
import numpy as np
from json import JSONDecodeError

from fooof import FOOOF

###################################################################################################
###################################################################################################

class FOOOFGroup(FOOOF):

    def __init__(self, *args, **kwargs):

        FOOOF.__init__(self, *args, **kwargs)

        self._reset_group_results()


    def _reset_group_results(self):
        """Set (or reset) results to be empty."""

        self.group_results = []


    def fit_group(self, freqs, psds, freq_range=None, save_dat=False, file_name='fooof_group_results', file_path=''):
        """Run FOOOF across a group of PSDs.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the PSDs, in linear space.
        psds : 2d array
            Matrix of PSD values, in linear space. Shape should be [n_psds, n_freqs].
        freq_range : list of [float, float], optional
            Desired frequency range to run FOOOF on. If not provided, fits the entire given range.
        save_dat : bool, optional
            Whether to save data out to file while running. Default: False.
        file_name : str, optional
            File name to save to.
        file_path : str, optional
            Path to directory in which to save. If not provided, saves to current directory.
        """

        # Clear results so that any prior data doesn't end up lumped together
        self._reset_group_results()

        # If saving, open a file to save to
        if save_dat:
            f_obj = open(os.path.join(file_path, file_name + '.json'), 'w')

        # Fit FOOOF across matrix of PSDs.
        #  Note: shape checking gets performed in fit - wrong shapes/orientations will fail there.
        for psd in psds:
            self.fit(freqs, psd, freq_range)
            self.group_results.append(self.get_results())
            if save_dat:
                self.save(f_obj, save_results=True)

        # Clear out last run PSD, but while keeping frequency information
        #  This is so that it doesn't retain data from an arbitrary PSD
        self._reset_dat(False)

        # If savine, close file
        if save_dat:
            f_obj.close()


    def get_group_results(self):
        """Return the results run across a group of PSDs."""

        return self.group_results


    def load_group_results(self, file_name='fooof_group_results', file_path=''):
        """Load data from file, reconstructing the group_results.

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
                    self.load(f_obj)
                    self.group_results.append(self.get_results())

                # Break off when get a JSON error - end of the file
                except JSONDecodeError:
                    break

        # Reset peripheral data from last loaded result, keeping freqs info
        self._reset_dat(False)


FOOOFGroup.__doc__ = FOOOF.__doc__
