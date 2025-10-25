"""Define model parameters object."""

import numpy as np

###################################################################################################
###################################################################################################

class ModelParameters():
    """Object to manage model fit parameters.

    Parameters
    ----------
    modes : Modes
        Fit modes defintion.
        If provided, used to initialize parameter arrays to correct sizes.

    Attributes
    ----------
    aperiodic : 1d array
        Aperiodic parameters of the model fit.
    peak : 1d array
        Peak parameters of the model fit.
    gaussian : 1d array
        Gaussian parameters of the model fit.
    """

    def __init__(self, modes=None):
        """Initialize ModelParameters object."""

        self.aperiodic = np.nan

        self.peak = np.nan
        self.gaussian = np.nan

        self.reset(modes)

    def reset(self, modes=None):
        """Reset parameters."""

        # Aperiodic parameters
        if modes:
            self.aperiodic = np.array([np.nan] * modes.aperiodic.n_params)
        else:
            self.aperiodic = np.nan

        # Periodic parameters
        if modes:
            self.gaussian = np.empty([0, modes.periodic.n_params])
            self.peak = np.empty([0, modes.periodic.n_params])
        else:
            self.gaussian = np.nan
            self.peak = np.nan


    @property
    def fields(self):
        """Alias as a property attribute the list of fields."""

        return list(vars(self).keys())


class ComponentParameters():
    """Object to manage parameters for a particular model component.

    Parameters
    ----------
    component : {'periodic', 'aperiodic'}
        xx
    mode : str
        xx

    Attributes
    ----------
    XX

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


#     def __getattr__(self, label):

#         if label == self.component:
#             return self.params
#         else:
#             errstr = "'{}' object has no attribute '{}'".format(type(self).__name__, label)
#             raise AttributeError(errstr)

    def _has_param(self, attr):
        """Helper function to check whether

        Paramters
        ---------
        attr : {'fit', 'converted'}
            xx

        Returns
        -------
        bool
            XX

        Notes
        -----
        Return of False can indicate either that the attr is uninitialized (singular
        nan value), or that it is initialized but has no values (an array of nan).
        """

        return True if not np.all(np.isnan(getattr(self, attr))) else False

    @property
    def has_fit(self):
        """   """

        return self._has_param('_fit')

    @property
    def has_converted(self):
        """   """

        return self._has_param('_converted')

#     @property
#     def has_params(self):
#         """   """

#         return self._has_param('params')

    @property
    def params(self):
        """   """

        return self.get_params('converted' if self.has_converted else 'fit')

    def initialize(self, n_params):
        """Initialize

        Parameters
        ----------
        n_params : int
            The number of parameters to initialize.
        """

        self._fit = np.array([np.nan] * n_params)
        self._converted = np.array([np.nan] * n_params)

    def add_indices(self, indices):
        """   """

        self.indices = indices

    def add_params(self, params, version):
        """   """

        if version == 'fit':
            self._fit = params
        if version == 'converted':
            self._converted = params

    def get_params(self, version, field=None):
        """   """

        if version == 'fit':
            output = self._fit
        if version == 'converted':
            output = self._converted

        if field is not None:
            ind = self.indices[field] if isinstance(field, str) else field
            output = output[ind] if output.ndim == 1 else output[:, ind]

        return output

    def asdict(self):
        """   """

        outdict = {
            self.component + '_fit' : self._fit,
            self.component + '_converted' : self._converted,
        }

        return outdict


#     @property
#     def fields(self):
#         """Alias as a property attribute the list of fields."""

#         return list(vars(self).keys())


#     def asdict(self):
#         return dict(self)


#     def __iter__(self):
#         """   """

#         yield self.component + '_fit', self._fit,
#         yield self.component + '_converted', self._converted


#        Alternate version of checking has attr that supports None
#         attr_val = getattr(self, attr)

#         if attr_val is None:
#             answer = False
#         elif isinstance(attr_val, np.ndarray) and np.all(np.isnan(attr_val)):
#             answer = False
#         else:
#             answer = True

#         return answer
