"""Formatted strings for printing out ERPparam related information."""

import numpy as np

from ERPparam.core.errors import NoModelError
from ERPparam.version import __version__ as ERPPARAM_VERSION

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
        'ERPparam WARNING: Lower-bound peak width limit is < or ~= the frequency resolution: ' + \
            '{:1.2f} <= {:1.2f}'.format(bwl, freq_res),
        '\tLower bounds below frequency-resolution have no effect ' + \
        '(effective lower bound is the frequency resolution).',
        '\tToo low a limit may lead to overfitting noise as small bandwidth peaks.',
        '\tWe recommend a lower bound of approximately 2x the frequency resolution.',
        ''
    ])

    return output


def gen_version_str(concise=False):
    """Generate a string representation of the current version of ERPparam.

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
        'ERPparam - VERSION',
        '',

        # Version information
        '{}'.format(ERPPARAM_VERSION),

        # Footer
        '',
        '='

    ]

    output = _format(str_lst, concise)

    return output


def gen_settings_str(ERPparam_obj, description=False, concise=False):
    """Generate a string representation of current ERPparam settings.

    Parameters
    ----------
    ERPparam_obj : ERPparam or ERPparamGroup or ERPparamSettings
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
        }

    # Clear description for printing, if not requested
    if not description:
        desc = {k : '' for k, v in desc.items()}

    # Create output string
    str_lst = [

        # Header
        '=',
        '',
        'ERPparam - SETTINGS',
        '',

        # Settings - include descriptions if requested
        *[el for el in ['Peak Width Limits : {}'.format(ERPparam_obj.peak_width_limits),
                        '{}'.format(desc['peak_width_limits']),
                        'Max Number of Peaks : {}'.format(ERPparam_obj.max_n_peaks),
                        '{}'.format(desc['max_n_peaks']),
                        'Minimum Peak Height : {}'.format(ERPparam_obj.min_peak_height),
                        '{}'.format(desc['min_peak_height']),
                        'Peak Threshold: {}'.format(ERPparam_obj.peak_threshold),
                        '{}'.format(desc['peak_threshold'])] if el != ''],

        # Footer
        '',
        '='
    ]

    output = _format(str_lst, concise)

    return output


