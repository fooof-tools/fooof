"""FOOOF - Group fitting object and methods."""

from fooof import FOOOF

###################################################################################################
###################################################################################################

class FOOOFGroup(FOOOF):

    def __init__(self, *args, **kwargs):

        FOOOF.__init__(self, *args, **kwargs)

        self.group_results = []


    def fit_group(self, freqs, psds, freq_range=None):
        """Run FOOOF across a group of PSDs.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the PSDs, in linear space.
        psds : 2d array
            Matrix of PSD values, in linear space. Shape should be [n_psds, n_freqs].
        freq_range : list of [float, float], optional
            Desired frequency range to run FOOOF on. If not provided, fits the entire given range.
        """

        # Fit FOOOF across matrix of PSDs.
        #  Note: shape checking gets performed in fit - wrong shapes/orientations will fail there.
        for psd in psds:
            self.fit(freqs, psd, freq_range)
            self.group_results.append(self.get_results())

        # Clear out last run PSD (so it doesn't have data from an arbitrary PSD)
        self._reset_dat()


    def get_group_results(self):
        """Return the results run across a group of PSDs."""

        return self.group_results


FOOOFGroup.__doc__ = FOOOF.__doc__