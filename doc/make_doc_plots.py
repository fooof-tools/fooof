"""Create the images for the FOOOF documentation."""

import shutil

import numpy as np
import matplotlib.pyplot as plt

from fooof import FOOOF, FOOOFGroup
from fooof.sim.gen import gen_power_spectrum
from fooof.plts.utils import check_ax
from fooof.plts.spectra import plot_spectrum
from fooof.utils.download import load_fooof_data

###################################################################################################
###################################################################################################

def main():

    ## Individual Model Plot

    # Download examples data files needed for this example
    freqs = load_fooof_data('freqs.npy', folder='data')
    spectrum = load_fooof_data('spectrum.npy', folder='data')

    # Initialize and fit an example power spectrum model
    fm = FOOOF(peak_width_limits=[1, 6], max_n_peaks=6, min_peak_height=0.2, verbose=False)
    fm.fit(freqs, spectrum, [3, 40])

    # Save out the report
    fm.save_report('FOOOF_report.png', 'img')

    ## Group Plot

    # Download examples data files needed for this example
    freqs = load_fooof_data('group_freqs.npy', folder='data')
    spectra = load_fooof_data('group_powers.npy', folder='data')

    # Initialize and fit a group of example power spectrum models
    fg = FOOOFGroup(peak_width_limits=[1, 6], max_n_peaks=6, min_peak_height=0.2, verbose=False)
    fg.fit(freqs, spectra, [3, 30])

    # Save out the report
    fg.save_report('FOOOFGroup_report.png', 'img')

    ## Make the icon plot

    # Simulate an example power spectrum
    fs, ps = gen_power_spectrum([4, 35], [0, 1], [[10, 0.3, 1],[22, 0.15, 1.25]], nlv=0.01)

    def custom_style(ax, log_freqs, log_powers):
        """Custom styler-function for the icon plot."""

        # Set the top and right side frame & ticks off
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)

        # Set linewidth of remaining spines
        ax.spines['left'].set_linewidth(10)
        ax.spines['bottom'].set_linewidth(10)
        ax.set_xticks([], [])
        ax.set_yticks([], [])

    # Create and save out the plot
    plot_spectrum(fs, ps, log_freqs=False, log_powers=True, lw=12, alpha=0.8,
                  color='grey', plot_style=custom_style, ax=check_ax(None, [6, 6]))
    plt.tight_layout()
    plt.savefig('img/spectrum.png')

    ## Clean Up

    # Remove the data folder
    shutil.rmtree('data')

if __name__ == "__main__":
    main()
