"""Formatted strings for printing out FOOOF related information and data."""

import numpy as np

###################################################################################################
###################################################################################################

## Settings & Globals
CV = 100                # Centering Value

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


def gen_settings_str(f_obj, description=False):
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

    # Parameter descriptions to print out, if requested
    desc = {'bg_use_knee' : 'Whether to fit a knee parameter in background fitting.',
            'bw_lims'     : 'Possible range of bandwidths for extracted oscillations, in Hz.',
            'num_oscs'    : 'The maximum number of oscillations that can be extracted.',
            'min_amp'     : "Minimum absolute amplitude, above background, "
                            "for an oscillation to be extracted.",
            'amp_thresh'  : "Threshold, in units of standard deviation,"
                            "at which to stop searching for oscillations."}

    # Clear description for printing if not requested
    if not description:
        desc = {k : '' for k, v in desc.items()}

    # Create output string
    output = '\n'.join([

        # Header
        '=' * CV,
        '',
        'FOOOF - SETTINGS'.center(CV),
        '',

        # Settings - include descriptions if requested
        *[el for el in ['Fit Knee : {}'.format(f_obj.bg_use_knee).center(CV),
                        '{}'.format(desc['bg_use_knee']).center(CV),
                        'Bandwidth Limits : {}'.format(f_obj.bandwidth_limits).center(CV),
                        '{}'.format(desc['bw_lims']).center(CV),
                        'Max Number of Oscillations : {}'.format(f_obj.max_n_gauss).center(CV),
                        '{}'.format(desc['num_oscs']).center(CV),
                        'Minimum Amplitude : {}'.format(f_obj.min_amp).center(CV),
                        '{}'.format(desc['min_amp']).center(CV),
                        'Amplitude Threshold: {}'.format(f_obj.amp_std_thresh).center(CV),
                        '{}'.format(desc['amp_thresh']).center(CV)] if el != ' '*CV],

        # Footer
        '',
        '=' * CV
    ])

    return output


def gen_results_str_fm(fm):
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

    # Create output string
    output = '\n'.join([

        # Header
        '=' * CV,
        '',
        ' FOOOF - PSD MODEL'.center(CV),
        '',

        # Frequency range and resolution
        'The input PSD was modelled in the frequency range: {} - {} Hz'.format(
            int(np.floor(fm.freq_range[0])), int(np.ceil(fm.freq_range[1]))).center(CV),
        'Frequency Resolution is {:1.2f} Hz'.format(fm.freq_res).center(CV),
        '',

        # Background parameters
        ('Background Parameters (offset, ' + ('knee, ' if fm.bg_use_knee else '') + \
           'slope): ').center(CV),
        ', '.join(['{:2.4f}'] * len(fm.background_params_)).format(
            *fm.background_params_).center(CV),
        '',

        # Oscillation parameters
        '{} oscillations were found:'.format(
            len(fm.oscillation_params_)).center(CV),
        *['CF: {:6.2f}, Amp: {:6.3f}, BW: {:5.2f}'.format(op[0], op[1], op[2]).center(CV) \
          for op in fm.oscillation_params_],
        '',

        # R^2 and error
        'R^2 of model fit is {:5.4f}'.format(fm.r2_).center(CV),
        'Root mean squared error of model fit is {:5.4f}'.format(
            fm.error_).center(CV),
        '',

        # Footer
        '=' * CV
    ])

    return output


def gen_results_str_fg(fg):
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

    # Create output string
    output = '\n'.join([

        # Header
        '=' * CV,
        '',
        ' FOOOF - GROUP RESULTS'.center(CV),
        '',

        # Group information
        'Number of PSDs in the Group: {}'.format(len(fg.group_results)).center(CV),
        '',

        # Frequency range and resolution
        'The input PSDs were modelled in the frequency range: {} - {} Hz'.format(
            int(np.floor(fg.freq_range[0])), int(np.ceil(fg.freq_range[1]))).center(CV),
        'Frequency Resolution is {:1.2f} Hz'.format(fg.freq_res).center(CV),
        '',

        # Background parameters - knee fit status, and quick slope description
        'PSDs were fit {} a knee.'.format('with' if fg.bg_use_knee else 'without').center(CV),
        '',
        *[el for el in ['Background Knee Values'.center(CV),
                        'Min: {:6.2f}, Max: {:6.2f}, Mean: {:5.2f}'
                        .format(kns.min(), kns.max(), kns.mean()).center(CV)
                       ] if fg.bg_use_knee],
        'Background Slope Values'.center(CV),
        'Min: {:6.4f}, Max: {:6.4f}, Mean: {:5.4f}'
        .format(sls.min(), sls.max(), sls.mean()).center(CV),
        '',

        # Oscillation Parameters
        'In total {} oscillations were extracted from the group'
        .format(len(cens)).center(CV),
        '',

        # Fitting stats - error and r^2
        'Fitting Performance'.center(CV),
        '   R2s -  Min: {:6.4f}, Max: {:6.4f}, Mean: {:5.4f}'
        .format(r2s.min(), r2s.max(), r2s.mean()).center(CV),
        'Errors -  Min: {:6.4f}, Max: {:6.4f}, Mean: {:5.4f}'
        .format(errors.min(), errors.max(), errors.mean()).center(CV),
        '',

        # Footer
        '=' * CV
    ])

    return output


def gen_report_str():
    """Generate a string representation of instructions to report an issue.

    Returns
    -------
    output : str
        Formatted string of how to provide feedback.
    """

    # Create output string
    output = '\n'.join([

        # Header
        '=' * CV,
        '',
        'Contact / Reporting Information for FOOOF'.center(CV),
        '',

        # Reporting bugs
        'Please report any bugs or unexpected errors on Github. '.center(CV),
        'https://github.com/voytekresearch/fooof/issues'.center(CV),
        '',

        # Reporting a weird fit
        'If FOOOF gives you any weird / bad fits, we would like to know, so we can make it better!'.center(CV),
        'To help us with this, send us a FOOOF report, and a FOOOF data file, for any bad fits.'.center(CV),
        '',
        'With a FOOOF object (fm), after fitting, run the following commands:'.center(CV),
        "fm.create_report('FOOOF_bad_fit_report')".center(CV),
        "fm.save('FOOOF_bad_fit_data', True, True, True)".center(CV),
        '',
        "Send the generated files ('FOOOF_bad_fit_report.pdf' & 'FOOOF_bad_fit_data.json') to us.".center(CV),
        'We will have a look, and provide any feedback we can.'.center(CV),
        '',
        'We suggest sending individual examplars, but the above will also work with a FOOOFGroup.'.center(CV),
        '',

        # Contact
        'Contact address: voytekresearch@gmail.com'.center(CV),
        '',

        # Footer
        '=' * CV
    ])

    return output
