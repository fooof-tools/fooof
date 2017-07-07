"""FOOOF!"""

import itertools
import numpy as np
import statsmodels.api as sm
from scipy.optimize import curve_fit

# TODO:
#  Build the 'optimize' step into the main fooof function
#  Add post-fit, pre-multifit merging of overlapping oscillations
#  Make I/O order for parameters consistent

# NOTE:
#  Quite sensitive to f_low. Fails to fit sometimes.

###################################################################################################
###################################################################################################
###################################################################################################

def fooof(frequency_vector, input_psd, frequency_range, number_of_gaussians, window_around_max):
    """Fit oscillations & one over f.

    NOTE:
    Right now function expects linear frequency and logged powers right? Not sure that's ideal.
        Suggest: Take both in linear space, big note that this is what's expected (like old foof)
    Seems to be a lot of outputs, not all are clearly useful in most scenarios.
        Suggest: Reorder: full fit 1st, freqs 2nd, maybe rest are optional?
        Suggest 2: How it a proper module, so we can call fooof.fit.full(), fooof.fit.background(), etc.

    Parameters
    ----------
    frequency_vector : 1d array
        Frequency values for the PSD.
    input_psd : 2d array
        Power spectral density values.
    frequency_range : list of [float, float]
        Desired frequency range to run FOOOF on.
    number_of_gaussians : int
        Maximum number of oscillations to attempt to fit.
    window_around_max : int
        Frequency window around center frequency to examine.

    Returns
    -------
    p_flat_real : 1d array
        xx
    frequency_vector : 1d array
        xx
    trimmed_psd : 1d array
        xx
    psd_fit : 1d array
        xx
    background_fit : 1d array
        xx
    gaussian_fit : list of list of float
        xx
    background_params : 1d array
        xx
    oscillation_params : list of list of float
        xx
    """

    # TODO: Fix size checking, decide and document conventions for inputs
    # check dimensions
    if input_psd.ndim > 2:
        raise ValueError("input PSD must be 1- or 2- dimensional")

    # outlier amplitude is also the minimum amplitude required for counting as an "oscillation"
    # this is express as percent relative maximum oscillation height
    threshold = 0.025
    
    # convert window_around_max to freq
    window_around_max = np.int(np.ceil(window_around_max/(frequency_vector[1]-frequency_vector[0])))

    # trim the PSD
    frequency_vector, foof_spec = trim_psd(input_psd, frequency_vector, frequency_range)

    # Check dimensions
    if np.shape(frequency_vector)[0] == np.shape(foof_spec)[0]:
        foof_spec = foof_spec.T

    # NOTE: Since all we do is average, what is the benefit of taking multiple PSDs?
    #   - Since we only ever fit 1, could add a note to average before FOOOF, if user wants

    # Average across all provided PSDs
    trimmed_psd = np.nanmean(foof_spec, 0)

    # if the slope of the fit at the beginning is positive, adjust freq range up
    beginning_slope = True
    edge_shift = 1
    while beginning_slope:
      # Average across all provided PSDs
      trimmed_psd = trimmed_psd[edge_shift:]
      frequency_vector = frequency_vector[edge_shift:]

      # fit in log-log space and flatten the PSD
      log_f = np.log10(frequency_vector)
      _, background_params = fit_one_over_f(log_f, trimmed_psd)
      fit_values = background_params[0] + (background_params[1]*(log_f)) + (background_params[2]*(log_f**2))
      p_flat = trimmed_psd - fit_values

      # remove outliers
      p_flat[p_flat < 0] = 0
      amplitude_threshold = np.max(p_flat) * threshold
      cutoff = p_flat <= (amplitude_threshold)
      f_ignore = frequency_vector[cutoff]
      p_ignore = trimmed_psd[cutoff]

      # refit the background, ignoring regions with large amplitudes
      # this assumes those large amplitude regions are oscillations, not background
      log_f_ignore = np.log10(f_ignore)
      _, background_params = fit_one_over_f(log_f_ignore, p_ignore)
      background_fit = background_params[0] + (background_params[1]*(log_f)) + (background_params[2]*(log_f**2))
      p_flat_real = trimmed_psd - background_fit
      amplitude_threshold = np.max(p_flat_real)*threshold

      p_flat_real[p_flat_real < 0] = 0
      p_flat_iteration = np.copy(p_flat_real)
      
      beginning_slope = background_fit[1] > background_fit[0]

    guess = np.empty((0, 3))
    gausi = 0
    while gausi <= number_of_gaussians:
        max_index = np.argmax(p_flat_iteration)
        max_amp = p_flat_iteration[max_index]
        amp_cut = 2 * np.median(p_flat_real)
        drop_cond1 = (max_index - window_around_max) <= frequency_range[0]
        drop_cond2 = (max_index + window_around_max) >= frequency_range[1]
        drop_criterion = drop_cond1 | drop_cond2
        if ~drop_criterion:
            if max_amp >= amp_cut:
                guess_freq = frequency_vector[max_index]
                guess_amp = max_amp
                guess_bw = 2.
                guess = np.vstack((guess, (guess_freq, guess_amp, guess_bw)))
                flat_range = ((max_index-window_around_max), (max_index+window_around_max))
                p_flat_iteration[flat_range[0]:flat_range[1]] = 0
        if drop_cond1:
            flat_range = (0, (max_index+window_around_max))
            p_flat_iteration[flat_range[0]:flat_range[1]] = 0
        if drop_cond2:
            flat_range = ((max_index-window_around_max), frequency_range[1])
            p_flat_iteration[flat_range[0]:flat_range[1]] = 0
        gausi += 1
    
    if len(guess) > 0:
      guess = list(itertools.chain.from_iterable(guess))
      num_of_oscillations = int(np.shape(guess)[0]/3)
      lo_bw = 0.5
      hi_bw = 5.
      lo_bound = frequency_range[0], 0, lo_bw
      hi_bound = frequency_range[1], np.inf, hi_bw      
      param_bounds = lo_bound*num_of_oscillations, hi_bound*num_of_oscillations      
      oscillation_params, _ = curve_fit(gaussian_function, frequency_vector, p_flat_real, p0=guess, maxfev=5000, bounds=param_bounds)



      bw_params = group_three(oscillation_params)
      bw_params = [item[2] for item in bw_params]
      keep_osc = (np.abs(np.subtract(bw_params,lo_bw))>10e-2) & \
                  (np.abs(np.subtract(bw_params,hi_bw))>10e-2)
      if ~np.all(keep_osc):
        guess = group_three(guess)
        to_remove = np.where(~keep_osc)[0]
        for i in range(np.size(to_remove)):
            del guess[to_remove[i]][:]
        guess = [x for x in guess if x]
        
        guess = list(itertools.chain.from_iterable(guess))
        num_of_oscillations = int(np.shape(guess)[0]/3)
        param_bounds = lo_bound*num_of_oscillations, hi_bound*num_of_oscillations
        oscillation_params, _ = curve_fit(gaussian_function, frequency_vector, p_flat_real, p0=guess, maxfev=5000, bounds=param_bounds)
      
      
      gaussian_fit = gaussian_function(frequency_vector, *oscillation_params)
      psd_fit = gaussian_fit + background_fit

    # logic handle background fit when there are no oscillations
    else:
        # just fit background without removing any windows
        log_f = np.log10(frequency_vector)
        _, background_params = fit_one_over_f(log_f, trimmed_psd)
        psd_fit = background_params[0] + (background_params[1]*(log_f)) + (background_params[2]*(log_f**2))

    return p_flat_real, frequency_vector, trimmed_psd, psd_fit, background_fit, gaussian_fit, background_params, oscillation_params


