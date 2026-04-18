""""Generate text."""

from specparam.version import __version__ as MODULE_VERSION

###################################################################################################
###################################################################################################

def gen_methods_text(model=None):
    """Generate a string representation of a template methods report.

    Parameters
    ----------
    model : SpectralModel or Spectral*Model, optional
        A model object with settings information available.
        If None, the text is returned as a template, without values.

    Returns
    -------
    str
        Formatted string of a template methods report.
    """

    if model:
        settings_names = list(model.algorithm.settings.values.keys())
        settings_values = list(model.algorithm.settings.values.values())
    else:
        settings_names = []
        settings_values = []

    template = [
        "The periodic & aperiodic spectral parameterization algorithm (version {}) "
        "was used to parameterize neural power spectra. "
        "The model was fit with {} aperiodic mode and {} periodic mode. "
        "Settings for the algorithm were set as: "
    ]

    if settings_names:
        settings_strs = [el + ' : {}, ' for el in settings_names]
        settings_strs[-1] = settings_strs[-1][:-2] + '. '
        template.extend(settings_strs)
    else:
        template.extend('XX. ')

    template.extend([
        "Power spectra were parameterized across the frequency range "
        "{} to {} Hz."
    ])

    if model and model.data.has_data:
        freq_range = model.data.freq_range
    else:
        freq_range = ('XX', 'XX')

    methods_str = ''.join(template).format(\
        MODULE_VERSION,
        model.modes.aperiodic.name if model else 'XX',
        model.modes.periodic.name if model else 'XX',
        *settings_values,
        *freq_range)

    return methods_str
