"""Formatted strings for printing out model and fit related information."""

import numpy as np

from specparam.modutils.errors import NoModelError
from specparam.data.utils import get_periodic_labels
from specparam.utils.array import compute_arr_desc
from specparam.measures.properties import compute_presence
from specparam.version import __version__ as MODULE_VERSION

###################################################################################################
###################################################################################################

## Settings & Globals
# Centering Value - Long & Short options
#   Note: Long CV of 98 is so that the max line length plays nice with notebook rendering
LCV = 98
SCV = 70

###################################################################################################
###################################################################################################

def gen_width_warning_str(freq_res, bwl):
    """Generate a string representation of the warning about peak width limits.

    Parameters
    ----------
    freq_res : float
        Frequency resolution.
    bwl : float
        Lower bound peak width limit.

    Returns
    -------
    output : str
        Formatted string of a warning about the peak width limits setting.
    """

    output = '\n'.join([
        '',
        'WARNING: Lower-bound peak width limit is < or ~= the frequency resolution: ' + \
        '{:1.2f} <= {:1.2f}'.format(bwl, freq_res),
        '\tLower bounds below frequency-resolution have no effect ' + \
        '(effective lower bound is the frequency resolution).',
        '\tToo low a limit may lead to overfitting noise as small bandwidth peaks.',
        '\tWe recommend a lower bound of approximately 2x the frequency resolution.',
        ''
    ])

    return output


def gen_version_str(concise=False):
    """Generate a string representation of the current version of the module.

    Parameters
    ----------
    concise : bool, optional, default: False
        Whether to print the report in concise mode.

    Returns
    -------
    output : str
        Formatted string of current version.
    """

    str_lst = [

        # Header
        '=',
        '',
        'specparam - VERSION',
        '',

        # Version information
        '{}'.format(MODULE_VERSION),

        # Footer
        '',
        '='

    ]

    output = _format(str_lst, concise)

    return output


def gen_settings_str(model_obj, description=False, concise=False):
    """Generate a string representation of current fit settings.

    Parameters
    ----------
    model_obj : SpectralModel or SpectralGroupModel or ModelSettings
        Object to access settings from.
    description : bool, optional, default: True
        Whether to also print out a description of the settings.
    concise : bool, optional, default: False
        Whether to print the report in concise mode.

    Returns
    -------
    output : str
        Formatted string of current settings.
    """

    # Parameter descriptions to print out, if requested
    desc = {
        'peak_width_limits' : 'Limits for minimum and maximum peak widths, in Hz.',
        'max_n_peaks'       : 'Maximum number of peaks that can be extracted.',
        'min_peak_height'   : 'Minimum absolute height of a peak, above the aperiodic component.',
        'peak_threshold'    : 'Relative threshold for minimum height required for detecting peaks.',
        'aperiodic_mode'    : 'The approach taken for fitting the aperiodic component.'
        }

    # Clear description for printing, if not requested
    if not description:
        desc = {k : '' for k, v in desc.items()}

    # Create output string
    str_lst = [

        # Header
        '=',
        '',
        'specparam - SETTINGS',
        '',

        # Settings - include descriptions if requested
        *[el for el in ['Peak Width Limits : {}'.format(model_obj.peak_width_limits),
                        '{}'.format(desc['peak_width_limits']),
                        'Max Number of Peaks : {}'.format(model_obj.max_n_peaks),
                        '{}'.format(desc['max_n_peaks']),
                        'Minimum Peak Height : {}'.format(model_obj.min_peak_height),
                        '{}'.format(desc['min_peak_height']),
                        'Peak Threshold: {}'.format(model_obj.peak_threshold),
                        '{}'.format(desc['peak_threshold']),
                        'Aperiodic Mode : {}'.format(model_obj.aperiodic_mode),
                        '{}'.format(desc['aperiodic_mode'])] if el != ''],

        # Footer
        '',
        '='
    ]

    output = _format(str_lst, concise)

    return output


