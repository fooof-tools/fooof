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
    description : bool, optional (default: True)
        Whether to print out a description with current settings.

    Returns
    -------
    output : str
        Formatted string of current settings.
    """

    # Use a smaller centering value if in concise mode
    cv = SCV if concise else LCV

    # Parameter descriptions to print out, if requested
    desc = {'bg_use_knee' : 'Whether to fit a knee parameter in background fitting.',
            'bw_lims'     : 'Possible range of bandwidths for extracted oscillations, in Hz.',
            'num_oscs'    : 'The maximum number of oscillations that can be extracted.',
            'min_amp'     : "Minimum absolute amplitude, above background, "
                            "for an oscillation to be extracted.",
            'amp_thresh'  : "Threshold, in units of standard deviation, "
                            "at which to stop searching for oscillations."}

    # Clear description for printing if not requested
    if not description:
        desc = {k : '' for k, v in desc.items()}

    # Create output string
    output = [

        # Header
        '=' * cv,
        ' ' if not concise else None,
        'FOOOF - SETTINGS'.center(cv),
        ' ' if not concise else None,

        # Settings - include descriptions if requested
        *[el for el in ['Fit Knee : {}'.format(f_obj.bg_use_knee).center(cv),
                        '{}'.format(desc['bg_use_knee']).center(cv),
                        'Bandwidth Limits : {}'.format(f_obj.bandwidth_limits).center(cv),
                        '{}'.format(desc['bw_lims']).center(cv),
                        'Max Number of Oscillations : {}'.format(f_obj.max_n_gauss).center(cv),
                        '{}'.format(desc['num_oscs']).center(cv),
                        'Minimum Amplitude : {}'.format(f_obj.min_amp).center(cv),
                        '{}'.format(desc['min_amp']).center(cv),
                        'Amplitude Threshold: {}'.format(f_obj.amp_std_thresh).center(cv),
                        '{}'.format(desc['amp_thresh']).center(cv)] if el != ' ' * cv],

        # Footer
        ' ' if not concise else None,
        '=' * cv
    ]

    # Converts list to string, dropping blank lines if concise
    output = '\n'.join(filter(None, output))

    return output


def gen_results_str_fm(fm, concise=False):
    """Generate a string representation of model fit results.

    Parameters
    ----------
    fm : FOOOF object
        Object for which results are to be printed.

    Returns
    -------
    output : str
        Formatted string of FOOOF model results.
    """

    if not np.all(fm.background_params_):
        raise ValueError('Model fit has not been run - can not proceed.')

    # Use a smaller centering value if in concise mode
    cv = SCV if concise else LCV

    # Create the formatted strings for printing
    output = [

        # Header
        '=' * cv,
        ' ' if not concise else None,
        ' FOOOF - PSD MODEL'.center(cv),
        ' ' if not concise else None,

        # Frequency range and resolution
        'The model was run on the frequency range {} - {} Hz'.format(
            int(np.floor(fm.freq_range[0])), int(np.ceil(fm.freq_range[1]))).center(cv),
        'Frequency Resolution is {:1.2f} Hz'.format(fm.freq_res).center(cv) if not concise else None,
        ' ' if not concise else None,

        # Background parameters
        ('Background Parameters (offset, ' + ('knee, ' if fm.bg_use_knee else '') + \
           'slope): ').center(cv),
        ', '.join(['{:2.4f}'] * len(fm.background_params_)).format(
            *fm.background_params_).center(cv),
        ' ' if not concise else None,

        # Oscillation parameters
        '{} oscillations were found:'.format(
            len(fm.oscillation_params_)).center(cv),
        *['CF: {:6.2f}, Amp: {:6.3f}, BW: {:5.2f}'.format(op[0], op[1], op[2]).center(cv) \
          for op in fm.oscillation_params_],
        ' ' if not concise else None,

        # R^2 and error
        'Goodness of fit metrics:'.center(cv),
        'R^2 of model fit is {:5.4f}'.format(fm.r2_).center(cv),
        'Root mean squared error is {:5.4f}'.format(
            fm.error_).center(cv),
        ' ' if not concise else None,

        # Footer
        '=' * cv
    ]

    # Converts list to string, dropping blank lines if concise
    output = '\n'.join(filter(None, output))

    return output


def gen_results_str_fg(fg, concise=False):
    """Generate a string representation of group fit results.

    Parameters
    ----------
    fg : FOOOFGroup() object
        Group object for which results are to be printed.

    Returns
    -------
    output : str
        Formatted string of FOOOFGroup results.
    """

    if not fg.group_results:
        raise ValueError('Model fit has not been run - can not proceed.')

    # Use a smaller centering value if in concise mode
    cv = SCV if concise else LCV

    # Extract all the relevant data for printing
    cens = fg.get_all_data('oscillation_params', 0)
    r2s = fg.get_all_data('r2')
    errors = fg.get_all_data('error')
    if fg.bg_use_knee:
        kns = fg.get_all_data('background_params', 1)
        sls = fg.get_all_data('background_params', 2)
    else:
        kns = np.array([0])
        sls = fg.get_all_data('background_params', 1)

    # Create the formatted strings for printing
    output = [

        # Header
        '=' * cv,
        ' ' if not concise else None,
        ' FOOOF - GROUP RESULTS'.center(cv),
        ' ' if not concise else None,

        # Group information
        'Number of PSDs in the Group: {}'.format(len(fg.group_results)).center(cv),
        ' ' if not concise else None,

        # Frequency range and resolution
        'The model was run on the frequency range {} - {} Hz'.format(
            int(np.floor(fg.freq_range[0])), int(np.ceil(fg.freq_range[1]))).center(cv),
        'Frequency Resolution is {:1.2f} Hz'.format(fg.freq_res).center(cv),
        ' ' if not concise else None,

        # Background parameters - knee fit status, and quick slope description
        'PSDs were fit {} a knee.'.format('with' if fg.bg_use_knee else 'without').center(cv),
        ' ' if not concise else None,
        *[el for el in ['Background Knee Values'.center(cv),
                        'Min: {:6.2f}, Max: {:6.2f}, Mean: {:5.2f}'
                        .format(kns.min(), kns.max(), kns.mean()).center(cv)
                       ] if fg.bg_use_knee],
        'Background Slope Values'.center(cv),
        'Min: {:6.4f}, Max: {:6.4f}, Mean: {:5.4f}'
        .format(sls.min(), sls.max(), sls.mean()).center(cv),
        ' ' if not concise else None,

        # Oscillation Parameters
        'In total {} oscillations were extracted from the group'
        .format(len(cens)).center(cv),
        ' ' if not concise else None,

        # Fitting stats - error and r^2
        'Goodness of fit metrics:'.center(cv),
        '   R2s -  Min: {:6.4f}, Max: {:6.4f}, Mean: {:5.4f}'
        .format(r2s.min(), r2s.max(), r2s.mean()).center(cv),
        'Errors -  Min: {:6.4f}, Max: {:6.4f}, Mean: {:5.4f}'
        .format(errors.min(), errors.max(), errors.mean()).center(cv),
        ' ' if not concise else None,

        # Footer
        '=' * cv
    ]

    # Converts list to string, dropping blank lines if concise
    output = '\n'.join(filter(None, output))

    return output


def gen_report_str(concise=False):
    """Generate a string representation of instructions to report an issue.

    Returns
    -------
    output : str
        Formatted string of how to provide feedback.
    """

    # Use a smaller centering value if in concise mode
    cv = SCV if concise else LCV

    # Create output string
    output = [

        # Header
        '=' * cv,
        ' ',
        'Contact / Reporting Information for FOOOF'.center(cv),
        ' ',

        # Reporting bugs
        'Please report any bugs or unexpected errors on Github. '.center(cv),
        'https://github.com/voytekresearch/fooof/issues'.center(cv),
        ' ',

        # Reporting a weird fit
        'If FOOOF gives you any weird / bad fits, we would like to know, so we can make it better!'.center(cv),
        'To help us with this, send us a FOOOF report, and a FOOOF data file, for any bad fits.'.center(cv),
        ' ',
        'With a FOOOF object (fm), after fitting, run the following commands:'.center(cv),
        "fm.create_report('FOOOF_bad_fit_report')".center(cv),
        "fm.save('FOOOF_bad_fit_data', True, True, True)".center(cv),
        ' ',
        "Send the generated files ('FOOOF_bad_fit_report.pdf' & 'FOOOF_bad_fit_data.json') to us.".center(cv),
        'We will have a look, and provide any feedback we can.'.center(cv),
        ' ',
        'We suggest sending individual examplars, but the above will also work with a FOOOFGroup.'.center(cv),
        ' ',

        # Contact
        'Contact address: voytekresearch@gmail.com'.center(cv),
        ' ',

        # Footer
        '=' * cv
    ]

    # Converts list to string, dropping blank lines if concise
    output = '\n'.join(filter(None, output))

    return output