def gen_freq_range_str(ERPparam_obj, concise=False):
    """Generate a string representation of the fit range that was used for the model.

    Parameters
    ----------
    ERPparam_obj : ERPparam or ERPparamGroup
        Object to access settings from.
    concise : bool, optional, default: False
        Whether to print the report in concise mode.

    Notes
    -----
    If fit range is not available, will print out 'XX' for missing values.
    """

    freq_range = ERPparam_obj.freq_range if ERPparam_obj.has_data else ('XX', 'XX')

    str_lst = [

        # Header
        '=',
        '',
        'ERPparam - FIT RANGE',
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
    """Generate a string representation of instructions for reporting about using ERPparam.

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
        'ERPparam - REPORTING',
        '',

        # Methods report information
        'To report on using ERPparam, you should report (at minimum):',
        '',
        '- the code version that was used used',
        '- the algorithm settings that were used',
        '- the frequency range that was fit',

        # Footer
        '',
        '='
    ]

    output = _format(str_lst, concise)

    return output


def gen_methods_text_str(ERPparam_obj=None):
    """Generate a string representation of a template methods report.

    Parameters
    ----------
    ERPparam_obj : ERPparam or ERPparamGroup, optional
        A ERPparam object with settings information available.
        If None, the text is returned as a template, without values.
    """

    template = (
        "The ERPparam algorithm (version {}) was used to parameterize "
        "neural power spectra. Settings for the algorithm were set as: "
        "peak width limits : {}; "
        "max number of peaks : {}; "
        "minimum peak height : {}; "
        "peak threshold : {}; "
        "and aperiodic mode : '{}'. "
        "Power spectra were parameterized across the frequency range "
        "{} to {} Hz."
    )

    if ERPparam_obj:
        freq_range = ERPparam_obj.freq_range if ERPparam_obj.has_data else ('XX', 'XX')
    else:
        freq_range = ('XX', 'XX')

    methods_str = template.format(ERPPARAM_VERSION,
                                  ERPparam_obj.peak_width_limits if ERPparam_obj else 'XX',
                                  ERPparam_obj.max_n_peaks if ERPparam_obj else 'XX',
                                  ERPparam_obj.min_peak_height if ERPparam_obj else 'XX',
                                  ERPparam_obj.peak_threshold if ERPparam_obj else 'XX',
                                  ERPparam_obj.aperiodic_mode if ERPparam_obj else 'XX',
                                  *freq_range)

    return methods_str


def gen_results_fm_str(fm, concise=False):
    """Generate a string representation of model fit results.

    Parameters
    ----------
    fm : ERPparam
        Object to access results from.
    concise : bool, optional, default: False
        Whether to print the report in concise mode.

    Returns
    -------
    output : str
        Formatted string of model results.
    """

    # Returns a null report if no results are available
    if np.all(np.isnan(fm.gaussian_params_)):
        return _no_model_str(concise)

    # Create the formatted strings for printing
    str_lst = [

        # Header
        '=',
        '',
        ' ERP MODEL',
        '',

        # Peak parameters
        '{} peaks were found:'.format(
            len(fm.peak_params_)),
        *['Time: {:6.2f}, Amp: {:6.3f}, Dur: {:5.2f}'.format(op[0], op[1], op[2]) \
          for op in fm.peak_params_],
        '',

        # Goodness if fit
        'Goodness of fit metrics:',
        'R^2 of model fit is {:5.4f}'.format(fm.r_squared_),
        'Error of the fit is {:5.4f}'.format(fm.error_),
        '',

        # Footer
        '='
    ]

    output = _format(str_lst, concise)

    return output


def gen_results_fg_str(fg, concise=False):
    """Generate a string representation of group fit results.

    Parameters
    ----------
    fg : ERPparamGroup
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

    if not fg.has_model:
        raise NoModelError("No model fit results are available, can not proceed.")

    # Extract all the relevant data for printing
    n_peaks = len(fg.get_params('peak_params'))
    r2s = fg.get_params('r_squared')
    errors = fg.get_params('error')
    bws = fg.get_params('peak_params', 'BW')
    pws = fg.get_params('peak_params', 'PW')

    # Check if there are any power spectra that failed to fit
    n_failed = fg.n_null_#sum(np.isnan(bws))

    str_lst = [

        # Header
        '=',
        '',
        ' ERPparam - GROUP RESULTS',
        '',

        # Group information
        'Number of Events in the Group: {}'.format(len(fg.group_results)),
        *[el for el in ['{} Events failed to fit'.format(n_failed)] if n_failed],
        '',

        # Frequency range and resolution
        'The model was run on the time range {} - {} '.format(
            int(np.floor(fg.time_range[0])), int(np.ceil(fg.time_range[1]))),
        'Time Resolution is {:1.2f}'.format(fg.time_res),
        '',

        # Aperiodic parameters - knee fit status, and quick exponent description
        # 'Power spectra were fit {} a knee.'.format(\
        #     'with' if fg.aperiodic_mode == 'knee' else 'without'),
        # '',
        'Peak Fit Values:',
        *[el for el in ['    Amplitudes - Min: {:6.2f}, Max: {:6.2f}, Mean: {:5.2f}'
                        .format(np.nanmin(pws), np.nanmax(pws), np.nanmean(pws)),
                       ]],
        'Bandwidths - Min: {:6.3f}, Max: {:6.3f}, Mean: {:5.3f}'
        .format(np.nanmin(bws), np.nanmax(bws), np.nanmean(bws)),
        '',

        # Peak Parameters
        'In total {} peaks were extracted from the group'
        .format(n_peaks),
        '',

        # Goodness if fit
        'Goodness of fit metrics:',
        '   R2s -  Min: {:6.3f}, Max: {:6.3f}, Mean: {:5.3f}'
        .format(np.nanmin(r2s), np.nanmax(r2s), np.nanmean(r2s)),
        'Errors -  Min: {:6.3f}, Max: {:6.3f}, Mean: {:5.3f}'
        .format(np.nanmin(errors), np.nanmax(errors), np.nanmean(errors)),
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
        'ERPparam - ISSUE REPORTING',
        '',

        # Reporting bugs
        'Please report any bugs or unexpected errors on Github.',
        '',

        # Reporting a weird fit
        'If ERPparam gives you any weird / bad fits, please let us know!',
        'To do so, send us a ERPparam report, and a ERPparam data file, ',
        '',
        'With a ERPparam object (fm), after fitting, run the following commands:',
        "fm.create_report('ERPparam_bad_fit_report')",
        "fm.save('ERPparam_bad_fit_data', True, True, True)",
        '',
        'Send the generated files to us.',
        'We will have a look, and provide any feedback we can.',
        '',

        # Contact
        'Contact address: voytekresearch@gmail.com',
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