def gen_freq_range_str(model_obj, concise=False):
    """Generate a string representation of the fit range that was used for the model.

    Parameters
    ----------
    model_obj : SpectralModel or SpectralGroupModel
        Object to access settings from.
    concise : bool, optional, default: False
        Whether to print the report in concise mode.

    Notes
    -----
    If fit range is not available, will print out 'XX' for missing values.
    """

    freq_range = model_obj.freq_range if model_obj.has_data else ('XX', 'XX')

    str_lst = [

        # Header
        '=',
        '',
        'specparam - FIT RANGE',
        '',

        # Frequency range information information
        'The model was fit from {} to {} Hz.'.format(*freq_range),

        # Footer
        '',
        '='

    ]

    output = _format(str_lst, concise)

    return output


def gen_methods_report_str(concise=False):
    """Generate a string representation of instructions for reporting on using the module.

    Parameters
    ----------
    concise : bool, optional, default: False
        Whether to print the report in concise mode.

    Returns
    -------
    output : str
        Formatted string of instructions for methods reporting.
    """

    str_lst = [

        # Header
        '=',
        '',
        'specparam - REPORTING',
        '',

        # Methods report information
        'Reports using spectral parameterization should include (at minimum):',
        '',
        '- the code version that was used',
        '- the algorithm settings that were used',
        '- the frequency range that was fit',

        # Footer
        '',
        '='
    ]

    output = _format(str_lst, concise)

    return output


def gen_methods_text_str(model_obj=None):
    """Generate a string representation of a template methods report.

    Parameters
    ----------
    model_obj : SpectralModel or SpectralGroupModel, optional
        A model object with settings information available.
        If None, the text is returned as a template, without values.
    """

    template = (
        "The periodic & aperiodic spectral parameterization algorithm (version {}) "
        "was used to parameterize neural power spectra. Settings for the algorithm were set as: "
        "peak width limits : {}; "
        "max number of peaks : {}; "
        "minimum peak height : {}; "
        "peak threshold : {}; "
        "and aperiodic mode : '{}'. "
        "Power spectra were parameterized across the frequency range "
        "{} to {} Hz."
    )

    if model_obj:
        freq_range = model_obj.freq_range if model_obj.has_data else ('XX', 'XX')
    else:
        freq_range = ('XX', 'XX')

    methods_str = template.format(MODULE_VERSION,
                                  model_obj.peak_width_limits if model_obj else 'XX',
                                  model_obj.max_n_peaks if model_obj else 'XX',
                                  model_obj.min_peak_height if model_obj else 'XX',
                                  model_obj.peak_threshold if model_obj else 'XX',
                                  model_obj.aperiodic_mode if model_obj else 'XX',
                                  *freq_range)

    return methods_str


def gen_model_results_str(model, concise=False):
    """Generate a string representation of model fit results.

    Parameters
    ----------
    model : SpectralModel
        Object to access results from.
    concise : bool, optional, default: False
        Whether to print the report in concise mode.

    Returns
    -------
    output : str
        Formatted string of model results.
    """

    # Returns a null report if no results are available
    if np.all(np.isnan(model.aperiodic_params_)):
        return _no_model_str(concise)

    # Create the formatted strings for printing
    str_lst = [

        # Header
        '=',
        '',
        'POWER SPECTRUM MODEL',
        '',

        # Frequency range and resolution
        'The model was run on the frequency range {} - {} Hz'.format(
            int(np.floor(model.freq_range[0])), int(np.ceil(model.freq_range[1]))),
        'Frequency Resolution is {:1.2f} Hz'.format(model.freq_res),
        '',

        # Aperiodic parameters
        ('Aperiodic Parameters (offset, ' + \
         ('knee, ' if model.aperiodic_mode == 'knee' else '') + \
         'exponent): '),
        ', '.join(['{:2.4f}'] * len(model.aperiodic_params_)).format(*model.aperiodic_params_),
        '',

        # Peak parameters
        '{} peaks were found:'.format(
            len(model.peak_params_)),
        *['CF: {:6.2f}, PW: {:6.3f}, BW: {:5.2f}'.format(op[0], op[1], op[2]) \
          for op in model.peak_params_],
        '',

        # Goodness if fit
        'Goodness of fit metrics:',
        'R^2 of model fit is {:5.4f}'.format(model.r_squared_),
        'Error of the fit is {:5.4f}'.format(model.error_),
        '',

        # Footer
        '='
    ]

    output = _format(str_lst, concise)

    return output


