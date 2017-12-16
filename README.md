# FOOOF - fitting oscillations & one over f

[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](http://www.repostatus.org/badges/latest/active.svg)](http://www.repostatus.org/#active)
[![Build Status](https://travis-ci.org/voytekresearch/fooof.svg)](https://travis-ci.org/voytekresearch/fooof)
[![codecov](https://codecov.io/gh/voytekresearch/fooof/branch/master/graph/badge.svg)](https://codecov.io/gh/voytekresearch/fooof)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

FOOOF is a fast, efficient, physiologically-informed model to parameterize neural power spectra, characterizing both oscillations and the background 1/f.

The model conceives of the neural power spectral density (PSD) as consisting of two distinct functional processes:
- A 1/f background modeled as a line in log-log space with;
- Band-limited oscillatory "bumps" rising above this background, modeled as Gaussians in log(power) space.

With regards to oscillations, the benefit of the FOOOF approach is to characterize oscillations in terms of their center frequency, amplitude and bandwidth without requiring predefining specific bands of interest. In particular, it separates oscillations from a dynamic, and independently interesting 1/f background. This conception of the 1/f as potentially functional (and therefore worth carefully modeling) is based on work from our lab suggesting that the 1/f slope may index excitation/inhibition balance ([Gao, Peterson, Voytek, _NeuroImage_ 2017](http://voyteklab.com/wp-content/uploads/Gao-NeuroImage2017.pdf); [Voytek & Knight, _Biol Psychiatry_ 2015](http://voyteklab.com/wp-content/uploads/Voytek-BiolPsychiatry2015.pdf)). At the very least, however, the 1/f appears to change with task ([Podvalny _et al._, _J Neurophysiol_ 2015](http://www.weizmann.ac.il/neurobiology/labs/malach/sites/neurobiology.labs.malach/files/Podvalny%20et%20al_2015_JNeurophysiol.pdf)), with aging ([Voytek _et al._, _J Neurosci_ 2015](http://voyteklab.com/wp-content/uploads/Voytek-JNeurosci2015.pdf)).

## Python Version

FOOOF runs on Python 3.5 and 3.6.

## Dependencies

- numpy
- matplotlib
- scipy >= 0.19

## Install

To install the latest stable release of fooof, you can use pip:

`$ pip install fooof`

## Development Branch

To get the lastest, development version, you can get the code using git:

`$ git clone https://github.com/voytekresearch/fooof`

To then install the development version (without making changes), move into the directory you cloned and run:

`$ pip install .`

Otherwise, if you want to install an editable, development version, move into the directory you cloned and install with:

`$ pip install -e .`

## Usage

FOOOF is object oriented. With a power spectrum loaded (with 'freqs' storing frequency values, and 'psd' storing power values, both as 1D arrays in linear space) FOOOF can be used as follows:

```python
from fooof import FOOOF

# Initialize FOOOF object
fm = FOOOF()

# Define frequency range to model PSD
freq_range = [3, 40]

# Model the PSD with FOOOF
fm.model(freqs, psd, freq_range)
```

FOOOF.model() fits the model, plots the original PSD with the associated model of the PSD, and prints out the parameters of the model fit for both background 1/f (offset, knee, exponent) and Gaussian parameters (center frequency, amplitude, and bandwidth) for any identified oscillations.

FOOOF also accepts parameters for fine-tuning the fit. For example:

```python
fm = FOOOF(bandwidth_limits=(1.0, 15.0), max_n_gauss=6, min_amp=0.1, amp_std_thresh=2.0)
```

* _bandwidth_limits_ sets the possible lower- and upper-bounds for the fitted oscillation bandwidths.
* _max_n_gauss_ sets the maximum number of gaussians to find (in decreasing order of amplitude).
* _min_amp_ sets an absolute limit on the minimum amplitude (above background 1/f) for any oscillation.
* _amp_std_thresh_, similar to _min_amp_, sets a threshold above which oscillation amplitude must cross to be included in the model. However this parameter is in terms of standard deviation above the noise of the flattened spectrum.

FOOOF also has convenience methods for running the FOOOF model across matrices of PSDs, as well as functionality for saving and loading results, creating reports from FOOOF outputs, and utilities to further analize FOOOF results.

An example workflow, with 'freqs' as 1D array of frequency values, and 'psds' as a 2D array of power spectra.

```python

# Initialize a FOOOFGroup object, specifying some parameters
fg = FOOOFGroup(bandwidth_limits=(1.0, 8.0), max_n_gauss=8)

# Fit FOOOF model across the matrix of PSDs
fg.fit(freqs, psds)

# Create a report summarizing the results across the group of PSDs
fg.create_report()

# Save out FOOOF results for further analysis later
fg.save('fooof_group_results')
```

## Output
Example output for a FOOOF fit of MEG data:
!["fooof_report"](img/FOOOF_report.pdf)

Example output for running FOOOF across a group of PSDs (with FOOOFGroup):
!["fooof_group_report"](img/FOOOF_group_report.pdf)
