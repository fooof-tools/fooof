"""Generate formatted strings for printing out information in report format."""

from itertools import chain

import numpy as np

from specparam.utils.select import list_insert
from specparam.utils.array import compute_arr_desc
from specparam.measures.properties import compute_presence
from specparam.version import __version__ as MODULE_VERSION
from specparam.reports.settings import LCV, SCV, DIVIDER

###################################################################################################
###################################################################################################

## GENERAL

def gen_issue_str(concise=False):
    """Generate a string representation of instructions to report an issue.

    Parameters
    ----------
    concise : bool, optional, default: False
        Whether to generate the string in concise mode.

    Returns
    -------
    str
        Formatted string of how to provide feedback.
    """

    str_lst = [
        'ISSUE REPORTING',
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
    ]

    return _format(str_lst, concise)


def gen_version_str(concise=False):
    """Generate a string representation of the current version of the module.

    Parameters
    ----------
    concise : bool, optional, default: False
        Whether to generate the string in concise mode.

    Returns
    -------
    str
        Formatted string of current version.
    """

    str_lst = [
        'CODE VERSION',
        '',
        '{}'.format(MODULE_VERSION),
    ]

    return _format(str_lst, concise)


def gen_methods_report_str(concise=False):
    """Generate a string representation of instructions for reporting on using the module.

    Parameters
    ----------
    concise : bool, optional, default: False
        Whether to generate the string in concise mode.

    Returns
    -------
    str
        Formatted string of instructions for methods reporting.
    """

    str_lst = [
        'REPORTING',
        '',
        'Reports using spectral parameterization should include (at minimum):',
        '',
        '- the code version that was used',
        '- the fit modes that were used',
        '- the algorithm & settings that were used',
        '- the frequency range that was fit',
    ]

    return _format(str_lst, concise)

## DATA

def gen_freq_range_str(model, concise=False):
    """Generate a string representation of the fit range that was used for the model.

    Parameters
    ----------
    model : SpectralModel or Spectral*Model
        Object to access settings from.
    concise : bool, optional, default: False
        Whether to generate the string in concise mode.

    Returns
    -------
    str
        String representation of the fit range.
        If fit range is not available, missing values will be set as 'XX'.
    """

    freq_range = model.data.freq_range if model.data.has_data else ('XX', 'XX')

    str_lst = [
        'FIT RANGE',
        '',
        'The model was fit from {} to {} Hz.'.format(*freq_range),
    ]

    return _format(str_lst, concise)


def gen_data_str(data, concise=False):
    """Generate a string representation summarizing current data.

    Parameters
    ----------
    data : Data
        Data object to summarize data for.
        Can also be any derived data object (e.g. Data2D).
    concise : bool, optional, default: False
        Whether to generate the string in concise mode.

    Returns
    -------
    str
        Formatted string of data summary.
    """

    str_lst = ['DATA INFORMATION', '']

    if not data.has_data:

        no_data_str = "No data currently loaded in the object."
        str_lst.append(no_data_str)

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

        str_lst_add = [
            'The data object contains {}'.format(n_spectra_str),
            'with a frequency range of {} Hz'.format(data.freq_range),
            'and a frequency resolution of {} Hz.'.format(data.freq_res),
        ]

        str_lst.extend(str_lst_add)

    return _format(str_lst, concise)


## MODES

def gen_mode_str_lst(mode, description=False, concise=False):
    """Generate a list of string components for representating a mode.

    Parameters
    ----------
    mode : Mode
        Mode object.
    description : bool, optional, default: False
        Whether to also print out a description of the fit mode.
    concise : bool, optional, default: False
        Whether to generate the string in concise mode.

    Returns
    -------
    lst
        List of string elements for a string representation of a mode.
    """

    str_lst = [mode.component.capitalize() + ' Mode : ' + mode.name]
    if description:
        str_lst.append(mode.description)

    return str_lst


def gen_mode_str(mode, description=False, concise=False):
    """Generate a string representation of a fit mode.

    Parameters
    ----------
    mode : Mode
        Mode definition.
    description : bool, optional, default: False
        Whether to also print out a description the fit mode.
    concise : bool, optional, default: False
        Whether to generate the string in concise mode.

    Returns
    -------
    str
        Formatted string of fit modes.
    """

    str_lst = gen_mode_str_lst(mode, description, concise)

    return _format(['FIT MODE', ''] + str_lst, concise)