def gen_group_results_str(group, concise=False):
    """Generate a string representation of group fit results.

    Parameters
    ----------
    group : SpectralGroupModel
        Object to access results from.
    concise : bool, optional, default: False
        Whether to print the report in concise mode.

    Returns
    -------
    output : str
        Formatted string of results.

    Raises
    ------
    NoModelError
        If no model fit data is available to report.
    """

    if not group.has_model:
        raise NoModelError("No model fit results are available, can not proceed.")

    # Extract all the relevant data for printing
    n_peaks = len(group.get_params('peak_params'))
    r2s = group.get_params('r_squared')
    errors = group.get_params('error')
    exps = group.get_params('aperiodic_params', 'exponent')
    kns = group.get_params('aperiodic_params', 'knee') \
        if group.aperiodic_mode == 'knee' else np.array([0])

    str_lst = [

        # Header
        '=',
        '',
        'GROUP RESULTS',
        '',

        # Group information
        'Number of power spectra in the Group: {}'.format(len(group.group_results)),
        *[el for el in ['{} power spectra failed to fit'.format(group.n_null_)] if group.n_null_],
        '',

        # Frequency range and resolution
        'The model was run on the frequency range {} - {} Hz'.format(
            int(np.floor(group.freq_range[0])), int(np.ceil(group.freq_range[1]))),
        'Frequency Resolution is {:1.2f} Hz'.format(group.freq_res),
        '',

        # Aperiodic parameters - knee fit status, and quick exponent description
        'Power spectra were fit {} a knee.'.format(\
            'with' if group.aperiodic_mode == 'knee' else 'without'),
        '',
        'Aperiodic Fit Values:',
        *[el for el in ['    Knees - Min: {:6.2f}, Max: {:6.2f}, Mean: {:5.2f}'
                        .format(*compute_arr_desc(kns)),
                       ] if group.aperiodic_mode == 'knee'],
        'Exponents - Min: {:6.3f}, Max: {:6.3f}, Mean: {:5.3f}'
        .format(*compute_arr_desc(exps)),
        '',

        # Peak Parameters
        'In total {} peaks were extracted from the group'
        .format(n_peaks),
        '',

        # Goodness if fit
        'Goodness of fit metrics:',
        '   R2s -  Min: {:6.3f}, Max: {:6.3f}, Mean: {:5.3f}'
        .format(*compute_arr_desc(r2s)),
        'Errors -  Min: {:6.3f}, Max: {:6.3f}, Mean: {:5.3f}'
        .format(*compute_arr_desc(errors)),
        '',

        # Footer
        '='
    ]

    output = _format(str_lst, concise)

    return output


