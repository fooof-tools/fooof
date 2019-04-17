"""Formatted strings for printing out FOOOF related information and data."""

import numpy as np

###################################################################################################
###################################################################################################

## Settings & Globals
# Centering Value - Long & Short options
#  Note: Long CV of 98 is so that the max line length plays nice with notebook rendering on Github
LCV = 98
SCV = 70

###################################################################################################
###################################################################################################

def gen_width_warning_str(freq_res, bwl):
    """Generate a string representation of warning about peak width limits.

    Parameters
    ----------
    freq_res : float
        Frequency resolution.
    bwl : float
        Lower bound peak width limit.
    """

    output = '\n'.join([
        '',
        'FOOOF WARNING: Lower-bound peak width limit is < or ~= the frequency resolution: ' + \
            '{:1.2f} <= {:1.2f}'.format(freq_res, bwl),
        '\tLower bounds below frequency-resolution have no effect (effective lower bound is the frequency resolution).',
        '\tToo low a limit may lead to overfitting noise as small bandwidth peaks.',
        '\tWe recommend a lower bound of approximately 2x the frequency resolution.',
        ''
    ])

    return output


def gen_settings_str(f_obj, description=False, concise=False):
    """Generate a string representation of current FOOOF settings.

    Parameters
    ----------
    f_obj : FOOOF or FOOOFGroup object
        A FOOOF derived object, from which settings are to be used.
    description : bool, optional, default: True
        Whether to print out a description with current settings.
    concise : bool, optional, default: False
        Whether to print the report in a concise mode, or not.

    Returns
    -------
    output : str
        Formatted string of current settings.
    """

    # Parameter descriptions to print out, if requested
    desc = {'peak_width_limits'     : 'Enforced limits for peak widths, in Hz.',
            'max_n_peaks'           : 'The maximum number of peaks that can be extracted.',
            'min_peak_height'       : 'Minimum absolute height of a peak, above the aperiodic component.',
            'peak_threshold'        : 'Threshold at which to stop searching for peaks.',
            'aperiodic_mode'        : 'The aproach taken to fitting the aperiodic component.'}

    # Clear description for printing if not requested
    if not description:
        desc = {k : '' for k, v in desc.items()}

    # Create output string
    str_lst = [

        # Header
        '=',
        '',
        'FOOOF - SETTINGS',
        '',

        # Settings - include descriptions if requested
        *[el for el in ['Peak Width Limits : {}'.format(f_obj.peak_width_limits),
                        '{}'.format(desc['peak_width_limits']),
                        'Max Number of Peaks : {}'.format(f_obj.max_n_peaks),
                        '{}'.format(desc['max_n_peaks']),
                        'Minimum Peak Height : {}'.format(f_obj.min_peak_height),
                        '{}'.format(desc['min_peak_height']),
                        'Peak Threshold: {}'.format(f_obj.peak_threshold),
                        '{}'.format(desc['peak_threshold']),
                        'Aperiodic Mode : {}'.format(f_obj.aperiodic_mode),
                        '{}'.format(desc['aperiodic_mode'])] if el != ''],

        # Footer
        '',
        '='
    ]

    output = _format(str_lst, concise)

    return output


