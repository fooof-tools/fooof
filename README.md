# FOOOF - fitting oscillations & one over f

FOOOF is a fast, efficient, physiologically-informed model to parameterize neural power spectra.

The model conceives of the neural power spectral density (PSD) as consisting of two distinct functional processes: 1) A 1/f background modeled as a curve with; 2) Band-limited oscillatory "bumps" rising above this background, modeled as Gaussians.

Note that this conception of the 1/f as potentially functional (and therefore worth carefully modeling) is based on work from our lab suggesting that the 1/f slope may index excitation/inhibition balance ([Gao, Peterson, Voytek, _NeuroImage_ 2017](http://voyteklab.com/wp-content/uploads/Gao-NeuroImage2017.pdf); [Voytek & Knight, _Biol Psychiatry_ 2015](http://voyteklab.com/wp-content/uploads/Voytek-BiolPsychiatry2015.pdf)). At the very least, however, the 1/f appears to change with task ([Podvalny _et al._, _J Neurophysiol_ 2015](http://www.weizmann.ac.il/neurobiology/labs/malach/sites/neurobiology.labs.malach/files/Podvalny%20et%20al_2015_JNeurophysiol.pdf)), with aging ([Voytek _et al._, _J Neurosci_ 2015](http://voyteklab.com/wp-content/uploads/Voytek-JNeurosci2015.pdf])).

## Dependencies

- numpy
- matplotlib
- scipy >= 0.19

## Usage

FOOOF is object oriented. With a PSD loaded (with 'freqs' storing frequency values, and 'psd' storing power values, both as 1D arrays) FOOOF can be used as follows:

```python
from fooof import FOOOF

# Initialize FOOOF object
foof_model = FOOOF()

# Define frequency range to model PSD
freq_range = [3, 40]

# Model the PSD with FOOOF
foof_model.model(freqs, psd, freq_range)
```

FOOOF.model() fits the model, plots the original PSD with the associated model of the PSD, and prints out the parameters of the model fit for both background 1/f (offset, slope, curve) and Gaussian parameters (center frequency, amplitude, and bandwidth) for any identified oscillations.