def gen_time_results_str(time_model, concise=False):
    """Generate a string representation of time fit results.

    Parameters
    ----------
    time_model : SpectralTimeModel
        Object to access results from.
    concise : bool, optional, default: False
        Whether to print the report in concise mode.

    Returns
    -------
    output : str
        Formatted string of results.

    Raises
    ------
    NoModelError
        If no model fit data is available to report.
    """

    if not time_model.has_model:
        raise NoModelError("No model fit results are available, can not proceed.")

    # Get parameter information needed for printing
    pe_labels = get_periodic_labels(time_model.time_results)
    band_labels = [\
        pe_labels['cf'][band_ind].split('_')[-1 if pe_labels['cf'][-2:] == 'cf' else 0] \
        for band_ind in range(len(pe_labels['cf']))]
    has_knee = time_model.aperiodic_mode == 'knee'

    str_lst = [

        # Header
        '=',
        '',
        'TIME RESULTS',
        '',

        # Group information
        'Number of time windows fit: {}'.format(len(time_model.group_results)),
        *[el for el in ['{} power spectra failed to fit'.format(time_model.n_null_)] \
            if time_model.n_null_],
        '',

        # Frequency range and resolution
        'The model was run on the frequency range {} - {} Hz'.format(
            int(np.floor(time_model.freq_range[0])), int(np.ceil(time_model.freq_range[1]))),
        'Frequency Resolution is {:1.2f} Hz'.format(time_model.freq_res),
        '',

        # Aperiodic parameters - knee fit status, and quick exponent description
        'Power spectra were fit {} a knee.'.format(\
            'with' if time_model.aperiodic_mode == 'knee' else 'without'),
        '',
        'Aperiodic Fit Values:',
        *[el for el in ['    Knees - Min: {:6.2f}, Max: {:6.2f}, Mean: {:6.2f}'
                        .format(*compute_arr_desc(time_model.time_results['knee']) \
                            if has_knee else [0, 0, 0]),
                       ] if has_knee],
        'Exponents - Min: {:6.3f}, Max: {:6.3f}, Mean: {:5.3f}'
        .format(*compute_arr_desc(time_model.time_results['exponent'])),
        '',

        # Periodic parameters
        'Periodic params (mean values across windows):',
        *['{:>6s} - CF: {:5.2f}, PW: {:5.2f}, BW: {:5.2f}, Presence: {:3.1f}%'.format(
            label,
            np.nanmean(time_model.time_results[pe_labels['cf'][ind]]),
            np.nanmean(time_model.time_results[pe_labels['pw'][ind]]),
            np.nanmean(time_model.time_results[pe_labels['bw'][ind]]),
            compute_presence(time_model.time_results[pe_labels['cf'][ind]], output='percent'))
                for ind, label in enumerate(band_labels)],
        '',

        # Goodness if fit
        'Goodness of fit (mean values across windows):',
        '   R2s -  Min: {:6.3f}, Max: {:6.3f}, Mean: {:5.3f}'
        .format(*compute_arr_desc(time_model.time_results['r_squared'])),
        'Errors -  Min: {:6.3f}, Max: {:6.3f}, Mean: {:5.3f}'
        .format(*compute_arr_desc(time_model.time_results['error'])),
        '',

        # Footer
        '='
    ]

    output = _format(str_lst, concise)

    return output


