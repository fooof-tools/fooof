"""Define model parameters object."""

import numpy as np

###################################################################################################
###################################################################################################

class ModelParameters():
    """Object to manage model fit parameters.

    Parameters
    ----------
    modes : Modes
        Fit modes definition.
        If provided, used to initialize parameter arrays to correct sizes.

    Attributes
    ----------
    aperiodic : ComponentParameters
        Aperiodic parameters of the model fit.
    peak : ComponentParameters
        Peak parameters of the model fit.
    """

    def __init__(self, modes=None):
        """Initialize ModelParameters object."""

        self.aperiodic = ComponentParameters('aperiodic')
        self.peak = ComponentParameters('periodic')

        self.reset(modes)


    def reset(self, modes=None):
        """Reset component parameter definitions."""

        self.aperiodic.reset(modes.aperiodic.n_params if modes else None)
        self.peak.reset(modes.periodic.n_params if modes else None)


    @property
    def fields(self):
        """Alias as a property attribute the list of fields."""

        return list(vars(self).keys())


class ComponentParameters():
    """Object to manage parameters for a particular model component.

    Parameters
    ----------
    component : {'periodic', 'aperiodic'}
        Description of which kind of component parameters are for.
    mode : Mode, optional
        Mode object description the component fit mode.
    """

    def __init__(self, component, mode=None):
        """Initialize ComponentParameters object."""

        self._fit = np.nan
        self._converted = np.nan

        self.indices = {}

        assert component in ['aperiodic', 'periodic'], "Component does not match expected names."
        self.component = component

        if mode is not None:
            assert mode.component == component, 'Given mode does not match component'
            self.initialize(mode.n_params)
            self.add_indices(mode.params.indices)


    def _has_param(self, version):
        """Helper function to check whether the object has parameter values.

        Parameters
        ----------
        version : {'fit', 'converted'}
            Which version of the parameters to check for.

        Returns
        -------
        bool
            Whether the object has the specified type of parameter values.

        Notes
        -----
        Return of False can indicate either that the specified params attribute is uninitialized
        (singular nan value), or that it is initialized but has no values (an array of nan).
        """

        return True if not np.all(np.isnan(getattr(self, version))) else False


    @property
    def has_fit(self):
        """Property attribute for checking if object has fit parameters."""

        return self._has_param('_fit')


    @property
    def has_converted(self):
        """Property attribute for checking if object has converted parameters."""

        return self._has_param('_converted')


    @property
    def params(self):
        """Property attribute to return parameters.

        Notes
        -----
        If available, this return converted parameters. If not, this returns fit parameters.
        """

        return self.get_params('converted' if self.has_converted else 'fit')


    def reset(self, n_params=None):
        """Reset parameter stores, optional specifying a specified size.

        Parameters
        ----------
        n_params : int, optional
            The number of parameters to initialize.
        """

        if n_params:
            self._fit = np.array([np.nan] * n_params)
            self._converted = np.array([np.nan] * n_params)
        else:
            self._fit = np.nan
            self._converted = np.nan


    def add_indices(self, indices):
        """Add parameter indices definition to the object."""

        self.indices = indices


    def add_params(self, version, params):
        """Add parameter values to the object.

        Parameters
        ----------
        version : {'fit', 'converted'}
            Which version of the parameters to return.
        params : array
            Parameter values to add to the object.
        """

        if version == 'fit':
            self._fit = params
        if version == 'converted':
            self._converted = params


    def get_params(self, version, field=None):
        """Get parameter values from the object.

        Parameters
        ----------
        version : {'fit', 'converted'}
            Which version of the parameters to return.
        field : str, optional
            Which field from the parameters to return.

        Returns
        -------
        params : array
            Extracted parameter values.
        """

        if version == 'fit':
            output = self._fit
        if version == 'converted':
            output = self._converted

        if field is not None:
            ind = self.indices[field] if isinstance(field, str) else field
            output = output[ind] if output.ndim == 1 else output[:, ind]

        return output


    def asdict(self):
        """Get the parameter values in a dictionary.

        Returns
        -------
        dict
            Parameter values from object in a dictionary.
        """

        outdict = {
            self.component + '_fit' : self._fit,
            self.component + '_converted' : self._converted,
        }

        return outdict
