"""Define model parameters object."""

import numpy as np

from specparam.modes.mode import Mode

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
        Parameters for the aperiodic component of the model fit.
    periodic : ComponentParameters
        Parameters for the periodic component of the model fit.
    """

    def __init__(self, modes=None):
        """Initialize ModelParameters object."""

        self.aperiodic = ComponentParameters(modes.aperiodic if modes else 'aperiodic')
        self.periodic = ComponentParameters(modes.periodic if modes else 'periodic')


    def reset(self):
        """Reset component parameter definitions."""

        self.aperiodic.reset()
        self.periodic.reset()


    def asdict(self):
        """"Export model parameters to a dictionary.

        Returns
        -------
        dict
            Exported dictionary of the model parameters.
        """

        apdict = self.aperiodic.asdict()
        pedict = self.periodic.asdict()

        return {**apdict, **pedict}


class ComponentParameters():
    """Object to manage parameters for a particular model component.

    Parameters
    ----------
    component : str or Mode
        Component that the parameters reflect.
        If Mode, includes a definition of the component fit mode.
        If str, should be a label to use for the component.
    """

    def __init__(self, component):
        """Initialize ComponentParameters object."""

        self._fit = np.nan
        self._converted = np.nan

        self.n_params = None
        self.ndim = None
        self.indices = {}

        if isinstance(component, Mode):
            self.component = component.component
            self.n_params = component.n_params
            self.ndim = component.ndim
            self.add_indices(component.params.indices)
            self.reset()

        else:
            self.component = component


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
    def has_params(self):
        """"Property attribute for checking if any params are avaialble."""

        return self.has_fit


    @property
    def params(self):
        """Property attribute to return parameters.

        Notes
        -----
        If available, this returns converted parameters. If not, this returns fit parameters.
        """

        return self.get_params('converted' if self.has_converted else 'fit')


    def reset(self):
        """Reset parameter stores."""

        if self.n_params:
            self._fit = np.array([np.nan] * self.n_params, ndmin=self.ndim)
            self._converted = np.array([np.nan] * self.n_params, ndmin=self.ndim)
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

        if version is None:
            output = self.params
        if version == 'fit':
            output = self._fit
        if version == 'converted':
            output = self._converted

        if field is not None:
            ind = self.indices[field.lower()] if isinstance(field, str) else field
            output = output[ind] if output.ndim == 1 else output[:, ind]

        return output


    def asdict(self):
        """Get the parameter values in a dictionary.

        Returns
        -------
        dict
            Parameter values from object in a dictionary.
        """

        # TEMP
        label = 'peak' if self.component == 'periodic' else self.component

        outdict = {
            label + '_fit' : self._fit,
            label + '_converted' : self._converted,
        }

        return outdict
