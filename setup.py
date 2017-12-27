"""FOOOF setup script."""

import os
from setuptools import setup, find_packages

# Get the current version number from inside the module
with open(os.path.join('fooof', 'version.py')) as vf:
    exec(vf.read())

# Copy in long description.
#  Note: this is a partial copy from the README
#    Only update here in coordination with the README, to keep things consistent.
long_description = \
"""
========================================
FOOOF: Fitting Oscillations & One-Over F
========================================

FOOOF is a fast, efficient, physiologically-informed model to parameterize
neural power spectra, characterizing both the 1/f background, and overlying
peaks (putative oscillations).

The model conceives of the neural power spectrum as consisting of two distinct functional processes:
- A 1/f background, modeled with an exponential fit, with:
- Band-limited peaks rising above this background (modeled as Gaussians).

With regards to examing peaks in the frequency domain, as putative oscillations, the benefit
of the FOOOF approach is that these peaks are characterized in terms of their specific center
frequency, amplitude and bandwidth without requiring predefining specific bands of interest.
In particular, it separates these peaks from a dynamic, and independently interesting 1/f
background. This conception of the 1/f as potentially functional (and therefore worth carefully
modeling) is based on work from the Voytek lab and others that collectively shows that 1/f changes
across task demands and participant demographics, and that it may index underlying
excitation/inhibition (EI) balance.
"""

setup(
    name = 'fooof',
    version = __version__,
    description = 'Fitting oscillations & one-over f',
    long_description = long_description,
    author = 'The Voytek Lab',
    author_email = 'voyteklab@gmail.com',
    url = 'https://github.com/voytekresearch/fooof',
    packages = find_packages(),
    license = 'Apache License, 2.0',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    download_url = 'https://github.com/voytekresearch/fooof/releases',
    keywords = ['neuroscience', 'neural oscillations', 'power spectra', '1/f', 'electrophysiology'],
    install_requires = ['numpy', 'scipy>=0.19.0'],
    tests_require = ['pytest'],
    extras_require = {
        'plot'    : ['matplotlib'],
        'tests'   : ['pytest'],
        'all'     : ['matplotlib', 'pytest']
    }
)