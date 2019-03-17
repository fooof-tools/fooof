"""Oscillation band defintion object for OM."""

from collections import OrderedDict

import numpy as np

###################################################################################################
###################################################################################################

class Bands(object):
    """Class to hold definitions of oscillation bands.

    Attributes
    ----------
    bands : dict
        Dictionary of band definitions.
    """

    def __init__(self, input_bands=None):
        """Initialize the Bands object.

        Parameters
        ----------
        input_bands : dict, optional (default = None)
            A dictionary of oscillation bands to use.
        """

        self.bands = OrderedDict()

        for label, band_def in input_bands.items():
            self.add_band(label)


    def __getitem__(self, name):

        try:
            return self.bands[name]
        except KeyError:
            raise BandNotDefinedError from None


    def __getattr__(self, name):

        return self.__getitem__(name)


    def __repr__(self):

        return '\n'.join(['{:8} :  {:2} - {:2}  Hz'.format(*val) \
            for key, val in self.bands.items()])


    def __len__(self):

        return self.n_bands


    @property
    def labels(self):

        return list(self.bands.keys())


    @property
    def n_bands(self):

        return len(self.bands)


    def add_band(self, label, band_definition):
        """Add a new oscillation band definition.

        Parameters
        ----------
        label : str
            Label of the band to add.
        band_definition : tuple of (float, float)
            The lower and upper frequency limit of the band, in Hz.
        """

        # Check that band definition is properly formatted & add if so
        _check_band(label, band_definition)
        self.bands[label] = band_definition


    def remove_band(self, label):
        """Remove a previously defined oscillation band.

        Parameters
        ----------
        label : str
            Band label to remove from band definitions.
        """

        self.bands.pop(rm_band)


    @staticmethod
    def _check_band(label, band_definition):
        """Check that a proposed band definition is properly formatted.

        Parameters
        ----------
        label : str
            The name of the new oscillation band.
        band_definition : tuple of (float, float)
            The lower and upper frequency limit of the band, in Hz.

        Raises
        ------
        InconsistentDataError
            If oscillation band definition is not properly formatted.
        """

        # Check that band name is a string
        if not isinstance(label, str):
            raise InconsistentDataError('Band name definition is not a string.')

        # Check that band limits has the right size
        if not len(band_definition) == 2:
            raise InconsistentDataError('Band limit definition is not the right size.')

        # Safety check that limits are in correct order
        if not band_definition[0] < band_definition[1]:
            raise InconsistentDataError('Band limits are incorrect.')


class BandNotDefinedError(Exception):
    pass

class InconsistentDataError(Exception):
    pass
