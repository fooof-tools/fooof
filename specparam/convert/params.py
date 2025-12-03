"""Conversion functions for specific parameters."""

import numpy as np

from specparam.utils.select import nearest_ind

###################################################################################################
###################################################################################################

## PARAMETER CONVERTERS

PEAK_HEIGHT_OPERATIONS = {
    'subtract' : np.subtract,
    'divide' : np.divide,
}

def compute_peak_height(model, peak_ind, spacing, operation):
    """Compute peak heights, based on specified approach & spacing.

    Parameters
    ----------
    model : SpectralModel
        Model object, post fitting.
    peak_ind : int
        Index of which peak to compute height for.
    spacing : {'log', 'linear'}
        Spacing to extract the data components in.
    operation : {'subtract', 'divide'}
        Approach to take to compute the peak height measure.

    Returns
    -------
    peak_height : float
        Computed peak height.
    """

    ind = nearest_ind(model.data.freqs, model.results.params.periodic._fit[\
                          peak_ind, model.modes.periodic.params.indices['cf']])
    peak_height = PEAK_HEIGHT_OPERATIONS[operation](\
        model.results.model.get_component('full', spacing)[ind],
        model.results.model.get_component('aperiodic', spacing)[ind])

    return peak_height