def gen_modes_str(modes, description=False, concise=False):
    """Generate a string representation of fit modes.

    Parameters
    ----------
    modes : Modes
        Modes definition.
    description : bool, optional, default: False
        Whether to also print out a description of the fit modes.
    concise : bool, optional, default: False
        Whether to generate the string in concise mode.

    Returns
    -------
    str
        Formatted string of fit modes.
    """


    str_lst = []
    for mode in [modes.aperiodic, modes.periodic]:
        str_lst.extend(gen_mode_str_lst(mode, description, concise))

    return _format(['FIT MODES', ''] + str_lst, concise)


def gen_params_str(params, description=False, concise=False):
    """Generate a string representation of the parameters of a fit mode.

    Parameters
    ----------
    params : ParamDefinition
        Parameter definition object for a fit mode
    description : bool, optional, default: False
        Whether to also print out a description of the fit mode parameters.
    concise : bool, optional, default: False
        Whether to print the report in concise mode.

    Returns
    -------
    str
        Formatted string of the fit mode parameters description.
    """

    str_lst = [
        'FIT MODE PARAMETERS',
        '',
    ]

    for param, desc in params.descriptions.items():
        if description:
            param = param + ' : {}'.format(desc)
        str_lst.append(param)

    return _format(str_lst, concise)

## ALGORITHM / SETTINGS

def gen_settings_str(algorithm, description=False, concise=False):
    """Generate a string representation of algorithm and fit settings.

    Parameters
    ----------
    algorithm : Algorithm
        Algorithm object.
    description : bool, optional, default: False
        Whether to also print out a description of the settings.
    concise : bool, optional, default: False
        Whether to generate the string in concise mode.

    Returns
    -------
    str
        Formatted string of current settings.
    """

    # Create output string - header
    str_lst = [
        'ALGORITHM',
        algorithm.name,
    ]

    if description:
        str_lst.append(algorithm.description)

    str_lst.extend([
        '',
        'ALGORITHM SETTINGS',
    ])

    # Loop through algorithm settings, and add information
    for name in algorithm.settings.names:
        str_lst.append(name + ' : ' + str(getattr(algorithm.settings, name)))
        if description:
            str_lst.append(algorithm.public_settings.descriptions[name].split('\n ')[0])

    return _format(str_lst, concise)


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
    str
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


## BANDS

def gen_bands_str(bands, concise=False):
    """Generate a string representation of a set of bands definitions.

    Parameters
    ----------
    bands : Bands
        Bands definition.
    concise : bool, optional, default: False
        Whether to generate the string in concise mode.

    Returns
    -------
    str
        Formatted string of bands definition.
    """

    str_lst = [
        'BANDS DEFINITION',
        '',
    ]

    for label, definition in bands.bands.items():
        str_lst.append('{}: {}'.format(label, definition))

    return _format(str_lst, concise)


## METRICS

def gen_metric_str_lst(metric, description=False, concise=False):
    """Generate a list of string components for representating a metric.

    Parameters
    ----------
    metrics : Metric
        Metric object.
    description : bool, optional, default: False
        Whether to also print out a description of the metric.
    concise : bool, optional, default: False
        Whether to generate the string in concise mode.

    Returns
    -------
    lst
        List of string elements for a string representation of a metric.
    """

    str_lst = [metric.label, metric.description] if description else [metric.label]

    return str_lst


def gen_metric_str(metric, description=False, concise=False):
    """Generate a string representation of a metric.

    Parameters
    ----------
    metrics : Metric
        Metric object.
    description : bool, optional, default: False
        Whether to also print out a description of the settings.
    concise : bool, optional, default: False
        Whether to generate the string in concise mode.

    Returns
    -------
    str
        Formatted string of metric.
    """

    str_lst = gen_metric_str_lst(metric, description, concise)

    return _format(['CURRENT METRIC', ''] + str_lst, concise)


def gen_metrics_str(metrics, description=False, concise=False):
    """Generate a string representation of a set of metrics.

    Parameters
    ----------
    metrics : Metrics
        Metrics object.
    description : bool, optional, default: False
        Whether to also print out a description of the settings.
    concise : bool, optional, default: False
        Whether to generate the string in concise mode.

    Returns
    -------
    str
        Formatted string of metrics.
    """

    str_lst = []
    for metric in metrics.metrics:
        str_lst.extend(gen_metric_str_lst(metric, description, concise))

    return _format(['CURRENT METRICS', ''] + str_lst, concise)


