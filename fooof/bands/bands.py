"""A data oject for managing band definitions."""

from collections import OrderedDict

###################################################################################################
###################################################################################################

class Bands():
    """Frequency band definitions.

    Attributes
    ----------
    bands : dict
        Band definitions. Each entry should be {'label' : (f_low, f_high)}.

    Examples
    --------
    Define a bands object storing canonical frequency bands:

    >>> bands = Bands({'theta' : [4, 8], 'alpha' : [8, 12], 'beta' : [15, 30]})
    """

    def __init__(self, input_bands={}):
        """Initialize the Bands object.

        Parameters
        ----------
        input_bands : dict, optional
            A dictionary of oscillation bands.
        """

        self.bands = OrderedDict()

        for label, band_def in input_bands.items():
            self.add_band(label, band_def)

    def __getitem__(self, label):
        """Define indexing as returning the definition of a requested band label."""

        try:
            return self.bands[label]
        except KeyError:
            message = "The label '{}' was not found in the defined bands.".format(label)
            raise ValueError(message) from None

    def __getattr__(self, label):
        """Define getting an attribute as returning the definition of a requested band label."""

        return self.__getitem__(label)

    def __repr__(self):
        """Define the string representation as a printout of the band information."""

        return '\n'.join(['{:8} :  {:2} - {:2}  Hz'.format(key, *val) \
            for key, val in self.bands.items()])

    def __len__(self):
        """Define length as the number of bands it contains."""

        return self.n_bands

    def __iter__(self):
        """Define iteratation as stepping across each band."""

        for label, band_definition in self.bands.items():
            yield (label, band_definition)

    @property
    def labels(self):
        """Labels for all the bands defined in the object."""

        return list(self.bands.keys())


    @property
    def definitions(self):
        """Frequency definitions for all the bands defined in the object."""

        return list(self.bands.values())


    @property
    def n_bands(self):
        """The number of bands defined in the object."""

        return len(self.bands)


    def add_band(self, label, band_definition):
        """Add a new oscillation band definition.

        Parameters
        ----------
        label : str
            Band label to add.
        band_definition : tuple of (float, float)
            The lower and upper frequency limit of the band, in Hz.
        """

        self._check_band(label, band_definition)
        self.bands[label] = band_definition


    def remove_band(self, label):
        """Remove a previously defined oscillation band.

        Parameters
        ----------
        label : str
            Band label to remove from band definitions.
        """

        self.bands.pop(label)


    @staticmethod
    def _check_band(label, band_definition):
        """Check that a proposed band definition is valid.

        Parameters
        ----------
        label : str
            The name of the new band.
        band_definition : tuple of (float, float)
            The lower and upper frequency limit of the band, in Hz.

        Raises
        ------
        ValueError
            If band definition is not properly formatted.
        """

        # Check that band name is a string
        if not isinstance(label, str):
            raise ValueError("Band name definition is not a string.")

        # Check that band limits has the right size
        if not len(band_definition) == 2:
            raise ValueError("Band limit definition is not the right size.")

        # Safety check that limits are in correct order
        if not band_definition[0] < band_definition[1]:
            raise ValueError("Band limit definitions are invalid.")
