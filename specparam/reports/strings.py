"""Formatted strings for printing out model and fit related information."""

from itertools import chain

import numpy as np

from specparam.utils.array import compute_arr_desc
from specparam.measures.properties import compute_presence
from specparam.version import __version__ as MODULE_VERSION
from specparam.reports.settings import LCV, SCV, DIVIDER

###################################################################################################
###################################################################################################

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

        DIVIDER,
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

        DIVIDER,
    ]

    output = _format(str_lst, concise)

    return output


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

        DIVIDER,
        '',
        'CODE VERSION',
        '',
        '{}'.format(MODULE_VERSION),
        '',
        DIVIDER,

    ]

    output = _format(str_lst, concise)

    return output


def gen_data_str(data, concise=False):
    """Generate a string representation summarizing current data.

    Parameters
    ----------
    data : Data
        Data object to summarize data for.
        Can also be any derived data object (e.g. Data2D).
    concise : bool, optional, default: False
        Whether to print the report in concise mode.

    Returns
    -------
    output : str
        Formatted string of data summary.
    """

    if not data.has_data:

        no_data_str = "No data currently loaded in the object."
        str_lst = [DIVIDER,'', no_data_str, '', DIVIDER]

    else:

        # Get number of spectra, checking attributes for {Data3D, Data2DT, Data2D, Data}
        if getattr(data, 'n_events', None):
            n_spectra_str = '{} spectrograms with {} windows each'.format(\
                data.n_events, data.n_time_windows)
        elif getattr(data, 'n_time_windows', None):
            n_spectra_str = '1 spectrogram with {} windows'.format(data.n_time_windows)
        elif getattr(data, 'n_spectra', None):
            n_spectra_str = '{} power spectra'.format(data.n_spectra)
        else:
            n_spectra_str = '1 power spectrum'

        str_lst = [

            DIVIDER,
            '',
            'The data object contains {}'.format(n_spectra_str),
            'with a frequency range of {} Hz'.format(data.freq_range),
            'and a frequency resolution of {} Hz.'.format(data.freq_res),
            '',
            DIVIDER,
        ]

    output = _format(str_lst, concise)

    return output


def gen_modes_str(modes, description=False, concise=False):
    """Generate a string representation of fit modes.

    Parameters
    ----------
    modes : Modes
        Modes definition.
    description : bool, optional, default: False
        Whether to also print out a description of the fit modes.
    concise : bool, optional, default: False
        Whether to print the report in concise mode.

    Returns
    -------
    output : str
        Formatted string of fit modes.
    """

    desc = {
        'aperiodic_mode' : 'The approach taken for fitting the aperiodic component.',
        'periodic_mode'  : 'The approach taken for fitting the periodic component.',
    }

    # Clear description for printing, if not requested
    if not description:
        desc = {k : '' for k, v in desc.items()}

    # Create output string
    str_lst = [

        DIVIDER,
        '',
        'FIT MODES',
        '',
        # Settings - include descriptions if requested
        *[el for el in ['Periodic Mode : {}'.format(modes.periodic.name),
                        '{}'.format(desc['aperiodic_mode']),
                        'Aperiodic Mode : {}'.format(modes.aperiodic.name),
                        '{}'.format(desc['aperiodic_mode'])] if el != ''],
        '',
        DIVIDER,
    ]

    output = _format(str_lst, concise)

    return output