def gen_event_results_str(event_model, concise=False):
    """Generate a string representation of event fit results.

    Parameters
    ----------
    event_model : SpectralTimeEventModel
        Object to access results from.
    concise : bool, optional, default: False
        Whether to print the report in concise mode.

    Returns
    -------
    output : str
        Formatted string of results.

    Raises
    ------
    NoModelError
        If no model fit data is available to report.
    """

    if not event_model.has_model:
        raise NoModelError("No model fit results are available, can not proceed.")

    # Extract all the relevant data for printing
    pe_labels = get_periodic_labels(event_model.event_time_results)
    band_labels = [\
        pe_labels['cf'][band_ind].split('_')[-1 if pe_labels['cf'][-2:] == 'cf' else 0] \
        for band_ind in range(len(pe_labels['cf']))]
    has_knee = event_model.aperiodic_mode == 'knee'

    str_lst = [

        # Header
        '=',
        '',
        'EVENT RESULTS',
        '',

        # Group information
        'Number of events fit: {}'.format(len(event_model.event_group_results)),
        '',

        # Frequency range and resolution
        'The model was run on the frequency range {} - {} Hz'.format(
            int(np.floor(event_model.freq_range[0])), int(np.ceil(event_model.freq_range[1]))),
        'Frequency Resolution is {:1.2f} Hz'.format(event_model.freq_res),
        '',

        # Aperiodic parameters - knee fit status, and quick exponent description
        'Power spectra were fit {} a knee.'.format(\
            'with' if event_model.aperiodic_mode == 'knee' else 'without'),
        '',
        'Aperiodic params (values across events):',
        *[el for el in ['    Knees - Min: {:6.2f}, Max: {:6.2f}, Mean: {:6.2f}'
                        .format(*compute_arr_desc(np.mean(event_model.event_time_results['knee'], 1) \
                            if has_knee else [0, 0, 0])),
                       ] if has_knee],
        'Exponents - Min: {:6.3f}, Max: {:6.3f}, Mean: {:5.3f}'
        .format(*compute_arr_desc(np.mean(event_model.event_time_results['exponent'], 1))),
        '',

        # Periodic parameters
        'Periodic params (mean values across events):',
        *['{:>6s} - CF: {:5.2f}, PW: {:5.2f}, BW: {:5.2f}, Presence: {:3.1f}%'.format(
            label,
            np.nanmean(event_model.event_time_results[pe_labels['cf'][ind]]),
            np.nanmean(event_model.event_time_results[pe_labels['pw'][ind]]),
            np.nanmean(event_model.event_time_results[pe_labels['bw'][ind]]),
            compute_presence(event_model.event_time_results[pe_labels['cf'][ind]],
                             average=True, output='percent'))
                for ind, label in enumerate(band_labels)],
        '',

        # Goodness if fit
        'Goodness of fit (values across events):',
        '   R2s -  Min: {:6.3f}, Max: {:6.3f}, Mean: {:5.3f}'
        .format(*compute_arr_desc(np.mean(event_model.event_time_results['r_squared'], 1))),

        'Errors -  Min: {:6.3f}, Max: {:6.3f}, Mean: {:5.3f}'
        .format(*compute_arr_desc(np.mean(event_model.event_time_results['error'], 1))),
        '',

        # Footer
        '='
    ]

    output = _format(str_lst, concise)

    return output


def gen_issue_str(concise=False):
    """Generate a string representation of instructions to report an issue.

    Parameters
    ----------
    concise : bool, optional, default: False
        Whether to print the report in a concise mode, or not.

    Returns
    -------
    output : str
        Formatted string of how to provide feedback.
    """

    str_lst = [

        # Header
        '=',
        '',
        'specparam - ISSUE REPORTING',
        '',

        # Reporting bugs
        'Please report any bugs or unexpected errors on Github:',
        'https://github.com/fooof-tools/fooof/issues',
        '',

        # Reporting a weird fit
        'If model fitting gives you any weird / bad fits, please let us know!',
        'To do so, you can send us a fit report, and an associated data file, ',
        '',
        'With a model object (model), after fitting, run the following commands:',
        "model.create_report('bad_fit_report')",
        "model.save('bad_fit_data', True, True, True)",
        '',
        'You can attach the generated files to a Github issue.',
        '',

        # Footer
        '='
    ]

    output = _format(str_lst, concise)

    return output


def _format(str_lst, concise):
    """Format a string for printing.

    Parameters
    ----------
    str_lst : list of str
        List containing all elements for the string, each element representing a line.
    concise : bool, optional, default: False
        Whether to print the report in a concise mode, or not.

    Returns
    -------
    output : str
        Formatted string, ready for printing.
    """

    # Set centering value - use a smaller value if in concise mode
    center_val = SCV if concise else LCV

    # Expand the section markers to full width
    str_lst[0] = str_lst[0] * center_val
    str_lst[-1] = str_lst[-1] * center_val

    # Drop blank lines, if concise
    str_lst = list(filter(lambda x: x != '', str_lst)) if concise else str_lst

    # Convert list to a single string representation, centering each line
    output = '\n'.join([string.center(center_val) for string in str_lst])

    return output


def _no_model_str(concise=False):
    """Creates a null report, for use if the model fit failed, or is unavailable.

    Parameters
    ----------
    concise : bool, optional, default: False
        Whether to print the report in a concise mode, or not.
    """

    str_lst = [
        '=',
        '',
        'Model fit has not been run, or fitting was unsuccessful.',
        '',
        '='
    ]

    output = _format(str_lst, concise)

    return output
