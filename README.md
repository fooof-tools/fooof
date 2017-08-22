# FOOOF - fitting oscillations & one over f

FOOOF is a model to parameterize neural power spectra. 

It conceives of the neural power spectral density (PSD) as consisting of two distinct processes - a 1/f distributed background process, with potentially multiple sections of band-limited power - oscillatory regions in which the power is greater than the background process.

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

FOOOF.model() fits the model, plots the original PSD with the associated model of the PSD, and prints out the parameters of the model fit, for both background (1/f component), and parameters for each modelled oscillatory region.