def gen_results_fm_str(fm, concise=False):
    """Generate a string representation of model fit results.

    Parameters
    ----------
    fm : FOOOF object
        Object for which results are to be printed.
    concise : bool, optional, default: False
        Whether to print the report in a concise mode, or not.

    Returns
    -------
    output : str
        Formatted string of FOOOF model results.
    """

    # Returns a null report if no results are available
    if np.all(np.isnan(fm.aperiodic_params_)):
        return _no_model_str(concise)

    # Create the formatted strings for printing
    str_lst = [

        # Header
        '=',
        '',
        ' FOOOF - POWER SPECTRUM MODEL',
        '',

        # Frequency range and resolution
        'The model was run on the frequency range {} - {} Hz'.format(
            int(np.floor(fm.freq_range[0])), int(np.ceil(fm.freq_range[1]))),
        'Frequency Resolution is {:1.2f} Hz'.format(fm.freq_res),
        '',

        # Aperiodic parameters
        ('Aperiodic Parameters (offset, ' + ('knee, ' if fm.aperiodic_mode == 'knee' else '') + \
           'exponent): '),
        ', '.join(['{:2.4f}'] * len(fm.aperiodic_params_)).format(
            *fm.aperiodic_params_),
        '',

        # Peak parameters
        '{} peaks were found:'.format(
            len(fm.peak_params_)),
        *['CF: {:6.2f}, PW: {:6.3f}, BW: {:5.2f}'.format(op[0], op[1], op[2]) \
          for op in fm.peak_params_],
        '',

        # R^2 and error
        'Goodness of fit metrics:',
        'R^2 of model fit is {:5.4f}'.format(fm.r_squared_),
        'Root mean squared error is {:5.4f}'.format(
            fm.error_),
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
    fg : FOOOFGroup() object
        Group object for which results are to be printed.
    concise : bool, optional, default: False
        Whether to print the report in a concise mode, or not.

    Returns
    -------
    output : str
        Formatted string of FOOOFGroup results.
    """

    if not fg.group_results:
        raise ValueError('Model fit has not been run - can not proceed.')

    # Extract all the relevant data for printing
    n_peaks = len(fg.get_params('peak_params'))
    r2s = fg.get_params('r_squared')
    errors = fg.get_params('error')
    if fg.aperiodic_mode == 'knee':
        kns = fg.get_params('aperiodic_params', 1)
        sls = fg.get_params('aperiodic_params', 2)
    else:
        kns = np.array([0])
        sls = fg.get_params('aperiodic_params', 1)

    # Check if there are any power spectra that failed to fit
    n_failed = sum(np.isnan(sls))

    str_lst = [

        # Header
        '=',
        '',
        ' FOOOF - GROUP RESULTS',
        '',

        # Group information
        'Number of power spectra in the Group: {}'.format(len(fg.group_results)),
        *[el for el in ['{} power spectra failed to fit'.format(n_failed)] if n_failed],
        '',

        # Frequency range and resolution
        'The model was run on the frequency range {} - {} Hz'.format(
            int(np.floor(fg.freq_range[0])), int(np.ceil(fg.freq_range[1]))),
        'Frequency Resolution is {:1.2f} Hz'.format(fg.freq_res),
        '',

        # Aperiodic parameters - knee fit status, and quick exponent description
        'Power spectra were fit {} a knee.'.format('with' if fg.aperiodic_mode == 'knee' else 'without'),
        '',
        *[el for el in ['Aperiodic Knee Values',
                        'Min: {:6.2f}, Max: {:6.2f}, Mean: {:5.2f}'
                        .format(np.nanmin(kns), np.nanmax(kns), np.nanmean(kns)),
                       ] if fg.aperiodic_mode == 'knee'],
        'Aperiodic Exponent Values',
        'Min: {:6.4f}, Max: {:6.4f}, Mean: {:5.4f}'
        .format(np.nanmin(sls), np.nanmax(sls), np.nanmean(sls)),
        '',

        # Peak Parameters
        'In total {} peaks were extracted from the group'
        .format(n_peaks),
        '',

        # Fitting stats - error and r^2
        'Goodness of fit metrics:',
        '   R2s -  Min: {:6.4f}, Max: {:6.4f}, Mean: {:5.4f}'
        .format(np.nanmin(r2s), np.nanmax(r2s), np.nanmean(r2s)),
        'Errors -  Min: {:6.4f}, Max: {:6.4f}, Mean: {:5.4f}'
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
        'CONTACT / REPORTING ISSUES WITH FOOOF',
        '',

        # Reporting bugs
        'Please report any bugs or unexpected errors on Github.',
        'https://github.com/fooof-tools/fooof/issues',
        '',

        # Reporting a weird fit
        'If FOOOF gives you any weird / bad fits, please let us know!',
        'To do so, send us a FOOOF report, and a FOOOF data file, ',
        '',
        'With a FOOOF object (fm), after fitting, run the following commands:',
        "fm.create_report('FOOOF_bad_fit_report')",
        "fm.save('FOOOF_bad_fit_data', True, True, True)",
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

    # Use a smaller centering value if in concise mode
    cv = SCV if concise else LCV

    # Expand the section markers to full width
    str_lst[0] = str_lst[0] * cv
    str_lst[-1] = str_lst[-1] * cv

    # Drop blank lines, if concise
    str_lst = list(filter(lambda x: x != '', str_lst)) if concise else str_lst

    # Convert list to a single string representation, centering each line
    output = '\n'.join([string.center(cv) for string in str_lst])

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