def trim_psd(input_psd, input_frequency_vector, frequency_range):
    """Extract PSD, and frequency vector, to desired frequency range.

    Parameters
    ----------
    input_psd : 1d array
        Power spectral density values.
    input_frequency_vector :
        Frequency values for the PSD.
    frequency_range : list of [float, float]
        Desired frequency range of PSD.

    Returns
    -------
    output_frequency_vector : 1d array
        Extracted frequency values for the PSD.
    trimmed_psd :
        Extracted power spectral density values.
    """

    idx = [get_index_from_vector(input_frequency_vector, freq) for freq in frequency_range]

    output_frequency_vector = input_frequency_vector[idx[0]:idx[1]]
    trimmed_psd = input_psd[idx[0]:idx[1], :]

    return output_frequency_vector, trimmed_psd


def get_index_from_vector(input_vector, element_value):
    """Returns index for input closest to desired element value.

    Parameters
    ----------
    input_vector : 1d array
        Vector of values to search through.
    element_value : float
        Value to search for in input vector.

    Returns
    -------
    idx : int
        Index closest to element value.
    """

    loc = input_vector - element_value
    idx = np.where(np.abs(loc) == np.min(np.abs(loc)))
    idx = idx[0][0]

    return idx


def fit_one_over_f(frequency_vector, trimmed_psd):
    """Fit the 1/f slope of PSD - does so like a 2nd order fit in

    Parameters
    ----------
    frequency_vector : 1d array
        Frequency values for the PSD.
    trimmed_psd : 1d array
        Power spectral density values.

    Returns
    -------
    fit_values : 1d array
        Values of fit slope.
    fit_parameters : 1d array
        Parameters of slope fit (length of 3).
    """

    # 2nd degree polynomial robust fit for first pass
    Xvar = np.column_stack((frequency_vector, frequency_vector**2))
    Xvar = sm.add_constant(Xvar)

    # logic in case RLM fails
    # TODO: choose fit model (based on data appropriateness and/or speed)
    try:
        mdl_fit = sm.RLM(trimmed_psd, Xvar, M=sm.robust.norms.HuberT()).fit()
    except:
        mdl_fit = sm.OLS(trimmed_psd, Xvar).fit()

    fit_values = mdl_fit.fittedvalues
    fit_parameters = mdl_fit.params

    return fit_values, fit_parameters


