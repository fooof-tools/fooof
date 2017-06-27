import numpy as np

def bw_to_std(bandwidth):
    standard_deviation = bandwidth / (2 * np.sqrt(2 * np.log2(2)))
    return standard_deviation

def std_to_bw(standard_deviation):
    bandwidth = standard_deviation * (2 * np.sqrt(2 * np.log2(2)))
    return bandwidth

def make_gaussian(frequency_vector, oscillation_params):
    oscillation_params[2] = bw_to_std(oscillation_params[2])
    gaussian = (oscillation_params[0] *
        np.exp(-(((frequency_vector-oscillation_params[1])**2)/(2*(oscillation_params[2]**2)))))
    return gaussian

def simulate_neural_spectra(frequency_vector, slope_params, oscillation_params, noise):
    """
    Simulate oscillatory power specetra as a funciton of 1/f plus oscillations and noise

    Args:
      frequency_vector: vector of frequency indices
      slope_params: polynomial in the form of [offset, x, x**2, ... x**i]
      oscillation_params: array of oscillation parameters (amplitude, center frequency, and bandwidth)
          where each row is a separate oscillation
      noise: vector of noise to add, in the form of [mu, sigma]

    Returns:
      simulated_spectrum: vector containing simulated power at each frequency
    """

    frequency_vector = np.asarray(frequency_vector)
    slope_params = np.asarray(slope_params)
    oscillation_params = np.asarray(oscillation_params)

    # Return nan if any list is empty
    if not np.any(np.isfinite(frequency_vector)):
        return np.nan
    if not np.any(np.isfinite(slope_params)):
        return np.nan
    if not np.any(np.isfinite(oscillation_params)):
        return np.nan
    if not frequency_vector.size:
        return np.nan
    if not slope_params.size:
        return np.nan
    if not oscillation_params.size:
        return np.nan
    if frequency_vector.ndim != 1:
        raise ValueError("frequency_vector must be 1d")
    if slope_params.ndim != 1:
        raise ValueError("frequency_vector must be 1d")
    
    gaussian_shape = np.shape(oscillation_params)[0]
    gaussian_vector = np.zeros(np.size(frequency_vector))
    for i in range(gaussian_shape):
        gaussian_vector = gaussian_vector + make_gaussian(frequency_vector, oscillation_params[i])
    
    noise_vector = np.random.normal(noise[0], noise[1], np.size(frequency_vector))
    background_vector = (noise_vector + 
        slope_params[0] + (frequency_vector * slope_params[1]) + ((frequency_vector**2) * slope_params[2]))

    simulated_spectrum = gaussian_vector + background_vector
        
    return simulated_spectrum