## MODEL OBJECTS

def gen_model_results_str(model, concise=False):
    """Generate a string representation of model fit results.

    Parameters
    ----------
    model : SpectralModel
        Object to access results from.
    concise : bool, optional, default: False
        Whether to generate the string in concise mode.

    Returns
    -------
    str
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

        'SPECTRUM MODEL RESULTS',
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
    ]

    return _format(str_lst, concise)


def gen_group_results_str(group, concise=False):
    """Generate a string representation of group fit results.

    Parameters
    ----------
    group : SpectralGroupModel
        Object to access results from.
    concise : bool, optional, default: False
        Whether to generate the string in concise mode.

    Returns
    -------
    str
        Formatted string of results.
    """

    if not group.results.has_model:
        return _no_model_str(concise)

    str_lst = [

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
            ])

    return _format(str_lst, concise)


def gen_time_results_str(time, concise=False):
    """Generate a string representation of time fit results.

    Parameters
    ----------
    time : SpectralTimeModel
        Object to access results from.
    concise : bool, optional, default: False
        Whether to generate the string in concise mode.

    Returns
    -------
    str
        Formatted string of results.
    """

    if not time.results.has_model:
        return _no_model_str(concise)

    # Set up string for peak parameters
    peak_str = '{:>8s} - ' + ', '.join(['{:s}:'.format(el.upper()) + \
        ' {:6.2f}' for el in time.modes.periodic.params.labels]) + \
        ', Presence: {:3.1f}%'

    str_lst = [

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
    ]

    return _format(str_lst, concise)


def gen_event_results_str(event, concise=False):
    """Generate a string representation of event fit results.

    Parameters
    ----------
    event : SpectralTimeEventModel
        Object to access results from.
    concise : bool, optional, default: False
        Whether to generate the string in concise mode.

    Returns
    -------
    str
        Formatted string of results.
    """

    if not event.results.has_model:
        return _no_model_str(concise)

    # Set up string for peak parameters
    peak_str = '{:>8s} - ' + ', '.join(['{:s}:'.format(el.upper()) + \
        ' {:5.2f}' for el in event.modes.periodic.params.labels]) + \
        ', Presence: {:3.1f}%'

    str_lst = [

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
    ]

    return _format(str_lst, concise)


## HELPER SUB-FUNCTIONS FOR MODEL REPORT STRINGS

def _report_str_algo(model):
    """Create string about algorithm.

    Parameters
    ----------
    model : SpectralModel
        Object to access information from.

    Returns
    -------
    str
        Report string about algorithm.
    """

    output = 'The model was fit with the \'{}\' algorithm'.format(model.algorithm.name)

    return output


def _report_str_model(model):
    """Create string about data.

    Parameters
    ----------
    model : SpectralModel
        Object to access information from.

    Returns
    -------
    str
        Report string about data.
    """

    output = \
        'Model was fit to the {}-{} Hz frequency range '.format(
            int(np.floor(model.data.freq_range[0])),
            int(np.ceil(model.data.freq_range[1]))) + \
        'with {:1.2f} Hz resolution'.format(model.data.freq_res)

    return output


def _report_str_n_null(model):
    """Create string on number of failed fit / null models.

    Parameters
    ----------
    model : SpectralModel
        Object to access information from.

    Returns
    -------
    str
        Report string about number of failed fits.
    """

    output = \
            [el for el in ['{} power spectra failed to fit'.format(\
            model.results.n_null)] if model.results.n_null]

    return output


def _no_model_str(concise=False):
    """Creates a null report, for use if the model fit failed, or is unavailable.

    Parameters
    ----------
    concise : bool, optional, default: False
        Whether to generate the string in concise mode.

    Returns
    -------
    str
        Report string for a null model.
    """

    str_lst = [
        'Model fit has not been run, or fitting was unsuccessful.',
    ]

    return _format(str_lst, concise)


## UTILITIES

def _format(str_lst, concise):
    """Format a string for printing.

    Parameters
    ----------
    str_lst : list of str
        List containing all elements for the string, each element representing a line.
    concise : bool, optional, default: False
        Whether to format the string in concise mode.

    Returns
    -------
    output : str
        Formatted string, ready for printing.
    """

    str_template = [DIVIDER, '', '', DIVIDER]
    str_lst = list_insert(str_template, str_lst, 2)

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