def gaussian_function(x, *params):
    """Gaussian function to use for fitting.

    Parameters
    ----------
    x :
        xx
    *params :
        xx

    Returns
    -------
    y :
        xx
    """

    y = np.zeros_like(x)

    for i in range(0, len(params), 3):

        ctr = params[i]
        amp = params[i+1]
        wid = params[i+2]

        y = y + amp * np.exp(-((x - ctr)/wid)**2)

    return y


def fit_gaussian(flattened_psd, frequency_vector, window_around_max):
    """Fit a gaussian to the largest peak in a (flattened) PSD.

    Parameters
    ----------
    flattened_psd : 1d array
        Power spectral density values.
    frequency_vector : 1d array
        Frequency values for the PSD.
    window_around_max : int
        Window (in Hz) around peak to fit gaussian to.

    Returns
    -------
    popt : 1d array
        Parameter values to define the fit gaussian (length 3).
    gaussian_fit : 1d array
        Values of the gaussian fit to the input (flattened & zeroed out) PSD.
    """

    # find the location and amplitude of the maximum of the flattened spectrum
    # this assumes that this value is the peak of the biggest oscillation
    max_index = np.argmax(flattened_psd)
    guess_freq = frequency_vector[max_index]

    # set everything that's not the biggest oscillation to zero
    p_flat_zeros = np.copy(flattened_psd)

    idx = [get_index_from_vector(frequency_vector, edge) for edge in
        [guess_freq-window_around_max, guess_freq+window_around_max]]

    # if the cf is near left edge, only flatten to the right
    if (guess_freq-window_around_max) < window_around_max:
        p_flat_zeros[idx[1]:] = 0
    # if the cf is near right edge, only flatten to the left
    elif (guess_freq+window_around_max) > (np.max(frequency_vector)-window_around_max):
        p_flat_zeros[0:idx[0]] = 0
    # otherwise flatten it all
    else:
        p_flat_zeros[0:idx[0]] = 0
        p_flat_zeros[idx[1]:] = 0

    # the first guess for the gaussian fit is the biggest oscillation
    guess = [guess_freq, np.max(p_flat_zeros), 2]
    guess = np.array(guess)
    popt, _ = curve_fit(gaussian_function, frequency_vector, p_flat_zeros, p0=guess, maxfev=5000)
    gaussian_fit = gaussian_function(frequency_vector, *popt)
    gaussian_fit = np.array(gaussian_fit)

    return popt, gaussian_fit

# decision criteria for keeping fitted oscillations
# amp has to be at least 1.645 * residual noise
# std of gaussian fit needs to not be too narrow...
# ... nor too wide
# and cf of oscillation can't be too close to edges,
#   else there's not enough infomation to make a good fit

def decision_criterion(oscillation_params, frequency_range):
    """Decide whether a potential oscillation fit meets criterion.

    Parameters
    ----------
    oscillation_params :
        xx
    frequency_range :
        xx

    Returns
    -------
    keep_parameter : boolean
        Whether the oscillation fit is deemed appropriate to keep.
    """

    edge_criteria = oscillation_params[1]*2
    keep_parameter = \
        (oscillation_params[2] < 5.) & \
        (oscillation_params[2] > 0.5) & \
        (oscillation_params[0] > (frequency_range[0]+edge_criteria)) & \
        (oscillation_params[0] < (frequency_range[1]-edge_criteria))

    return keep_parameter

def group_three(vec):
    """Takes array of inputs, groups by three."""

    return [list(vec[i:i+3]) for i in range(0, len(vec), 3)]

