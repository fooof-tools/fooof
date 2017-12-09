"""Formatted strings for printing out FOOOF related information and data."""

import numpy as np

###################################################################################################
###################################################################################################

def gen_settings_str(f_obj, description=False):
    """Generate a string representation of current FOOOF settings.

    Parameters
    ----------
    f_obj : FOOOF or FOOOFGroup object
        A FOOOF derived object, from which settings are to be used.
    description : bool, optional (default: True)
        Whether to print out a description with current settings.
    """

    # Center value for spacing
    cen_val = 100

    # Parameter descriptions to print out
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
        '=' * cen_val,
        '',
        'FOOOF - SETTINGS'.center(cen_val),
        '',

        # Settings - include descriptions if requested
        *[el for el in ['Fit Knee : {}'.format(f_obj.bg_use_knee).center(cen_val),
                        '{}'.format(desc['bg_use_knee']).center(cen_val),
                        'Bandwidth Limits : {}'.format(f_obj.bandwidth_limits).center(cen_val),
                        '{}'.format(desc['bw_lims']).center(cen_val),
                        'Max Number of Oscillations : {}'.format(f_obj.max_n_oscs).center(cen_val),
                        '{}'.format(desc['num_oscs']).center(cen_val),
                        'Minimum Amplitude : {}'.format(f_obj.min_amp).center(cen_val),
                        '{}'.format(desc['min_amp']).center(cen_val),
                        'Amplitude Threshold: {}'.format(f_obj.amp_std_thresh).center(cen_val),
                        '{}'.format(desc['amp_thresh']).center(cen_val)] if el != ' '*cen_val],

        # Footer
        '',
        '=' * cen_val
    ])

    return output


def gen_results_str_fm(fm):
    """Generate a string representation of model fit results.

    Parameters
    ----------
    fm : FOOOF object
        Object for which results are to be printed.
    """

    if not np.all(fm.background_params_):
        raise ValueError('Model fit has not been run - can not proceed.')

    # Set centering value.
    cen_val = 100

    # Create output string
    output = '\n'.join([

        # Header
        '=' * cen_val,
        '',
        ' FOOOF - PSD MODEL'.center(cen_val),
        '',

        # Frequency range and resolution
        'The input PSD was modelled in the frequency range: {} - {} Hz'.format(
            int(np.floor(fm.freq_range[0])), int(np.ceil(fm.freq_range[1]))).center(cen_val),
        'Frequency Resolution is {:1.2f} Hz'.format(fm.freq_res).center(cen_val),
        '',

        # Background parameters
        ('Background Parameters (offset, ' + ('knee, ' if fm.bg_use_knee else '') + \
           'slope): ').center(cen_val),
        ', '.join(['{:2.4f}'] * len(fm.background_params_)).format(
            *fm.background_params_).center(cen_val),
        '',

        # Oscillation parameters
        '{} oscillations were found:'.format(
            len(fm.oscillation_params_)).center(cen_val),
        *['CF: {:6.2f}, Amp: {:6.3f}, BW: {:5.2f}'.format(op[0], op[1], op[2]).center(cen_val) \
          for op in fm.oscillation_params_],
        '',

        # R^2 and error
        'R^2 of model fit is {:5.4f}'.format(fm.r2_).center(cen_val),
        'Root mean squared error of model fit is {:5.4f}'.format(
            fm.error_).center(cen_val),
        '',

        # Footer
        '=' * cen_val
    ])

    return output


def gen_results_str_fg(fg):
    """Generate a string representation of group fit results.

    Parameters
    ----------
    fg : FOOOFGroup() object
        Group object for which results are to be printed.
    """

    if not fg.group_results:
        raise ValueError('Model fit has not been run - can not proceed.')

    # Set centering value
    cen_val = 100

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
        '=' * cen_val,
        '',
        ' FOOOF - GROUP RESULTS'.center(cen_val),
        '',

        # Group information
        'Number of PSDs in the Group: {}'.format(len(fg.group_results)).center(cen_val),
        '',

        # Frequency range and resolution
        'The input PSDs were modelled in the frequency range: {} - {} Hz'.format(
            int(np.floor(fg.freq_range[0])), int(np.ceil(fg.freq_range[1]))).center(cen_val),
        'Frequency Resolution is {:1.2f} Hz'.format(fg.freq_res).center(cen_val),
        '',

        # Background parameters - knee fit status, and quick slope description
        'PSDs were fit {} a knee.'.format('with' if fg.bg_use_knee else 'without').center(cen_val),
        '',
        *[el for el in ['Background Knee Values'.center(cen_val),
                        'Min: {:6.2f}, Max: {:6.2f}, Mean: {:5.2f}'
                        .format(kns.min(), kns.max(), kns.mean()).center(cen_val)
                       ] if fg.bg_use_knee],
        'Background Slope Values'.center(cen_val),
        'Min: {:6.4f}, Max: {:6.4f}, Mean: {:5.4f}'
        .format(sls.min(), sls.max(), sls.mean()).center(cen_val),
        '',

        # Oscillation Parameters
        'In total {} oscillations were extracted from the group'
        .format(len(cens)).center(cen_val),
        '',

        # Fitting stats - error and r^2
        'Fitting Performance'.center(cen_val),
        '   R2s -  Min: {:6.4f}, Max: {:6.4f}, Mean: {:5.4f}'
        .format(r2s.min(), r2s.max(), r2s.mean()).center(cen_val),
        'Errors -  Min: {:6.4f}, Max: {:6.4f}, Mean: {:5.4f}'
        .format(errors.min(), errors.max(), errors.mean()).center(cen_val),
        '',

        # Footer
        '=' * cen_val
    ])

    return output