def gen_settings_str(algorithm, description=False, concise=False):
    """Generate a string representation of algorithm and fit settings.

    Parameters
    ----------
    algorithm : Algorithm
        Algorithm object.
    description : bool, optional, default: False
        Whether to also print out a description of the settings.
    concise : bool, optional, default: False
        Whether to print the report in concise mode.

    Returns
    -------
    output : str
        Formatted string of current settings.
    """

    # Create output string - header
    str_lst = [
        DIVIDER,
        '',
        'ALGORITHM: {}'.format(algorithm.name),
    ]

    if description:
        str_lst.append(algorithm.description)

    str_lst.extend([
        '',
        'ALGORITHM SETTINGS',
        '',
    ])

    # Loop through algorithm settings, and add information
    for name in algorithm.settings.names:
        str_lst.append(name + ' : ' + str(getattr(algorithm.settings, name)))
        if description:
            str_lst.append(algorithm.public_settings.descriptions[name].split('\n ')[0])

    str_lst.extend([
        '',
        DIVIDER,
    ])

    output = _format(str_lst, concise)

    return output


def gen_metrics_str(metrics, description=False, concise=False):
    """Generate a string representation of a set of metrics.

    Parameters
    ----------
    metrics : Metrics
        Metrics object.
    description : bool, optional, default: False
        Whether to also print out a description of the settings.
    concise : bool, optional, default: False
        Whether to print the report in concise mode.

    Returns
    -------
    output : str
        Formatted string of metrics.
    """

    if description:
        prints = [(metric.label, metric.description) for metric in metrics.metrics]
        prints = list(chain(*prints))
    else:
        prints = [metric.label for metric in metrics.metrics]

    str_lst = [
        DIVIDER,
        '',
        'CURRENT METRICS',
        '',
        *[el for el in prints],
        '',
        DIVIDER,
    ]

    output = _format(str_lst, concise)

    return output


def gen_freq_range_str(model, concise=False):
    """Generate a string representation of the fit range that was used for the model.

    Parameters
    ----------
    model : SpectralModel or Spectral*Model
        Object to access settings from.
    concise : bool, optional, default: False
        Whether to print the report in concise mode.

    Notes
    -----
    If fit range is not available, will print out 'XX' for missing values.
    """

    freq_range = model.data.freq_range if model.data.has_data else ('XX', 'XX')

    str_lst = [

        DIVIDER,
        '',
        'FIT RANGE',
        '',
        'The model was fit from {} to {} Hz.'.format(*freq_range),
        '',
        DIVIDER,
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

        DIVIDER,
        '',
        'REPORTING',
        '',
        'Reports using spectral parameterization should include (at minimum):',
        '',
        '- the code version that was used',
        '- the fit modes that were used',
        '- the algorithm & settings that were used',
        '- the frequency range that was fit',
        '',
        DIVIDER,
    ]

    output = _format(str_lst, concise)

    return output


