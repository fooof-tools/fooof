"""FOOOF!"""
"""DEPENDENCIES: SCIPY >0.19"""

import itertools
import numpy as np
# import statsmodels.api as sm
from scipy.optimize import curve_fit

# TODO:
#  Build the 'optimize' step into the main fooof function
#  Add post-fit, pre-multifit merging of overlapping oscillations
#  Make I/O order for parameters consistent

###################################################################################################
###################################################################################################
###################################################################################################

def fooof(frequency_vector, input_psd, frequency_range, number_of_gaussians, window_around_max, bandwidth_limits):
    """Fit oscillations & one over f.

    NOTE:
    Right now function expects linear frequency and logged powers right? Not sure that's ideal.
        Suggest: Take both in linear space, big note that this is what's expected (like old foof)
    Seems to be a lot of outputs, not all are clearly useful in most scenarios.
        Suggest: Reorder: full fit 1st, freqs 2nd, maybe rest are optional?
        Suggest 2: Have it be a proper module, so we can call fooof.fit.full(), fooof.fit.background(), etc.

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
    param_bounds = (-np.inf, -8, -np.inf), (np.inf, 0, 0)
    
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
    
    # fit the background 1/f
    background_params, background_fit = clean_background_fit(frequency_vector, trimmed_psd, threshold, param_bounds)
    p_flat_real = trimmed_psd - background_fit
    p_flat_real[p_flat_real < 0] = 0
    p_flat_iteration = np.copy(p_flat_real)

    guess = np.empty((0, 3))
    gausi = 0
    while gausi < number_of_gaussians:
        max_index = np.argmax(p_flat_iteration)
        max_amp = p_flat_iteration[max_index]

        # trim gaussians at the edges of the PSD
        # trimming these here dramatically speeds things up, since the trimming later...
        # ... requires doing the gaussian curve fitting, which is slooow
        cut_freq = [0,0]
        cut_freq[0] = np.int(np.ceil(frequency_range[0]/(frequency_vector[1]-frequency_vector[0])))
        cut_freq[1] = np.int(np.ceil(frequency_range[1]/(frequency_vector[1]-frequency_vector[0])))
        drop_cond1 = (max_index - window_around_max) <= cut_freq[0]
        drop_cond2 = (max_index + window_around_max) >= cut_freq[1]
        drop_criterion = drop_cond1 | drop_cond2
        if ~drop_criterion:
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
      # remove low amplitude gaussians
      amp_cut =  0.5 * np.var(p_flat_real)
      amp_params = [item[1] for item in guess]
      keep_osc = amp_params > amp_cut
      
      guess = [d for (d, remove) in zip(guess, keep_osc) if remove]
      num_of_oscillations = int(np.shape(guess)[0])
      guess = list(itertools.chain.from_iterable(guess))
      
      lo_bound = frequency_range[0], 0, bandwidth_limits[0]
      hi_bound = frequency_range[1], np.inf, bandwidth_limits[1]      
      param_bounds = lo_bound*num_of_oscillations, hi_bound*num_of_oscillations 
      try:
        oscillation_params, _ = curve_fit(gaussian_function, frequency_vector, p_flat_real, p0=guess, maxfev=5000, bounds=param_bounds)
      except:
        pass

      keep_osc = False
      while ~np.all(keep_osc):
        # remove gaussians by bandwidth
        osc_params = group_three(oscillation_params)
        cf_params = [item[0] for item in osc_params]
        bw_params = [item[2] for item in osc_params]
        keep_osc = decision_criterion(cf_params, bw_params, frequency_range, bandwidth_limits)
        guess = [d for (d, remove) in zip(osc_params, keep_osc) if remove]
        if len(guess) > 0:
          num_of_oscillations = int(np.shape(guess)[0])
          guess = list(itertools.chain.from_iterable(guess))
          param_bounds = lo_bound*num_of_oscillations, hi_bound*num_of_oscillations
          oscillation_params, _ = curve_fit(gaussian_function, frequency_vector, p_flat_real, p0=guess, maxfev=5000, bounds=param_bounds)
          
        # logic hto andle background fit when there are no oscillations
        else:
          keep_osc = True
          oscillation_params = []

      if len(oscillation_params) > 0:
        gaussian_fit = gaussian_function(frequency_vector, *oscillation_params)
        psd_fit = gaussian_fit + background_fit
      else:
        log_f = np.log10(frequency_vector)
        psd_fit, _ = quick_background_fit(log_f, trimmed_psd, param_bounds)
        gaussian_fit = np.zeros_like(frequency_vector)
        oscillation_params = []
        
    # logic handle background fit when there are no oscillations
    else:
      log_f = np.log10(frequency_vector)
      psd_fit, _ = quick_background_fit(log_f, trimmed_psd, param_bounds)
      gaussian_fit = np.zeros_like(frequency_vector)
      oscillation_params = []

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


def linear_function(x, *params):
  """Linear function to use for quick fitting 1/f to estimate parameters.

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
  offset = params[0]
  slope = params[1]
  y = y + offset + (x*slope)
  return y


