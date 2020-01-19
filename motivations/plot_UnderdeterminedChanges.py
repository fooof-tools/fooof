"""
Underdetermined Measures
========================

Figure 1 from the FOOOF paper, in quantitatively exact code.
"""

###################################################################################################
#
# In this example, we will WORDS, WORDS, WORDS.
#

###################################################################################################

import numpy as np
import matplotlib.pyplot as plt

from fooof.sim import gen_power_spectrum

from fooof.utils import trim_spectrum
from fooof.plts.spectra import plot_spectra_shading

###################################################################################################

# Simulation Settings
nlv = 0
f_res = 0.1
f_range = [3, 30]

###################################################################################################

# Create baseline power spectrum, to compare to
fs, ps_base = gen_power_spectrum(f_range, [0, 1.5], [[10, 0.5, 1], [22, 0.2, 2]], nlv, f_res)

###################################################################################################

# Create comparison power spectra
_, ps_alp = gen_power_spectrum(f_range, [0, 1.5], [[10, 0.311, 1], [22, 0.2, 2]], nlv, f_res)
_, ps_alf = gen_power_spectrum(f_range, [0, 1.5], [[11.75, 0.5, 1], [22, 0.2, 2]], nlv, f_res)
_, ps_off = gen_power_spectrum(f_range, [-0.126, 1.5], [[10, 0.5, 1], [22, 0.2, 2]], nlv, f_res)
_, ps_exp = gen_power_spectrum(f_range, [-0.87, 0.75], [[10, 0.5, 1], [22, 0.2, 2]], nlv, f_res)

###################################################################################################

# Collect the comparison power spectra together
ps_comps = {
    'Alpha Power Change' : ps_alp,
    'Alpha Frequency Change' : ps_alf,
    'Offset Change' : ps_off,
    'Exponent Change' : ps_exp
}

###################################################################################################

def plot_style(ax):
    """Helper function to style the plot."""

    ax.xaxis.label.set_visible(False)
    ax.yaxis.label.set_visible(False)

###################################################################################################

# Create COMMENT
fig, ax = plt.subplots(2, 2, figsize=(16, 12))
for cur_ax, (title, cur_dat) in zip(ax.reshape(-1), ps_comps.items()):

    # Create COMMENT
    plot_spectra_shading(fs, [ps_base, cur_dat], [8, 12],
        log_freqs=True, log_powers=True, ax=cur_ax)

    # Add the title, and do some plot styling
    cur_ax.set_title(title, {'fontsize' : 20})
    plot_style(cur_ax)

###################################################################################################

def calc_avg_power(freqs, powers, freq_range):
    """Helper function to calculate average power in a band."""

    fs, ps = trim_spectrum(freqs, powers, freq_range)
    avg_power = np.mean(ps)

    return avg_power

###################################################################################################

# Calculate the amount of alpha power in the baseline power spectrum
base_alpha = calc_avg_power(fs, ps_base, [8, 12])

###################################################################################################

# COMMENT
for title, ps in ps_comps.items():
    print('{:20s}\t {:1.4f}'.format(title, calc_avg_power(fs, ps, [8, 12]) - base_alpha))

###################################################################################################
#
# Words, words, words.
#