def gen_methods_text_str(model=None):
    """Generate a string representation of a template methods report.

    Parameters
    ----------
    model : SpectralModel or Spectral*Model, optional
        A model object with settings information available.
        If None, the text is returned as a template, without values.
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
    if not model.results.has_model:
        return _no_model_str(concise)

    # Set up string for peak parameters
    peak_str = ', '.join(['{:s}:'.format(el.upper()) + \
        ' {:6.2f}' for el in model.modes.periodic.params.labels])

    # Create the formatted strings for printing
    str_lst = [

        DIVIDER,
        '',
        'POWER SPECTRUM MODEL',
        '',

        # Fit algorithm & data overview
        _report_str_algo(model),
        _report_str_model(model),
        '',

        'Aperiodic Parameters (\'{}\' mode)'.format(model.modes.aperiodic.name),
        '(' + ', '.join(model.modes.aperiodic.params.labels) + ')',
        ', '.join(['{:2.4f}'] * \
            len(model.results.params.aperiodic.params)).format(\
                *model.results.params.aperiodic.params),
        '',

        'Peak Parameters (\'{}\' mode) {} peaks found'.format(\
            model.modes.periodic.name, model.results.n_peaks),
        *[peak_str.format(*op) for op in model.results.params.periodic.params],
        '',

        'Model metrics:',
        *['{:>18s} is {:1.4f} {:8s}'.format('{:s} ({:s})'.format(*key.split('_')), res, ' ') \
            for key, res in model.results.metrics.results.items()],
        '',

        DIVIDER,
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
    """

    if not group.results.has_model:
        return _no_model_str(concise)

    str_lst = [

        DIVIDER,
        '',
        'GROUP SPECTRAL MODEL RESULTS ({} spectra)'.format(len(group.results.group_results)),
        *_report_str_n_null(group),
        '',

        # Fit algorithm & data overview
        _report_str_algo(group),
        _report_str_model(group),
        '',

        'Aperiodic Parameters (\'{}\' mode)'.format(group.modes.aperiodic.name),
        *[el for el in [\
            '{:8s} - Min: {:6.2f}, Max: {:6.2f}, Mean: {:5.2f}'.format(label, \
                *compute_arr_desc(group.results.get_params('aperiodic', label))) \
                    for label in group.modes.aperiodic.params.labels]],
        '',

        'Peak Parameters (\'{}\' mode) {} total peaks found'.format(\
            group.modes.periodic.name, sum(group.results.n_peaks)),
        '',
    ]

    if len(group.results.metrics) > 0:
        str_lst.extend([
            'Model metrics:',
            *['{:>18s} -  Min: {:6.3f}, Max: {:6.3f}, Mean: {:5.3f}'.format(\
                '{:s} ({:s})'.format(*label.split('_')),
                *compute_arr_desc(group.results.get_metrics(label))) \
                    for label in group.results.metrics.labels],
            '',
            ])

    str_lst.extend([
        DIVIDER,
    ])

    output = _format(str_lst, concise)

    return output


def gen_time_results_str(time, concise=False):
    """Generate a string representation of time fit results.

    Parameters
    ----------
    time : SpectralTimeModel
        Object to access results from.
    concise : bool, optional, default: False
        Whether to print the report in concise mode.

    Returns
    -------
    output : str
        Formatted string of results.
    """

    if not time.results.has_model:
        return _no_model_str(concise)

    # Set up string for peak parameters
    peak_str = '{:>8s} - ' + ', '.join(['{:s}:'.format(el.upper()) + \
        ' {:6.2f}' for el in time.modes.periodic.params.labels]) + \
        ', Presence: {:3.1f}%'

    str_lst = [

        DIVIDER,
        '',
        'TIME SPECTRAL MODEL RESULTS ({} time windows)'.format(time.data.n_time_windows),
        *_report_str_n_null(time),
        '',

        # Fit algorithm & data overview
        _report_str_algo(time),
        _report_str_model(time),
        '',

        'Aperiodic Parameters (\'{}\' mode)'.format(time.modes.aperiodic.name),
        *[el for el in [\
            '{:8s} - Min: {:6.2f}, Max: {:6.2f}, Mean: {:5.2f}'.format(label, \
                *compute_arr_desc(time.results.time_results[label])) \
                    for label in time.modes.aperiodic.params.labels]],
        '',

        'Peak Parameters (\'{}\' mode) - mean values across windows'.format(\
            time.modes.periodic.name),
        *[peak_str.format(*[band_label] + \
            list(_compute_avg_over_time(time.results.time_results, band_label).values()) + \
            [compute_presence(time.results.time_results[\
                band_label + '_' + time.modes.periodic.params.labels[0]], output='percent')]) \
            for band_label in time.results.bands.labels],
        '',

        'Model metrics (values across windows):',
        *['{:>18s} -  Min: {:6.3f}, Max: {:6.3f}, Mean: {:5.3f}'.format(\
            '{:s} ({:s})'.format(*key.split('_')),
            *compute_arr_desc(time.results.time_results[key])) \
                for key in time.results.metrics.results],
        '',

        DIVIDER,
    ]

    output = _format(str_lst, concise)

    return output