def quadratic_function(x, *params):
  """Quadratic function to use for better fitting 1/f.

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
  offset = params[0]
  slope = params[1]
  curve = params[2]
  y = y + offset + (x*slope) + ((x**2)*curve)
  return y

def quick_background_fit(frequency_vector, trimmed_psd, param_bounds):
  guess = [trimmed_psd[0], -2]
  guess = np.array(guess)
  popt, _ = curve_fit(linear_function, frequency_vector, trimmed_psd, p0=guess)
  guess = [popt[0], popt[1], 0]
  guess = np.array(guess)
  popt, _ = curve_fit(quadratic_function, frequency_vector, trimmed_psd, p0=guess, bounds=param_bounds)
  psd_fit = quadratic_function(frequency_vector, *popt)
  
  return psd_fit, popt

def clean_background_fit(frequency_vector, trimmed_psd, threshold, param_bounds):
  """Fit the 1/f slope of PSD using a linear and then quadratic fit

  Parameters
  ----------
  frequency_vector : 1d array
      Frequency values for the PSD.
  trimmed_psd : 1d array
      Power spectral density values.
  threshold : scalar
      Threshold for removing outliers during fitting.

  Returns
  -------
  background_params : 1d array
    Parameters of slope fit (length of 3: offset, slope, curvature).
  background_fit : 1d array
      Values of fit slope.
  """
  log_f = np.log10(frequency_vector)
  quadratic_fit, popt = quick_background_fit(frequency_vector, trimmed_psd, param_bounds)
  p_flat = trimmed_psd - quadratic_fit

  # remove outliers
  p_flat[p_flat < 0] = 0
  amplitude_threshold = np.max(p_flat) * threshold
  cutoff = p_flat <= (amplitude_threshold)
  log_f_ignore = log_f[cutoff]
  p_ignore = trimmed_psd[cutoff]

  guess = [popt[0], popt[1], popt[2]]
  guess = np.array(guess)
  # note param_bounds here carry over from above quadratic fit
  background_params, _ = curve_fit(quadratic_function, log_f_ignore, p_ignore, p0=guess, bounds=param_bounds)
  background_fit = background_params[0] + (background_params[1]*(log_f)) + (background_params[2]*(log_f**2))

  return background_params, background_fit


# decision criteria for keeping fitted oscillations
# std of gaussian fit needs to not be too narrow...
# ... nor too wide
# and cf of oscillation can't be too close to edges,
#   else there's not enough infomation to make a good fit

def decision_criterion(cf_params, bw_params, frequency_range, bandwidth_limits):
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
    lo_bw = bandwidth_limits[0]
    hi_bw = bandwidth_limits[1]
    keep_parameter = \
        (np.abs(np.subtract(cf_params, frequency_range[0]))>2) & \
        (np.abs(np.subtract(cf_params, frequency_range[1]))>2) & \
        (np.abs(np.subtract(bw_params, lo_bw))>10e-4) & \
        (np.abs(np.subtract(bw_params, hi_bw))>10e-4)

    return keep_parameter

def group_three(vec):
    """Takes array of inputs, groups by three."""

    return [list(vec[i:i+3]) for i in range(0, len(vec), 3)]

