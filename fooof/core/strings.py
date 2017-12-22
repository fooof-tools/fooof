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

def gen_bw_warn_str(freq_res, bwl):
    """Generate a string representation of warning about bandwidth limits.

    Parameters
    ----------
    freq_res : float
        Frequency resolution.
    bwl : float
        Lower bound bandwidth-limit.
    """

    output = '\n'.join([
        '',
        "FOOOF WARNING: Lower-bound bandwidth limit is < or ~= the frequency resolution: " + \
            "{:1.2f} <= {:1.2f}".format(freq_res, bwl),
        '\tLower bounds below frequency-resolution have no effect (effective lower bound is freq-res)',
        '\tToo low a limit may lead to overfitting noise as small bandwidth oscillations.',
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
    description : bool, optional
        Whether to print out a description with current settings. default: True
    concise : bool, optional
        Whether to print the report in a concise mode, or not. default: False

    Returns
    -------
    output : str
        Formatted string of current settings.
    """

    # Parameter descriptions to print out, if requested
    desc = {'background_mode' : 'The aproach taken to fitting the background.',
            'bw_lims'         : 'Possible range of bandwidths for extracted oscillations, in Hz.',
            'num_oscs'        : 'The maximum number of oscillations that can be extracted.',
            'min_amp'         : "Minimum absolute amplitude, above background, "
                                "for an oscillation to be extracted.",
            'amp_thresh'      : "Threshold, in units of standard deviation, "
                                "at which to stop searching for oscillations."}

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
        *[el for el in ['Fit Knee : {}'.format(f_obj.background_mode),
                        '{}'.format(desc['background_mode']),
                        'Bandwidth Limits : {}'.format(f_obj.bandwidth_limits),
                        '{}'.format(desc['bw_lims']),
                        'Max Number of Oscillations : {}'.format(f_obj.max_n_gauss),
                        '{}'.format(desc['num_oscs']),
                        'Minimum Amplitude : {}'.format(f_obj.min_amp),
                        '{}'.format(desc['min_amp']),
                        'Amplitude Threshold: {}'.format(f_obj.amp_std_thresh),
                        '{}'.format(desc['amp_thresh'])] if el != ''],

        # Footer
        '',
        '='
    ]

    output = _format(str_lst, concise)

    return output


def gen_results_str_fm(fm, concise=False):
    """Generate a string representation of model fit results.

    Parameters
    ----------
    fm : FOOOF object
        Object for which results are to be printed.
    concise : bool, optional
        Whether to print the report in a concise mode, or not. default: False

    Returns
    -------
    output : str
        Formatted string of FOOOF model results.
    """

    if not np.all(fm.background_params_):
        raise ValueError('Model fit has not been run - can not proceed.')

    # Create the formatted strings for printing
    str_lst = [

        # Header
        '=',
        '',
        ' FOOOF - PSD MODEL',
        '',

        # Frequency range and resolution
        'The model was run on the frequency range {} - {} Hz'.format(
            int(np.floor(fm.freq_range[0])), int(np.ceil(fm.freq_range[1]))),
        'Frequency Resolution is {:1.2f} Hz'.format(fm.freq_res),
        '',

        # Background parameters
        ('Background Parameters (offset, ' + ('knee, ' if fm.background_mode == 'knee' else '') + \
           'slope): '),
        ', '.join(['{:2.4f}'] * len(fm.background_params_)).format(
            *fm.background_params_),
        '',

        # Oscillation parameters
        '{} oscillations were found:'.format(
            len(fm.oscillation_params_)),
        *['CF: {:6.2f}, Amp: {:6.3f}, BW: {:5.2f}'.format(op[0], op[1], op[2]) \
          for op in fm.oscillation_params_],
        '',

        # R^2 and error
        'Goodness of fit metrics:',
        'R^2 of model fit is {:5.4f}'.format(fm.r2_),
        'Root mean squared error is {:5.4f}'.format(
            fm.error_),
        '',

        # Footer
        '='
    ]

    output = _format(str_lst, concise)

    return output


def gen_results_str_fg(fg, concise=False):
    """Generate a string representation of group fit results.

    Parameters
    ----------
    fg : FOOOFGroup() object
        Group object for which results are to be printed.
    concise : bool, optional
        Whether to print the report in a concise mode, or not. default: False

    Returns
    -------
    output : str
        Formatted string of FOOOFGroup results.
    """

    if not fg.group_results:
        raise ValueError('Model fit has not been run - can not proceed.')

    # Extract all the relevant data for printing
    cens = fg.get_all_data('oscillation_params', 0)
    r2s = fg.get_all_data('r2')
    errors = fg.get_all_data('error')
    if fg.background_mode == 'knee':
        kns = fg.get_all_data('background_params', 1)
        sls = fg.get_all_data('background_params', 2)
    else:
        kns = np.array([0])
        sls = fg.get_all_data('background_params', 1)

    str_lst = [

        # Header
        '=',
        '',
        ' FOOOF - GROUP RESULTS',
        '',

        # Group information
        'Number of PSDs in the Group: {}'.format(len(fg.group_results)),
        '',

        # Frequency range and resolution
        'The model was run on the frequency range {} - {} Hz'.format(
            int(np.floor(fg.freq_range[0])), int(np.ceil(fg.freq_range[1]))),
        'Frequency Resolution is {:1.2f} Hz'.format(fg.freq_res),
        '',

        # Background parameters - knee fit status, and quick slope description
        'PSDs were fit {} a knee.'.format('with' if fg.background_mode == 'knee' else 'without'),
        '',
        *[el for el in ['Background Knee Values',
                        'Min: {:6.2f}, Max: {:6.2f}, Mean: {:5.2f}'
                        .format(kns.min(), kns.max(), kns.mean()),
                       ] if fg.background_mode == 'knee'],
        'Background Slope Values',
        'Min: {:6.4f}, Max: {:6.4f}, Mean: {:5.4f}'
        .format(sls.min(), sls.max(), sls.mean()),
        '',

        # Oscillation Parameters
        'In total {} oscillations were extracted from the group'
        .format(len(cens)),
        '',

        # Fitting stats - error and r^2
        'Goodness of fit metrics:',
        '   R2s -  Min: {:6.4f}, Max: {:6.4f}, Mean: {:5.4f}'
        .format(r2s.min(), r2s.max(), r2s.mean()),
        'Errors -  Min: {:6.4f}, Max: {:6.4f}, Mean: {:5.4f}'
        .format(errors.min(), errors.max(), errors.mean()),
        '',

        # Footer
        '='
    ]

    output = _format(str_lst, concise)

    return output


def gen_report_str(concise=False):
    """Generate a string representation of instructions to report an issue.

    Parameters
    ----------
    concise : bool, optional
        Whether to print the report in a concise mode, or not. default: False

    Returns
    -------
    output : str
        Formatted string of how to provide feedback.
    """

    str_lst = [

        # Header
        '=',
        '',
        'Contact / Reporting Information for FOOOF',
        '',

        # Reporting bugs
        'Please report any bugs or unexpected errors on Github.',
        'https://github.com/voytekresearch/fooof/issues',
        '',

        # Reporting a weird fit
        'If FOOOF gives you any weird / bad fits, we would like to know, so we can make it better!',
        'To help us with this, send us a FOOOF report, and a FOOOF data file, for any bad fits.',
        '',
        'With a FOOOF object (fm), after fitting, run the following commands:',
        "fm.create_report('FOOOF_bad_fit_report')",
        "fm.save('FOOOF_bad_fit_data', True, True, True)",
        '',
        "Send the generated files ('FOOOF_bad_fit_report.pdf' & 'FOOOF_bad_fit_data.json') to us.",
        'We will have a look, and provide any feedback we can.',
        '',
        'We suggest sending individual examplars, but the above will also work with a FOOOFGroup.',
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
    concise : bool, optional
        Whether to print the report in a concise mode, or not. default: False

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