def gen_event_results_str(event, concise=False):
    """Generate a string representation of event fit results.

    Parameters
    ----------
    event : SpectralTimeEventModel
        Object to access results from.
    concise : bool, optional, default: False
        Whether to print the report in concise mode.

    Returns
    -------
    output : str
        Formatted string of results.
    """

    if not event.results.has_model:
        return _no_model_str(concise)

    # Set up string for peak parameters
    peak_str = '{:>8s} - ' + ', '.join(['{:s}:'.format(el.upper()) + \
        ' {:5.2f}' for el in event.modes.periodic.params.labels]) + \
        ', Presence: {:3.1f}%'

    str_lst = [

        DIVIDER,
        '',
        'EVENT SPECTRAL MODEL RESULTS ({} events with {} time windows)'.format(\
            event.data.n_events, event.data.n_time_windows),
        *_report_str_n_null(event),
        '',

        # Fit algorithm & data overview
        _report_str_algo(event),
        _report_str_model(event),
        '',

        'Aperiodic Parameters (\'{}\' mode)'.format(event.modes.aperiodic.name),
        *[el for el in [\
            '{:8s} - Min: {:6.2f}, Max: {:6.2f}, Mean: {:5.2f}'.format(label, \
                *compute_arr_desc(np.mean(event.results.event_time_results[label]))) \
                    for label in event.modes.aperiodic.params.labels]],
        '',

        'Peak Parameters (\'{}\' mode) - mean values across windows'.format(\
            event.modes.periodic.name),
        *[peak_str.format(*[band_label] + \
            list(_compute_avg_over_time(event.results.event_time_results, band_label).values()) + \
            [compute_presence(event.results.event_time_results[\
                band_label + '_' + event.modes.periodic.params.labels[0]],
                average=True, output='percent')]) \
            for band_label in event.results.bands.labels],
        '',

        'Model metrics (values across events):',
        *['{:>18s} -  Min: {:6.3f}, Max: {:6.3f}, Mean: {:5.3f}'.format(\
            '{:s} ({:s})'.format(*key.split('_')),
            *compute_arr_desc(np.mean(event.results.event_time_results[key], 1))) \
                for key in event.results.metrics.results],
        '',
        DIVIDER,
    ]

    output = _format(str_lst, concise)

    return output


## HELPER SUB-FUNCTIONS FOR MODEL REPORT STRINGS

def _report_str_algo(model):
    """Create report string section to report on algorithm."""

    output = 'The model was fit with the \'{}\' algorithm'.format(model.algorithm.name)

    return output


def _report_str_model(model):
    """Create report string section to report on data."""

    output = \
        'Model was fit to the {}-{} Hz frequency range '.format(
            int(np.floor(model.data.freq_range[0])),
            int(np.ceil(model.data.freq_range[1]))) + \
        'with {:1.2f} Hz resolution'.format(model.data.freq_res)

    return output


def _report_str_n_null(model):
    """Create report string section to on number of failed fit / null models."""

    output = \
            [el for el in ['{} power spectra failed to fit'.format(\
            model.results.n_null)] if model.results.n_null]

    return output


def _no_model_str(concise=False):
    """Creates a null report, for use if the model fit failed, or is unavailable.

    Parameters
    ----------
    concise : bool, optional, default: False
        Whether to print the report in a concise mode, or not.
    """

    str_lst = [
        DIVIDER,
        '',
        'Model fit has not been run, or fitting was unsuccessful.',
        '',
        DIVIDER,
    ]

    output = _format(str_lst, concise)

    return output


## UTILITIES

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


def _compute_avg_over_time(results, subselect=None):
    """Compute average across results over time array.

    Parameters
    ----------
    results : dict of array
        Dictionary with array entries.
    subselect : str, optional
        If provided, subselects keys containing 'subselect' from results.

    Returns
    -------
    out : dict of array
        Dictionary with array entries.
    """

    if subselect:
        results = {key : vals for key, vals in results.items() if subselect in key}

    out = {}
    for label in results.keys():
        out[label] = np.nanmean(results[label])

    return out
