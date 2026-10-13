"""
Damped & Modulated Oscillations
===============================

Words, words, words.

"""

# Import spectral model object & plot function
from specparam import SpectralModel
from specparam.plts import plot_spectra

# Import time domain simulation function for damped oscillations
from neurodsp.sim.periodic import sim_damped_oscillation

# Import time domain simulation function for modulated signals
from neurodsp.sim.combined import sim_modulated_signal

# Import neurodsp functionality of computer power spectra & plotting
from neurodsp.utils import create_times
from neurodsp.spectral import compute_spectrum_welch
from neurodsp.plts.spectral import plot_power_spectra
from neurodsp.plts.time_series import plot_time_series, plot_multi_time_series

###################################################################################################

# General simulation parameters
n_seconds = 10
fs = 250
freq = 25
exp = -1.5

# Damping settings
damp_coef = 1

# Define fitting frequency range
freq_range = [2, 75]

###################################################################################################
# Damped Oscillations
# -------------------
#
# Words, words, words
#

###################################################################################################

# Create a times vector for the time series
times = create_times(n_seconds, fs)

###################################################################################################

# Simulate a damped oscillation
d_osc = sim_damped_oscillation(n_seconds, fs, freq, damp_coef)

###################################################################################################

# ..
plot_time_series(times, d_osc, xlim=[0, 3])

###################################################################################################

# ...
freqs, powers_dosc = compute_spectrum_welch(d_osc, fs)

###################################################################################################

# ...
fm = SpectralModel(aperiodic_mode='fixed', verbose=False)

###################################################################################################

# ...
fm.add_data(freqs_dosc, powers_dosc, freq_range)
fm.plot()

###################################################################################################

# ...
fm.report()

###################################################################################################
# XXXX
# ----
#
#

###################################################################################################

# ...
damp_coefs = [0.1, 1, 10]

###################################################################################################

damped_sigs = []
damped_powers = []
for d_coef in damp_coefs:

    # ...
    csig = sim_damped_oscillation(n_seconds, fs, freq, d_coef)
    cfreqs, cpowers = compute_spectrum_welch(csig, fs)

    # ...
    damped_sigs.append(csig)
    damped_powers.append(cpowers)

###################################################################################################

# ...
plot_multi_time_series(times, damped_sigs, xlim=[0, 3])

###################################################################################################

plot_spectra(freqs, damped_powers, log_powers=True)

###################################################################################################

for damping, cpowers in zip(damp_coefs, damped_powers):
    fm.fit(freqs, cpowers, freq_range)
    print('Damping co-efficient: {:4.1f} - aperiodic exponent: {:1.2f}'.format(\
        damping, fm.results.get_params('aperiodic', 'exponent')))

###################################################################################################
#
# Words, words, words.
#

###################################################################################################
# Modulated Oscillators
# ---------------------
#
#

###################################################################################################

# Simulate another modulated signal
m_osc = sim_modulated_signal(n_seconds, fs,
                            'sim_oscillation', {'freq' : freq},
                            'sim_powerlaw', {'exponent' : exp})

###################################################################################################

# ...
plot_time_series(times, msig)

###################################################################################################

# ...
freqs, powers_mosc = compute_spectrum_welch(m_osc, fs)

###################################################################################################

# ...
fm.add_data(freqs_dosc, powers_mosc, freq_range)
fm.plot()

###################################################################################################

# ...
fm.report()

###################################################################################################
#
# Words, words, words.
#

###################################################################################################

# Simulate a modulated signal, passing in instruction for the main and modulating signal
m_osc2 = sim_modulated_signal(n_seconds, fs,
                              'sim_oscillation', {'freq' : 1},
                              'sim_oscillation', {'freq' : 10})

###################################################################################################

# ...
plot_time_series(times, m_osc2)

###################################################################################################

# ...
fm.report(*compute_spectrum_welch(m_osc2, fs))

###################################################################################################
#
# Words, words, words.
#
